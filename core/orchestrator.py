"""
Turn Orchestrator - coordinates all components for each turn.
Main entry point for processing user messages.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List

from core.database.db_manager import DatabaseManager
from core.managers.memory_manager import MemoryManager
from core.managers.context_manager import ContextManager
from core.agents.gm_agent import GMAgent
from core.agents.quantizer_agent import QuantizerAgent
from core.agents.summarizer_agent import SummarizerAgent
from core.llm.openrouter_client import OpenRouterClient
from core.config import settings
from core.utils import load_initial_summary, load_initial_quants

logger = logging.getLogger(__name__)


class TurnOrchestrator:
    """
    Orchestrates the complete turn cycle.
    
    Flow:
    1. User message arrives
    2. Get active quants from previous turn
    3. Build context (summary + raw turns + quants)
    4. GM generates response and predicts next quants
    5. Save turn to database
    6. If needed (async): trigger Quantizer and Summarizer
    7. Return response to user
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        llm_client: OpenRouterClient
    ):
        """Initialize orchestrator with all components."""
        self.db = db_manager
        self.llm = llm_client
        
        # Managers
        self.memory_manager = MemoryManager(db_manager)
        self.context_manager = ContextManager(db_manager, self.memory_manager)
        
        # Agents (each with their own model configuration)
        self.gm_agent = GMAgent(llm_client, model=settings.gm_model)
        self.quantizer_agent = QuantizerAgent(llm_client, model=settings.quantizer_model)
        self.summarizer_agent = SummarizerAgent(llm_client, model=settings.summarizer_model)
    
    async def process_turn(
        self,
        session_id: int,
        user_message: str,
        system_prompt_parts: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process one turn of conversation.
        
        Args:
            session_id: Session ID
            user_message: User's message
            system_prompt_parts: Optional custom system prompt components
        
        Returns:
            Dict with:
            - reply: Agent's response text
            - turn_number: Current turn number
            - quants_used: Quants that were in context
            - quants_requested: Quants requested for next turn
        """
        logger.info(f"Processing turn for session {session_id}")
        
        # Get session
        db_session = self.db.get_session_by_id(session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found")
        
        # Increment turn number
        current_turn = db_session.current_turn + 1
        logger.info(f"Turn number: {current_turn}")
        
        # Step 1: Get active quants (from previous turn's request)
        active_quants = await self._get_active_quants(session_id)
        logger.info(f"Active quants: {[q.id for q in active_quants]}")
        
        # Step 2: Build context
        context_messages = self.context_manager.build_context(
            session_id=session_id,
            current_turn=current_turn,
            active_quants=active_quants,
            system_prompt_parts=system_prompt_parts
        )
        logger.debug(f"Context built with {len(context_messages)} messages")
        
        # Step 3: GM generates response
        gm_response = await self.gm_agent.generate_response(
            context_messages=context_messages,
            user_message=user_message,
            max_tokens=settings.gm_max_tokens
        )
        
        reply = gm_response["reply"]
        requested_quants = gm_response["quants"]
        
        logger.info(f"GM response generated. Requested quants: {requested_quants}")
        
        # Step 4: Save turn to database
        self.db.create_turn(
            session_id=session_id,
            turn_number=current_turn,
            user_message=user_message,
            agent_reply=reply,
            requested_quants=requested_quants
        )
        
        # Update session turn counter
        self.db.update_session_turn(session_id, current_turn)
        
        # Step 5: Check if background processing is needed
        # Trigger when raw turns reach max (7), not by turn number
        recent_turns_count = len(self.db.get_recent_turns(session_id, limit=settings.raw_turns_max + 1))
        should_process_memory = (recent_turns_count >= settings.raw_turns_max)
        
        if should_process_memory:
            logger.info(f"Triggering background memory processing ({recent_turns_count} raw turns)")
            # Run in background (non-blocking) - user gets response immediately
            asyncio.create_task(
                self._background_memory_processing(
                    session_id=session_id,
                    current_turn=current_turn,
                    active_quants=active_quants
                )
            )
        
        # Return response
        return {
            "reply": reply,
            "turn_number": current_turn,
            "quants_used": [q.id for q in active_quants],
            "quants_requested": requested_quants
        }
    
    async def _get_active_quants(self, session_id: int) -> List[Any]:
        """Get quants that should be active for this turn."""
        # Check if this is truly the first turn by checking session state
        db_session = self.db.get_session_by_id(session_id)
        
        if db_session.current_turn == 0:
            # First turn - load initial quants
            logger.info("First turn (current_turn=0) - loading initial quants")
            await self._load_initial_data(session_id)
            
            # Get all quants for the session (initial quants just loaded)
            all_quants = self.memory_manager.get_all_quants(session_id)
            logger.info(f"Loaded {len(all_quants)} initial quants")
            return all_quants
        
        # Get latest turn to see what quants were requested
        recent_turns = self.db.get_recent_turns(session_id, limit=1)
        
        if not recent_turns or not recent_turns[0].requested_quants:
            # No quants requested on previous turn - return empty list
            # (GM will work with summary and recent turns only)
            logger.info("No quants requested on previous turn")
            return []
        
        # Get requested quants
        requested_names = recent_turns[0].requested_quants
        logger.info(f"Retrieving {len(requested_names)} requested quants")
        
        # Retrieve from memory with fuzzy matching
        quants = self.memory_manager.get_quants_by_names(
            session_id=session_id,
            quant_names=requested_names,
            fuzzy=True
        )
        
        return quants
    
    async def _background_memory_processing(
        self,
        session_id: int,
        current_turn: int,
        active_quants: List[Any]
    ):
        """
        Background processing: Quantizer and Summarizer.
        Runs asynchronously while user reads response.
        After completion, trims raw turns window to keep only recent ones.
        """
        try:
            logger.info("Starting background memory processing")
            
            # Run Quantizer and Summarizer in parallel
            await asyncio.gather(
                self._run_quantizer(session_id, current_turn, active_quants),
                self._run_summarizer(session_id),
                return_exceptions=True
            )
            
            # After summarization, trim old turns (keep last 4)
            deleted_count = self.db.trim_old_turns(
                session_id=session_id,
                keep_last_n=settings.raw_turns_min
            )
            
            if deleted_count > 0:
                logger.info(f"Trimmed {deleted_count} old turns, keeping last {settings.raw_turns_min}")
            
            logger.info("Background memory processing completed")
        
        except Exception as e:
            logger.error(f"Error in background processing: {e}", exc_info=True)
    
    async def _run_quantizer(
        self,
        session_id: int,
        current_turn: int,
        active_quants: List[Any]
    ):
        """Run Quantizer agent."""
        try:
            logger.info("Running Quantizer agent")
            
            # Get context for quantizer
            summary_text = self.context_manager._get_summary(session_id)
            recent_turns_db = self.db.get_recent_turns(session_id, limit=20)
            recent_turns = [
                {
                    "user_message": t.user_message,
                    "agent_reply": t.agent_reply
                }
                for t in reversed(recent_turns_db)
            ]
            
            # Run quantizer
            commands = await self.quantizer_agent.process_memory_updates(
                summary_text=summary_text,
                recent_turns=recent_turns,
                active_quants=active_quants,
                current_turn=current_turn
            )
            
            if commands:
                logger.info(f"Quantizer generated {len(commands)} commands")
                
                # Process commands
                results = self.memory_manager.process_commands(
                    session_id=session_id,
                    commands=commands,
                    current_turn=current_turn
                )
                
                logger.info(
                    f"Memory updates: "
                    f"{len(results['created'])} created, "
                    f"{len(results['updated'])} updated, "
                    f"{len(results['deleted'])} deleted, "
                    f"{len(results['errors'])} errors"
                )
                
                if results['errors']:
                    for error in results['errors']:
                        logger.warning(f"Command error: {error}")
            else:
                logger.info("Quantizer: no updates needed")
        
        except Exception as e:
            logger.error(f"Error running Quantizer: {e}", exc_info=True)
    
    async def _load_initial_data(self, session_id: int):
        """Load initial summary and quants for a new session."""
        try:
            logger.info(f"Loading initial data for session {session_id}")
            
            # Load initial summary
            initial_summary = load_initial_summary()
            logger.info(f"Loaded initial summary ({len(initial_summary)} chars)")
            
            # Save summary to database
            self.db.create_summary(
                session_id=session_id,
                summary_text=initial_summary,
                turns_start=0,
                turns_end=0,
                is_full_rewrite=False
            )
            
            # Load initial quants
            initial_quants_data = load_initial_quants()
            logger.info(f"Loading {len(initial_quants_data)} initial quants")
            
            # Create quants in database
            commands = {}
            for quant_data in initial_quants_data:
                quant_id = quant_data.pop("id")
                commands[f"create_{quant_id}"] = quant_data
            
            # Process commands
            self.memory_manager.process_commands(
                session_id=session_id,
                commands=commands,
                current_turn=0
            )
            
            logger.info("Initial data loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading initial data: {e}", exc_info=True)
            raise
    
    async def _run_summarizer(self, session_id: int):
        """Run Summarizer agent."""
        try:
            logger.info("Running Summarizer agent")
            
            # Check if summarization is needed
            if not self.context_manager.should_trigger_summarization(session_id):
                logger.info("Summarizer: not needed yet")
                return
            
            # Get existing summary
            existing_summary = self.context_manager._get_summary(session_id)
            
            # Determine mode
            if self.summarizer_agent.should_use_rewrite_mode(existing_summary):
                mode = "rewrite"
                logger.info("Summarizer: using REWRITE mode")
                
                # Get all recent turns for rewrite
                recent_turns_db = self.db.get_recent_turns(session_id, limit=20)
                turns_data = [
                    {
                        "user_message": t.user_message,
                        "agent_reply": t.agent_reply
                    }
                    for t in reversed(recent_turns_db)
                ]
                
                # Create new summary
                new_summary = await self.summarizer_agent.summarize(
                    existing_summary=existing_summary,
                    turns_to_summarize=turns_data,
                    mode="rewrite"
                )
                
                # Save as full rewrite
                if turns_data:
                    self.db.create_summary(
                        session_id=session_id,
                        summary_text=new_summary,
                        turns_start=recent_turns_db[-1].turn_number if recent_turns_db else 1,
                        turns_end=recent_turns_db[0].turn_number if recent_turns_db else 1,
                        is_full_rewrite=True
                    )
            
            else:
                mode = "append"
                logger.info("Summarizer: using APPEND mode")
                
                # Get turns to summarize
                turns_to_summarize, new_start = self.context_manager.get_turns_for_summarization(session_id)
                
                if not turns_to_summarize:
                    logger.info("Summarizer: no turns to summarize")
                    return
                
                turns_data = [
                    {
                        "user_message": t.user_message,
                        "agent_reply": t.agent_reply
                    }
                    for t in reversed(turns_to_summarize)
                ]
                
                # Get last summary for context
                last_summary = self.db.get_latest_summary(session_id)
                last_summary_text = last_summary.summary_text if last_summary else ""
                
                # Create summary addition
                summary_addition = await self.summarizer_agent.summarize(
                    existing_summary=last_summary_text,
                    turns_to_summarize=turns_data,
                    mode="append"
                )
                
                # Save summary
                if turns_data:
                    self.db.create_summary(
                        session_id=session_id,
                        summary_text=summary_addition,
                        turns_start=turns_to_summarize[-1].turn_number if turns_to_summarize else 1,
                        turns_end=turns_to_summarize[0].turn_number if turns_to_summarize else 1,
                        is_full_rewrite=False
                    )
            
            logger.info(f"Summarizer completed in {mode} mode")
        
        except Exception as e:
            logger.error(f"Error running Summarizer: {e}", exc_info=True)

