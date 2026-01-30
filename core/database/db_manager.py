"""
Database Manager - handles all database operations.
Designed to be easily migrated from SQLite to PostgreSQL.
"""
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from core.config import settings
from core.database.models import Base, UserDB, SessionDB, QuantDB, TurnDB, SummaryDB, CharacterDB
from core.models import Quant, QuantType, SessionType

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations.
    Uses SQLAlchemy for easy migration from SQLite to PostgreSQL.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.database_url
        
        # SQLite-specific configuration
        if self.database_url.startswith("sqlite"):
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            # PostgreSQL configuration (for future)
            self.engine = create_engine(self.database_url, pool_pre_ping=True)
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
        # Run simple migrations for new columns
        self._run_migrations()

    def _run_migrations(self):
        """Add new columns to existing tables if they don't exist."""
        from sqlalchemy import inspect, text
        inspector = inspect(self.engine)

        # Check users table for new settings columns
        if "users" in inspector.get_table_names():
            existing_columns = [col["name"] for col in inspector.get_columns("users")]

            with self.engine.connect() as conn:
                if "difficulty" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN difficulty VARCHAR(20) DEFAULT 'normal'"))
                    conn.commit()
                if "content_filter" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN content_filter VARCHAR(20) DEFAULT 'safe'"))
                    conn.commit()

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    # ============= USER OPERATIONS =============
    
    def get_or_create_user(self, platform_id: str, platform_type: str = "telegram") -> UserDB:
        """Get existing user or create new one."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(
                UserDB.platform_id == platform_id
            ).first()
            
            if not user:
                user = UserDB(
                    platform_id=platform_id,
                    platform_type=platform_type
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return user
    
    # ============= SESSION OPERATIONS =============
    
    def create_session(
        self,
        user_id: int,
        session_type: SessionType = SessionType.GAME,
        world_id: str = "isekai"
    ) -> SessionDB:
        """Create new session with specified world."""
        with self.get_session() as session:
            new_session = SessionDB(
                user_id=user_id,
                session_type=session_type.value,
                world_id=world_id
            )
            session.add(new_session)
            session.commit()
            session.refresh(new_session)
            return new_session
    
    def get_session_by_id(self, session_id: int) -> Optional[SessionDB]:
        """Get session by ID."""
        with self.get_session() as session:
            return session.query(SessionDB).filter(
                SessionDB.id == session_id
            ).first()
    
    def get_session_by_platform_id(
        self,
        platform_id: str,
        platform_type: str = "telegram"
    ) -> Optional[SessionDB]:
        """Get active session by platform ID."""
        with self.get_session() as session:
            # Find user by platform_id
            user = session.query(UserDB).filter(
                UserDB.platform_id == platform_id,
                UserDB.platform_type == platform_type
            ).first()
            
            if not user:
                return None
            
            # Get most recent session for this user
            return session.query(SessionDB).filter(
                SessionDB.user_id == user.id
            ).order_by(SessionDB.id.desc()).first()
    
    def get_active_session(
        self,
        user_id: int,
        session_type: Optional[SessionType] = None
    ) -> Optional[SessionDB]:
        """Get user's active session."""
        with self.get_session() as session:
            query = session.query(SessionDB).filter(
                SessionDB.user_id == user_id,
                SessionDB.is_active == True
            )
            
            if session_type:
                query = query.filter(SessionDB.session_type == session_type.value)
            
            return query.first()
    
    def update_session_turn(self, session_id: int, turn_number: int):
        """Update session's current turn."""
        with self.get_session() as session:
            db_session = session.query(SessionDB).filter(
                SessionDB.id == session_id
            ).first()
            
            if db_session:
                db_session.current_turn = turn_number
                session.commit()
    
    # ============= QUANT OPERATIONS =============
    
    def create_quant(
        self,
        session_id: int,
        quant: Quant
    ) -> QuantDB:
        """Create new quant."""
        with self.get_session() as session:
            db_quant = QuantDB(
                session_id=session_id,
                quant_id=quant.id,
                type=quant.type.value,
                synopsis=quant.synopsis,  # Save synopsis!
                body=quant.body,
                links=quant.links,
                aliases=quant.aliases,  # Save aliases!
                created_at=quant.created_at,
                updated_at=quant.updated_at,
                is_game=quant.is_game
            )
            session.add(db_quant)
            session.commit()
            session.refresh(db_quant)
            return db_quant
    
    def get_quant(
        self,
        session_id: int,
        quant_id: str
    ) -> Optional[QuantDB]:
        """Get quant by ID."""
        with self.get_session() as session:
            return session.query(QuantDB).filter(
                QuantDB.session_id == session_id,
                QuantDB.quant_id == quant_id
            ).first()
    
    def get_quants_by_ids(
        self,
        session_id: int,
        quant_ids: List[str]
    ) -> List[QuantDB]:
        """Get multiple quants by their IDs."""
        with self.get_session() as session:
            return session.query(QuantDB).filter(
                QuantDB.session_id == session_id,
                QuantDB.quant_id.in_(quant_ids)
            ).all()
    
    def get_all_quants(self, session_id: int) -> List[QuantDB]:
        """Get all quants for a session."""
        with self.get_session() as session:
            return session.query(QuantDB).filter(
                QuantDB.session_id == session_id
            ).all()
    
    def update_quant(
        self,
        session_id: int,
        quant_id: str,
        synopsis: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        updated_at: Optional[int] = None,
        needs_summarization: Optional[bool] = None
    ):
        """Update quant fields."""
        with self.get_session() as session:
            db_quant = session.query(QuantDB).filter(
                QuantDB.session_id == session_id,
                QuantDB.quant_id == quant_id
            ).first()
            
            if db_quant:
                if synopsis is not None:
                    db_quant.synopsis = synopsis
                if body is not None:
                    db_quant.body = body
                if links is not None:
                    db_quant.links = links
                if updated_at is not None:
                    db_quant.updated_at = updated_at
                if needs_summarization is not None:
                    db_quant.needs_summarization = needs_summarization
                
                session.commit()
    
    def delete_quant(self, session_id: int, quant_id: str):
        """Delete quant."""
        with self.get_session() as session:
            db_quant = session.query(QuantDB).filter(
                QuantDB.session_id == session_id,
                QuantDB.quant_id == quant_id
            ).first()
            
            if db_quant:
                session.delete(db_quant)
                session.commit()
    
    def rename_quant(
        self,
        session_id: int,
        old_id: str,
        new_id: str,
        aliases: List[str] = None
    ):
        """
        Rename quant by changing its ID.
        Old ID is preserved in aliases.
        """
        with self.get_session() as session:
            quant = session.query(QuantDB).filter(
                QuantDB.session_id == session_id,
                QuantDB.quant_id == old_id
            ).first()
            
            if quant:
                quant.quant_id = new_id
                if aliases:
                    quant.aliases = aliases
                session.commit()
    
    # ============= TURN OPERATIONS =============
    
    def create_turn(
        self,
        session_id: int,
        turn_number: int,
        user_message: str,
        agent_reply: str,
        requested_quants: List[str],
        cost_gm: float = 0.0,
        cost_quantizer: float = 0.0,
        cost_summarizer: float = 0.0,
        cost_translator: float = 0.0
    ) -> TurnDB:
        """Create new turn with cost tracking."""
        cost_total = cost_gm + cost_quantizer + cost_summarizer + cost_translator
        
        with self.get_session() as session:
            turn = TurnDB(
                session_id=session_id,
                turn_number=turn_number,
                user_message=user_message,
                agent_reply=agent_reply,
                requested_quants=requested_quants,
                cost_gm=cost_gm,
                cost_quantizer=cost_quantizer,
                cost_summarizer=cost_summarizer,
                cost_translator=cost_translator,
                cost_total=cost_total
            )
            session.add(turn)
            session.commit()
            session.refresh(turn)
            return turn
    
    def get_recent_turns(
        self,
        session_id: int,
        limit: int
    ) -> List[TurnDB]:
        """Get recent turns."""
        with self.get_session() as session:
            return session.query(TurnDB).filter(
                TurnDB.session_id == session_id
            ).order_by(TurnDB.turn_number.desc()).limit(limit).all()
    
    def get_turns_range(
        self,
        session_id: int,
        start_turn: int,
        end_turn: int
    ) -> List[TurnDB]:
        """Get turns in specific range."""
        with self.get_session() as session:
            return session.query(TurnDB).filter(
                TurnDB.session_id == session_id,
                TurnDB.turn_number >= start_turn,
                TurnDB.turn_number <= end_turn
            ).order_by(TurnDB.turn_number).all()
    
    def delete_last_turn(self, session_id: int) -> bool:
        """
        Delete the last turn from the session and decrement current_turn.
        Also clears requested_quants from the previous turn to prevent stale quants.
        Also deletes summaries that include the deleted turn to prevent context conflicts.
        Returns True if deleted, False if no turns exist.
        Used for /undo and /retry functionality.
        """
        with self.get_session() as session:
            # Get session
            db_session = session.query(SessionDB).filter(
                SessionDB.id == session_id
            ).first()
            
            if not db_session or db_session.current_turn == 0:
                return False
            
            # Get last turn number before deletion
            deleted_turn_number = db_session.current_turn
            
            # Get last turn
            last_turn = session.query(TurnDB).filter(
                TurnDB.session_id == session_id,
                TurnDB.turn_number == db_session.current_turn
            ).first()
            
            if last_turn:
                # Delete the turn
                session.delete(last_turn)
                
                # Decrement current_turn
                db_session.current_turn -= 1
                
                # Delete summaries that include the deleted turn
                # This prevents outdated summaries from confusing the GM
                from core.database.models import SummaryDB
                outdated_summaries = session.query(SummaryDB).filter(
                    SummaryDB.session_id == session_id,
                    SummaryDB.turns_end >= deleted_turn_number
                ).all()
                
                for summary in outdated_summaries:
                    logger.info(f"Deleting outdated summary (turns {summary.turns_start}-{summary.turns_end}) after undo to turn {db_session.current_turn}")
                    session.delete(summary)
                
                # Clear requested_quants from the NEW last turn (previous turn)
                # This prevents stale quants from confusing GM on retry
                if db_session.current_turn > 0:
                    prev_turn = session.query(TurnDB).filter(
                        TurnDB.session_id == session_id,
                        TurnDB.turn_number == db_session.current_turn
                    ).first()
                    
                    if prev_turn:
                        prev_turn.requested_quants = "[]"  # Clear quant requests
                
                session.commit()
                return True
            
            return False
    
    def trim_old_turns(self, session_id: int, keep_last_n: int = 4) -> int:
        """
        Delete old turns, keeping only the last N.
        Called after summarization to maintain raw window size.
        Returns: number of deleted turns.
        """
        with self.get_session() as session:
            # Get all turns ordered by turn_number
            all_turns = session.query(TurnDB).filter(
                TurnDB.session_id == session_id
            ).order_by(TurnDB.turn_number.desc()).all()
            
            if len(all_turns) <= keep_last_n:
                return 0
            
            # Keep last N, delete the rest
            turns_to_keep = all_turns[:keep_last_n]
            min_turn_to_keep = min(t.turn_number for t in turns_to_keep)
            
            # Delete older turns
            deleted_count = session.query(TurnDB).filter(
                TurnDB.session_id == session_id,
                TurnDB.turn_number < min_turn_to_keep
            ).delete()
            
            session.commit()
            return deleted_count
    
    def update_turn_translation(self, session_id: int, turn_number: int, translated_json: str):
        """Update turn with translated JSON."""
        with self.get_session() as session:
            turn = session.query(TurnDB).filter(
                TurnDB.session_id == session_id,
                TurnDB.turn_number == turn_number
            ).first()
            
            if turn:
                turn.translated_json = translated_json
                session.commit()
    
    def update_turn_costs(
        self,
        session_id: int,
        turn_number: int,
        cost_quantizer: float = 0.0,
        cost_summarizer: float = 0.0,
        cost_translator: float = 0.0
    ):
        """Update turn costs after background processing."""
        with self.get_session() as session:
            turn = session.query(TurnDB).filter(
                TurnDB.session_id == session_id,
                TurnDB.turn_number == turn_number
            ).first()
            
            if turn:
                turn.cost_quantizer = cost_quantizer
                turn.cost_summarizer = cost_summarizer
                turn.cost_translator = cost_translator
                turn.cost_total = (
                    turn.cost_gm +
                    cost_quantizer +
                    cost_summarizer +
                    cost_translator
                )
                session.commit()
    
    def get_session_costs(self, session_id: int) -> Dict[str, Any]:
        """Get aggregated costs for entire session."""
        with self.get_session() as session:
            turns = session.query(TurnDB).filter(
                TurnDB.session_id == session_id
            ).all()
            
            total_gm = sum(t.cost_gm or 0.0 for t in turns)
            total_quantizer = sum(t.cost_quantizer or 0.0 for t in turns)
            total_summarizer = sum(t.cost_summarizer or 0.0 for t in turns)
            total_translator = sum(t.cost_translator or 0.0 for t in turns)
            total_all = sum(t.cost_total or 0.0 for t in turns)
            
            return {
                "num_turns": len(turns),
                "gm": total_gm,
                "quantizer": total_quantizer,
                "summarizer": total_summarizer,
                "translator": total_translator,
                "total": total_all
            }
    
    # ============= SUMMARY OPERATIONS =============
    
    def create_summary(
        self,
        session_id: int,
        summary_text: str,
        turns_start: int,
        turns_end: int,
        is_full_rewrite: bool = False
    ) -> SummaryDB:
        """Create new summary."""
        with self.get_session() as session:
            summary = SummaryDB(
                session_id=session_id,
                summary_text=summary_text,
                turns_start=turns_start,
                turns_end=turns_end,
                is_full_rewrite=is_full_rewrite
            )
            session.add(summary)
            session.commit()
            session.refresh(summary)
            return summary
    
    def get_all_summaries(self, session_id: int) -> List[SummaryDB]:
        """Get all summaries for a session."""
        with self.get_session() as session:
            return session.query(SummaryDB).filter(
                SummaryDB.session_id == session_id
            ).order_by(SummaryDB.turns_start).all()
    
    def get_latest_summary(self, session_id: int) -> Optional[SummaryDB]:
        """Get latest summary."""
        with self.get_session() as session:
            return session.query(SummaryDB).filter(
                SummaryDB.session_id == session_id
            ).order_by(SummaryDB.turns_end.desc()).first()
    
    # ============= CHARACTER OPERATIONS =============
    
    def get_character(self, session_id: int) -> Optional[CharacterDB]:
        """Get character for session."""
        with self.get_session() as session:
            return session.query(CharacterDB).filter(
                CharacterDB.session_id == session_id
            ).first()
    
    def create_character(
        self,
        session_id: int,
        spades: int,
        hearts: int,
        diamonds: int,
        clubs: int,
        hp: int,
        max_hp: int,
        mana: int,
        max_mana: int,
        gold: int = 0
    ) -> CharacterDB:
        """Create new character."""
        with self.get_session() as session:
            character = CharacterDB(
                session_id=session_id,
                spades=spades,
                hearts=hearts,
                diamonds=diamonds,
                clubs=clubs,
                hp=hp,
                max_hp=max_hp,
                mana=mana,
                max_mana=max_mana,
                gold=gold
            )
            session.add(character)
            session.commit()
            session.refresh(character)
            return character
    
    def update_character(
        self,
        session_id: int,
        spades: Optional[int] = None,
        hearts: Optional[int] = None,
        diamonds: Optional[int] = None,
        clubs: Optional[int] = None,
        spades_xp: Optional[int] = None,
        hearts_xp: Optional[int] = None,
        diamonds_xp: Optional[int] = None,
        clubs_xp: Optional[int] = None,
        hp: Optional[int] = None,
        max_hp: Optional[int] = None,
        mana: Optional[int] = None,
        max_mana: Optional[int] = None,
        gold: Optional[int] = None,
        inventory: Optional[List[Dict]] = None,
        equipped: Optional[Dict] = None
    ):
        """Update character data."""
        with self.get_session() as session:
            character = session.query(CharacterDB).filter(
                CharacterDB.session_id == session_id
            ).first()
            
            if not character:
                return
            
            if spades is not None:
                character.spades = spades
            if hearts is not None:
                character.hearts = hearts
            if diamonds is not None:
                character.diamonds = diamonds
            if clubs is not None:
                character.clubs = clubs
            if spades_xp is not None:
                character.spades_xp = spades_xp
            if hearts_xp is not None:
                character.hearts_xp = hearts_xp
            if diamonds_xp is not None:
                character.diamonds_xp = diamonds_xp
            if clubs_xp is not None:
                character.clubs_xp = clubs_xp
            if hp is not None:
                character.hp = hp
            if max_hp is not None:
                character.max_hp = max_hp
            if mana is not None:
                character.mana = mana
            if max_mana is not None:
                character.max_mana = max_mana
            if gold is not None:
                character.gold = gold
            if inventory is not None:
                character.inventory = inventory
            if equipped is not None:
                character.equipped = equipped
            
            session.commit()
    
    # ============= SAVE SYSTEM OPERATIONS =============
    
    def get_user_saved_sessions(self, user_id: int) -> List[SessionDB]:
        """
        Get all saved sessions for a user (is_saved=True).
        Returns sessions ordered by slot number.
        """
        with self.get_session() as session:
            return session.query(SessionDB).filter(
                SessionDB.user_id == user_id,
                SessionDB.is_saved == True
            ).order_by(SessionDB.slot_number).all()
    
    def get_session_in_slot(self, user_id: int, slot: int) -> Optional[SessionDB]:
        """Get session in specific save slot."""
        with self.get_session() as session:
            return session.query(SessionDB).filter(
                SessionDB.user_id == user_id,
                SessionDB.slot_number == slot,
                SessionDB.is_saved == True
            ).first()
    
    def save_session_to_slot(
        self,
        session_id: int,
        slot: int,
        save_name: Optional[str] = None
    ) -> bool:
        """
        Save session to a specific slot.
        If slot is already occupied, overwrites it.
        
        Returns:
            True if successful, False otherwise
        """
        from datetime import datetime
        
        with self.get_session() as session:
            # Get the session to save
            game_session = session.query(SessionDB).filter(
                SessionDB.id == session_id
            ).first()
            
            if not game_session:
                return False
            
            # Check if slot is occupied by another session
            existing_in_slot = session.query(SessionDB).filter(
                SessionDB.user_id == game_session.user_id,
                SessionDB.slot_number == slot,
                SessionDB.is_saved == True,
                SessionDB.id != session_id  # Different session
            ).first()
            
            if existing_in_slot:
                # Clear the old session from this slot
                existing_in_slot.slot_number = None
                existing_in_slot.is_saved = False
                existing_in_slot.saved_at = None
            
            # Save current session to slot
            game_session.slot_number = slot
            game_session.is_saved = True
            game_session.saved_at = datetime.utcnow()
            if save_name:
                game_session.save_name = save_name
            
            session.commit()
            return True
    
    def delete_session_from_slot(self, session_id: int) -> bool:
        """
        Remove session from save slot (but keep session in DB).
        Just clears slot_number and is_saved flag.
        """
        with self.get_session() as session:
            game_session = session.query(SessionDB).filter(
                SessionDB.id == session_id
            ).first()
            
            if not game_session:
                return False
            
            game_session.slot_number = None
            game_session.is_saved = False
            game_session.saved_at = None
            session.commit()
            return True
    
    def deactivate_user_sessions(self, user_id: int):
        """Deactivate all sessions for a user (for starting new game)."""
        with self.get_session() as session:
            sessions = session.query(SessionDB).filter(
                SessionDB.user_id == user_id,
                SessionDB.is_active == True
            ).all()
            
            for game_session in sessions:
                game_session.is_active = False
            
            session.commit()
    
    # ============= USER PREFERENCES =============
    
    def set_user_language(self, user_id: int, language: str):
        """Set user's language preference."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                user.language = language
                session.commit()
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's language preference."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            return user.language if user else "ru"
    
    def set_user_current_world(self, user_id: int, world_id: str):
        """Set user's last selected world."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                user.current_world = world_id
                session.commit()
    
    def get_user_current_world(self, user_id: int) -> str:
        """Get user's last selected world."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            return user.current_world if user else "isekai"

    def set_user_difficulty(self, user_id: int, difficulty: str):
        """Set user's difficulty preference (easy/normal/hard)."""
        if difficulty not in ("easy", "normal", "hard"):
            difficulty = "normal"
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                user.difficulty = difficulty
                session.commit()

    def get_user_difficulty(self, user_id: int) -> str:
        """Get user's difficulty preference."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            return user.difficulty if user and user.difficulty else "normal"

    def set_user_content_filter(self, user_id: int, content_filter: str):
        """Set user's content filter preference (safe/romantic/adult)."""
        if content_filter not in ("safe", "romantic", "adult"):
            content_filter = "safe"
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                user.content_filter = content_filter
                session.commit()

    def get_user_content_filter(self, user_id: int) -> str:
        """Get user's content filter preference."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            return user.content_filter if user and user.content_filter else "safe"

    def get_user_settings(self, user_id: int) -> dict:
        """Get all user settings as dict."""
        with self.get_session() as session:
            user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if user:
                return {
                    "language": user.language or "ru",
                    "difficulty": user.difficulty or "normal",
                    "content_filter": user.content_filter or "safe",
                    "current_world": user.current_world or "isekai"
                }
            return {
                "language": "ru",
                "difficulty": "normal",
                "content_filter": "safe",
                "current_world": "isekai"
            }

