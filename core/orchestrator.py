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
from core.agents.translator_agent import TranslatorAgent
from core.llm.openrouter_client import OpenRouterClient
from core.mechanics.mechanics_manager import MechanicsManager
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
        self.mechanics_manager = MechanicsManager(db_manager)
        self.context_manager = ContextManager(db_manager, self.memory_manager)
        
        # Agents (each with their own model configuration)
        self.gm_agent = GMAgent(llm_client, model=settings.gm_model)
        self.quantizer_agent = QuantizerAgent(llm_client, self.memory_manager, model=settings.quantizer_model)
        self.summarizer_agent = SummarizerAgent(llm_client, model=settings.summarizer_model)
        self.translator_agent = TranslatorAgent(llm_client)
    
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

        # Get user settings for prompts and mechanics
        user_settings = self.db.get_user_settings(db_session.user_id)
        logger.info(f"User settings: difficulty={user_settings['difficulty']}, filter={user_settings['content_filter']}")

        # Increment turn number
        current_turn = db_session.current_turn + 1
        logger.info(f"Turn number: {current_turn}")
        
        # Step 1: Get active quants (from previous turn's request)
        active_quants = await self._get_active_quants(session_id)
        logger.info(f"Active quants: {[q.id for q in active_quants]}")
        
        # Step 1.5: Game mechanics (cards, checks, combat)
        module_data = None
        character_exists = self.mechanics_manager.character_exists(session_id)
        logger.info(f"Character exists: {character_exists}")
        
        if not character_exists:
            # First turn - character creation
            logger.info("Character doesn't exist, generating creation cards")
            module_data = {
                "character_creation": self.mechanics_manager.generate_character_cards()
            }
            logger.debug(f"Character creation data keys: {module_data.keys()}")
        else:
            # Normal turn - draw cards and calculate
            logger.info("Drawing cards and calculating mechanics")
            cards_data = self.mechanics_manager.draw_cards_for_turn()
            logger.debug(f"Cards drawn: {cards_data['pairs']}")

            difficulty = user_settings.get("difficulty", "normal")
            thresholds = self.mechanics_manager.calculate_thresholds(session_id, difficulty)
            logger.debug(f"Thresholds calculated: {list(thresholds.keys())} (difficulty={difficulty})")

            checks = self.mechanics_manager.calculate_all_checks(session_id, cards_data, difficulty)
            logger.debug(f"Checks calculated: {len(checks)} checks")

            combat = self.mechanics_manager.calculate_all_combat_options(session_id, cards_data)
            logger.debug(f"Combat options calculated: {len(combat)} options")

            character_state = self.mechanics_manager.get_character_state(session_id)
            logger.debug(f"Character state: HP={character_state.get('hp')}/{character_state.get('max_hp')}, Mana={character_state.get('mana')}/{character_state.get('max_mana')}")

            module_data = {
                "cards": cards_data,
                "thresholds": thresholds,
                "checks": checks,
                "combat": combat,
                "character": character_state
            }
            logger.info(f"Module data prepared with keys: {list(module_data.keys())}")

        # Step 2: Build context (with world-specific prompts and user settings)
        context_messages = self.context_manager.build_context(
            session_id=session_id,
            current_turn=current_turn,
            active_quants=active_quants,
            system_prompt_parts=system_prompt_parts,
            module_data=module_data,
            world_id=db_session.world_id,
            user_settings=user_settings
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
        response_data = gm_response.get("response_data", {})
        
        logger.info(f"GM response generated. Requested quants: {requested_quants}")
        
        # Step 3.5: Apply game mechanics changes
        if response_data:
            # Check if character was just created
            if response_data.get("character_created") and "create_character" in response_data:
                logger.info("Creating character from GM response")
                char_stats = response_data["create_character"]
                self.mechanics_manager.create_character(session_id, char_stats)
                logger.info(f"Character created: {char_stats}")
            elif character_exists:
                # Apply changes to existing character
                logger.info(f"Applying mechanics changes: {response_data}")
                self.mechanics_manager.apply_gm_changes(session_id, response_data)
        
        # Step 4: Save turn to database
        # Extract cost from GM response (if available)
        gm_cost = 0.0
        if isinstance(gm_response, dict) and 'usage' in gm_response:
            gm_cost = gm_response['usage'].get('cost', 0.0)
            logger.info(f"GM cost: ${gm_cost:.6f}")
        
        self.db.create_turn(
            session_id=session_id,
            turn_number=current_turn,
            user_message=user_message,
            agent_reply=reply,
            requested_quants=requested_quants,
            cost_gm=gm_cost
        )
        
        # Update session turn counter
        self.db.update_session_turn(session_id, current_turn)
        
        # Step 4.5: Trigger TranslatorAgent (background, non-blocking)
        logger.info("Triggering translator agent (background)")
        asyncio.create_task(
            self._translate_turn(
                session_id=session_id,
                turn_number=current_turn,
                user_message=user_message,
                agent_reply=reply
            )
        )
        
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
            # No quants requested on previous turn
            # Return character + recent quants as fallback (minimum context)
            logger.warning("No quants requested on previous turn - using fallback (character + recent)")
            
            # Get character quant (always important)
            all_quants = self.memory_manager.get_all_quants(session_id)
            fallback_quants = [q for q in all_quants if q.type == "npc" and "пол" in q.id.lower()]
            
            # Add most recently updated quants (up to 10 total)
            recent_quants = sorted(all_quants, key=lambda q: q.updated_at, reverse=True)[:10]
            for q in recent_quants:
                if q not in fallback_quants:
                    fallback_quants.append(q)
            
            logger.info(f"Fallback: returning {len(fallback_quants)} quants: {[q.id for q in fallback_quants]}")
            return fallback_quants
        
        # Get requested quants
        requested_names = recent_turns[0].requested_quants
        logger.info(f"Retrieving {len(requested_names)} requested quants: {requested_names}")
        
        # Retrieve from memory with fuzzy matching
        quants = self.memory_manager.get_quants_by_names(
            session_id=session_id,
            quant_names=requested_names,
            fuzzy=True
        )
        
        # Fallback: if NO quants found (e.g. GM requested non-existent quants)
        if not quants:
            logger.warning(f"NO quants found for requested names! Providing fallback context.")
            all_quants = self.memory_manager.get_all_quants(session_id)
            
            # Return most recently updated quants (up to 10)
            fallback_quants = sorted(all_quants, key=lambda q: q.updated_at or q.created_at or 0, reverse=True)[:10]
            logger.info(f"Fallback: returning {len(fallback_quants)} quants: {[q.id for q in fallback_quants]}")
            return fallback_quants
        
        logger.info(f"Found {len(quants)} quants: {[q.id for q in quants]}")
        return quants
    
    async def _translate_turn(
        self,
        session_id: int,
        turn_number: int,
        user_message: str,
        agent_reply: str
    ):
        """
        Translate turn to English JSON (background task).
        Runs asynchronously after turn is saved.
        """
        try:
            logger.info(f"Translator: processing turn {turn_number}")
            
            # Call translator (async)
            translated_json = await self.translator_agent.translate_turn(
                player_action=user_message,
                gm_response=agent_reply,
                turn_number=turn_number
            )
            
            if translated_json:
                # Save to database
                import json
                json_str = json.dumps(translated_json, ensure_ascii=False)
                self.db.update_turn_translation(session_id, turn_number, json_str)
                
                # Extract cost if available
                translator_cost = translated_json.get('cost', 0.0) if isinstance(translated_json, dict) else 0.0
                if translator_cost > 0:
                    self.db.update_turn_costs(
                        session_id=session_id,
                        turn_number=turn_number,
                        cost_translator=translator_cost
                    )
                    logger.info(f"Translator: turn {turn_number} translated, cost ${translator_cost:.6f}")
                else:
                    logger.info(f"Translator: turn {turn_number} translated and saved")
            else:
                logger.warning(f"Translator: failed to translate turn {turn_number}")
                
        except Exception as e:
            logger.error(f"Translator: error processing turn {turn_number}: {e}")
    
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
                keep_last_n=settings.raw_turns_keep
            )
            
            if deleted_count > 0:
                logger.info(f"Trimmed {deleted_count} old turns, keeping last {settings.raw_turns_keep}")
            
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
            
            # Get session to determine world_id
            session = self.db.get_session_by_id(session_id)
            world_id = session.world_id if session else None
            
            # Get context for quantizer
            summary_text = self.context_manager._get_summary(session_id)
            
            # Get synopsis list (for navigation)
            synopsis_list = self.memory_manager.get_recent_quants_synopsis(session_id, current_turn)
            logger.info(f"Quantizer: synopsis list has {len(synopsis_list)} chars")
            
            # Get recent turns (prefer translated JSON)
            import json
            recent_turns_db = self.db.get_recent_turns(session_id, limit=20)
            recent_turns = []
            for t in reversed(recent_turns_db):
                if t.translated_json:
                    try:
                        # Use translated English JSON
                        translated = json.loads(t.translated_json)
                        recent_turns.append({
                            "user_message": f"Turn {translated.get('turn', '?')}: {translated.get('player_action', '')}",
                            "agent_reply": translated.get('gm_narrative', '')
                        })
                    except (json.JSONDecodeError, KeyError):
                        # Fallback to raw Russian
                        recent_turns.append({
                            "user_message": t.user_message,
                            "agent_reply": t.agent_reply
                        })
                else:
                    # No translation - use raw Russian
                    recent_turns.append({
                        "user_message": t.user_message,
                        "agent_reply": t.agent_reply
                    })
            
            logger.info(f"Quantizer: {len(recent_turns)} turns in context")
            
            # Run quantizer with world_id for world-specific instructions
            commands = await self.quantizer_agent.process_memory_updates(
                session_id=session_id,
                summary_text=summary_text,
                recent_turns=recent_turns,
                active_quants=active_quants,
                synopsis_list=synopsis_list,
                current_turn=current_turn,
                world_id=world_id
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
                
                # Use translated JSON if available, otherwise raw turns
                turns_data = []
                for t in reversed(recent_turns_db):
                    if t.translated_json:
                        # Use compressed English JSON
                        turns_data.append({
                            "user_message": t.translated_json,
                            "agent_reply": ""  # Already included in JSON
                        })
                    else:
                        # Fallback to raw Russian turns
                        turns_data.append({
                            "user_message": t.user_message,
                            "agent_reply": t.agent_reply
                        })
                
                # Create new summary
                new_summary = await self.summarizer_agent.summarize(
                    existing_summary=existing_summary,
                    turns_to_summarize=turns_data,
                    mode="rewrite"
                )
                
                # Delete all old summaries before saving compressed one
                old_summaries = self.db.get_all_summaries(session_id)
                for old_summary in old_summaries:
                    from core.database.models import SummaryDB
                    with self.db.get_session() as db_session:
                        summary_obj = db_session.query(SummaryDB).filter_by(id=old_summary.id).first()
                        if summary_obj:
                            db_session.delete(summary_obj)
                            db_session.commit()
                    logger.info(f"Deleted old summary (turns {old_summary.turns_start}-{old_summary.turns_end}) before rewrite")
                
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
                
                # Use translated JSON if available, otherwise raw turns
                turns_data = []
                for t in reversed(turns_to_summarize):
                    if t.translated_json:
                        # Use compressed English JSON
                        turns_data.append({
                            "user_message": t.translated_json,
                            "agent_reply": ""  # Already included in JSON
                        })
                    else:
                        # Fallback to raw Russian turns
                        turns_data.append({
                            "user_message": t.user_message,
                            "agent_reply": t.agent_reply
                        })
                
                # Get last summary for context
                last_summary = self.db.get_latest_summary(session_id)
                last_summary_text = last_summary.summary_text if last_summary else ""
                
                # Create summary addition
                summary_addition = await self.summarizer_agent.summarize(
                    existing_summary=last_summary_text,
                    turns_to_summarize=turns_data,
                    mode="append"
                )
                
                # Delete old summaries before saving new one
                # Since append mode returns FULL cumulative summary,
                # we only need the latest one
                old_summaries = self.db.get_all_summaries(session_id)
                for old_summary in old_summaries:
                    from core.database.models import SummaryDB
                    with self.db.get_session() as db_session:
                        summary_obj = db_session.query(SummaryDB).filter_by(id=old_summary.id).first()
                        if summary_obj:
                            db_session.delete(summary_obj)
                            db_session.commit()
                    logger.info(f"Deleted old summary (turns {old_summary.turns_start}-{old_summary.turns_end})")
                
                # Save new summary
                if turns_data:
                    self.db.create_summary(
                        session_id=session_id,
                        summary_text=summary_addition,
                        turns_start=turns_to_summarize[-1].turn_number if turns_to_summarize else 1,
                        turns_end=turns_to_summarize[0].turn_number if turns_to_summarize else 1,
                        is_full_rewrite=False
                    )
            
            logger.info(f"Summarizer completed in {mode} mode")
            
            # Trim old raw turns after successful summarization
            # Keep only last N turns as per config
            deleted_count = self.db.trim_old_turns(
                session_id,
                keep_last_n=settings.raw_turns_keep
            )
            
            if deleted_count > 0:
                logger.info(f"Trimmed {deleted_count} summarized turns, keeping last {settings.raw_turns_keep} raw turns")
        
        except Exception as e:
            logger.error(f"Error running Summarizer: {e}", exc_info=True)

