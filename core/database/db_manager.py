"""
Database Manager - handles all database operations.
Designed to be easily migrated from SQLite to PostgreSQL.
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from core.config import settings
from core.database.models import Base, UserDB, SessionDB, QuantDB, TurnDB, SummaryDB
from core.models import Quant, QuantType, SessionType


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
        session_type: SessionType = SessionType.GAME
    ) -> SessionDB:
        """Create new session."""
        with self.get_session() as session:
            new_session = SessionDB(
                user_id=user_id,
                session_type=session_type.value
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
                body=quant.body,
                links=quant.links,
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
        updated_at: Optional[int] = None
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
        requested_quants: List[str]
    ) -> TurnDB:
        """Create new turn."""
        with self.get_session() as session:
            turn = TurnDB(
                session_id=session_id,
                turn_number=turn_number,
                user_message=user_message,
                agent_reply=agent_reply,
                requested_quants=requested_quants
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

