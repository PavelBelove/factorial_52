"""
FastAPI application main file.
Provides REST API for PlexMem system.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database.db_manager import DatabaseManager
from core.llm.openrouter_client import OpenRouterClient
from core.orchestrator import TurnOrchestrator
from core.mechanics.mechanics_manager import MechanicsManager
from core.models import SessionType
from core.utils.logger import setup_logging
from core.api.models import (
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
    GetSessionInfoResponse,
    GetQuantsResponse,
    HealthResponse
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Global instances
db_manager: DatabaseManager = None
orchestrator: TurnOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for FastAPI app."""
    global db_manager, orchestrator, mechanics_manager
    
    logger.info("Starting PlexMem API...")
    
    # Initialize components
    db_manager = DatabaseManager()
    llm_client = OpenRouterClient()
    mechanics_manager = MechanicsManager(db_manager)
    orchestrator = TurnOrchestrator(db_manager, llm_client)
    
    logger.info("PlexMem API started successfully")
    
    yield
    
    logger.info("Shutting down PlexMem API...")


# Create FastAPI app
app = FastAPI(
    title="PlexMem API",
    description="Predictive-associative memory system for LLM agents",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= ENDPOINTS =============

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        database="connected"
    )


@app.get("/sessions/user/{platform_user_id}")
async def get_user_session(platform_user_id: str, platform_type: str = "telegram"):
    """
    Get active session for user by platform_id (e.g. Telegram user_id).
    Returns 404 if no active session found.
    """
    try:
        # Find user by platform_id
        with db_manager.get_session() as db_session:
            from core.database.models import UserDB, SessionDB
            
            # First, find user by platform_id
            user = db_session.query(UserDB).filter(
                UserDB.platform_id == platform_user_id,
                UserDB.platform_type == platform_type
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No user found with platform_id {platform_user_id}"
                )
            
            # Then find active session for this user
            session = db_session.query(SessionDB).filter(
                SessionDB.user_id == user.id,
                SessionDB.is_active == True
            ).first()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No active session found for user {platform_user_id}"
                )
            
            logger.info(f"Found active session {session.id} for platform user {platform_user_id}")
            
            return {
                "session_id": session.id,
                "user_id": user.id,
                "platform_id": platform_user_id,
                "current_turn": session.current_turn,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/sessions/deactivate")
async def deactivate_user_sessions(request: CreateSessionRequest):
    """
    Deactivate all active sessions for a user.
    Used when starting a new game with /start.
    """
    try:
        logger.info(f"Deactivating sessions for user {request.platform_id}")
        
        # Find user
        with db_manager.get_session() as db_session:
            from core.database.models import UserDB, SessionDB
            
            user = db_session.query(UserDB).filter(
                UserDB.platform_id == request.platform_id,
                UserDB.platform_type == request.platform_type
            ).first()
            
            if not user:
                return {"deactivated": 0, "message": "No user found"}
            
            # Deactivate all active sessions
            count = db_session.query(SessionDB).filter(
                SessionDB.user_id == user.id,
                SessionDB.is_active == True
            ).update({"is_active": False})
            
            db_session.commit()
            
            logger.info(f"Deactivated {count} sessions for user {user.id}")
            
            return {
                "deactivated": count,
                "user_id": user.id,
                "message": f"Deactivated {count} sessions"
            }
    
    except Exception as e:
        logger.error(f"Error deactivating sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create new session for user.
    If user doesn't exist, creates user first.
    """
    try:
        logger.info(f"Creating session for user {request.platform_id}")
        
        # Get or create user
        user = db_manager.get_or_create_user(
            platform_id=request.platform_id,
            platform_type=request.platform_type
        )
        
        # Get world_id from request or use default
        world_id = getattr(request, 'world_id', 'isekai')
        
        # Create session
        session = db_manager.create_session(
            user_id=user.id,
            session_type=SessionType(request.session_type),
            world_id=world_id
        )
        
        logger.info(f"Session {session.id} created for user {user.id} in world {world_id}")
        
        return CreateSessionResponse(
            session_id=session.id,
            user_id=user.id,
            session_type=session.session_type
        )
    
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(session_id: int, request: SendMessageRequest):
    """
    Send message to agent and get response.
    This is the main endpoint for conversation.
    """
    try:
        logger.info(f"Processing message for session {session_id}")
        
        # Validate session exists
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session {session_id} is not active"
            )
        
        # Process turn
        result = await orchestrator.process_turn(
            session_id=session_id,
            user_message=request.message,
            system_prompt_parts=request.system_prompt_parts
        )
        
        return SendMessageResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/sessions/{session_id}", response_model=GetSessionInfoResponse)
async def get_session_info(session_id: int):
    """Get session information."""
    try:
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Get quants count
        quants = db_manager.get_all_quants(session_id)
        
        # Get summary length
        summaries = db_manager.get_all_summaries(session_id)
        summary_length = sum(len(s.summary_text) for s in summaries)
        
        return GetSessionInfoResponse(
            session_id=session.id,
            user_id=session.user_id,
            session_type=session.session_type,
            current_turn=session.current_turn,
            is_active=session.is_active,
            quants_count=len(quants),
            summary_length=summary_length
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/sessions/{session_id}/quants", response_model=GetQuantsResponse)
async def get_quants(session_id: int):
    """Get all quants for session."""
    try:
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        quants = db_manager.get_all_quants(session_id)
        
        quants_data = [
            {
                "id": q.quant_id,
                "type": q.type,
                "body": q.body,
                "links": q.links,
                "created_at": q.created_at,
                "updated_at": q.updated_at,
                "is_game": q.is_game
            }
            for q in quants
        ]
        
        return GetQuantsResponse(
            quants=quants_data,
            total=len(quants_data)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quants: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/sessions/{session_id}/history")
async def get_history(session_id: int, limit: int = 10):
    """Get conversation history."""
    try:
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        turns = db_manager.get_recent_turns(session_id, limit=limit)
        
        history = [
            {
                "turn_number": t.turn_number,
                "user_message": t.user_message,
                "agent_reply": t.agent_reply,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None
            }
            for t in reversed(turns)
        ]
        
        return {"turns": history, "total": len(history)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/sessions/{session_id}/undo")
async def undo_last_turn(session_id: int):
    """
    Undo the last turn in the session.
    Deletes the last Turn from database and decrements current_turn.
    Used for /undo and /retry functionality.
    """
    try:
        # Validate session exists
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session {session_id} is not active"
            )
        
        # Delete last turn
        success = db_manager.delete_last_turn(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No turns to undo (session is at turn 0)"
            )
        
        # Get updated session info
        session = db_manager.get_session_by_id(session_id)
        
        logger.info(f"Undo successful for session {session_id}, now at turn {session.current_turn}")
        
        return {
            "success": True,
            "session_id": session_id,
            "current_turn": session.current_turn,
            "message": f"Turn undone. Session now at turn {session.current_turn}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error undoing turn: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/sessions/{session_id}/costs")
async def get_session_costs(session_id: int):
    """Get cost breakdown for a session."""
    try:
        logger.info(f"Getting costs for session {session_id}")
        
        # Get session to verify it exists
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Get cost breakdown
        costs = db_manager.get_session_costs(session_id)
        
        return {
            "session_id": session_id,
            "num_turns": costs["num_turns"],
            "costs": {
                "gm": costs["gm"],
                "quantizer": costs["quantizer"],
                "summarizer": costs["summarizer"],
                "translator": costs["translator"],
                "total": costs["total"]
            },
            "costs_formatted": {
                "gm": f"${costs['gm']:.6f}",
                "quantizer": f"${costs['quantizer']:.6f}",
                "summarizer": f"${costs['summarizer']:.6f}",
                "translator": f"${costs['translator']:.6f}",
                "total": f"${costs['total']:.6f}"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting costs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/sessions/{session_id}/character")
async def get_character(session_id: int):
    """Get character stats for session."""
    try:
        # Load character from mechanics manager
        character = mechanics_manager.get_character(session_id)
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        
        return {
            "hp": character.hp,
            "max_hp": character.max_hp,
            "mana": character.mana,
            "max_mana": character.max_mana,
            "gold": character.gold,
            "spades": character.spades,
            "hearts": character.hearts,
            "diamonds": character.diamonds,
            "clubs": character.clubs,
            "spades_xp": character.spades_xp,
            "hearts_xp": character.hearts_xp,
            "diamonds_xp": character.diamonds_xp,
            "clubs_xp": character.clubs_xp
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting character: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/sessions/{session_id}/inventory")
async def get_inventory(session_id: int):
    """Get inventory for session."""
    try:
        # Load character from mechanics manager
        character = mechanics_manager.get_character(session_id)
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        
        # Format inventory items
        inventory_items = []
        for item in character.inventory:
            inventory_items.append({
                "id": item.id,
                "type": item.type,
                "suit": item.suit,
                "bonus": item.bonus,
                "description": item.description
            })
        
        # Format equipped items
        equipped_items = {}
        if character.equipped:
            for slot, item in character.equipped.items():
                equipped_items[slot] = {
                    "id": item.id,
                    "type": item.type,
                    "suit": item.suit,
                    "bonus": item.bonus,
                    "description": item.description
                }
        
        return {
            "inventory": inventory_items,
            "equipped": equipped_items,
            "total_items": len(inventory_items)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============= WORLDS ENDPOINTS =============

@app.get("/worlds")
async def get_available_worlds():
    """Get list of available worlds."""
    try:
        from core.config import world_manager
        worlds = world_manager.get_available_worlds()
        
        worlds_list = []
        for world_id, world_name in worlds.items():
            world_config = world_manager.get_world_config(world_id)
            worlds_list.append({
                "id": world_id,
                "name": world_name,
                "description": world_config.get("description", "") if world_config else ""
            })
        
        return {
            "worlds": worlds_list,
            "total": len(worlds_list)
        }
    
    except Exception as e:
        logger.error(f"Error getting worlds: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/worlds/{world_id}")
async def get_world_config(world_id: str):
    """Get configuration for specific world."""
    try:
        from core.config import world_manager
        world_config = world_manager.get_world_config(world_id)
        
        if not world_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"World {world_id} not found"
            )
        
        return world_config
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting world config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============= SAVE/LOAD ENDPOINTS =============

@app.get("/users/{user_id}/saves")
async def get_user_saves(user_id: int):
    """Get all saved sessions for a user."""
    try:
        saved_sessions = db_manager.get_user_saved_sessions(user_id)
        
        saves_list = []
        for session in saved_sessions:
            saves_list.append({
                "session_id": session.id,
                "slot_number": session.slot_number,
                "world_id": session.world_id,
                "current_turn": session.current_turn,
                "saved_at": session.saved_at.isoformat() if session.saved_at else None,
                "save_name": session.save_name
            })
        
        return {
            "saves": saves_list,
            "total": len(saves_list)
        }
    
    except Exception as e:
        logger.error(f"Error getting saves: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/sessions/{session_id}/save")
async def save_session(session_id: int, slot: int, save_name: str = None):
    """Save session to specific slot."""
    try:
        # Validate session exists
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Validate slot number (1-5)
        if slot < 1 or slot > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot number must be between 1 and 5"
            )
        
        # Save to slot
        success = db_manager.save_session_to_slot(session_id, slot, save_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save session"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "slot": slot,
            "message": f"Session saved to slot {slot}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/sessions/{session_id}/load")
async def load_session(session_id: int, user_id: int):
    """
    Load saved session.
    Deactivates all other sessions and activates this one.
    """
    try:
        # Validate session exists
        session = db_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Deactivate all other sessions
        db_manager.deactivate_user_sessions(user_id)
        
        # Activate this session
        with db_manager.get_session() as db_session:
            from core.database.models import SessionDB
            session_obj = db_session.query(SessionDB).filter_by(id=session_id).first()
            if session_obj:
                session_obj.is_active = True
                db_session.commit()
        
        return {
            "success": True,
            "session_id": session_id,
            "world_id": session.world_id,
            "current_turn": session.current_turn,
            "message": "Session loaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "core.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )


