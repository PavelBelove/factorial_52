"""
SQLAlchemy database models.
Designed to be easily migrated from SQLite to PostgreSQL.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserDB(Base):
    """User table - represents platform users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(String(255), unique=True, nullable=False, index=True)  # telegram_id, discord_id, etc.
    platform_type = Column(String(50), default="telegram")  # telegram, discord, web, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User preferences
    language = Column(String(10), default="ru")  # User's language preference
    current_world = Column(String(50), default="isekai")  # Last selected world
    
    # Relationships
    sessions = relationship("SessionDB", back_populates="user", cascade="all, delete-orphan")


class SessionDB(Base):
    """Session table - conversation sessions."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_type = Column(String(50), default="game")  # game, companion
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Session state
    current_turn = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # World & Save system
    world_id = Column(String(50), default="isekai", nullable=False)  # World for this session
    slot_number = Column(Integer, nullable=True)  # Save slot (1-5), None if not saved
    is_saved = Column(Boolean, default=False)  # Is this session saved?
    saved_at = Column(DateTime, nullable=True)  # When was it last saved
    save_name = Column(String(255), nullable=True)  # Optional custom save name
    
    # Relationships
    user = relationship("UserDB", back_populates="sessions")
    quants = relationship("QuantDB", back_populates="session", cascade="all, delete-orphan")
    turns = relationship("TurnDB", back_populates="session", cascade="all, delete-orphan")
    summaries = relationship("SummaryDB", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_user_slot", "user_id", "slot_number"),
        Index("idx_session_world", "world_id"),
    )


class QuantDB(Base):
    """Quant table - atomic semantic memory units."""
    __tablename__ = "quants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    
    # Quant data
    quant_id = Column(String(255), nullable=False)  # The actual name like "Маша", "Таверна Атарикс"
    type = Column(String(50), default="other")  # npc, location, item, etc.
    synopsis = Column(String(500), nullable=True)  # Short summary with =markers= for navigation
    body = Column(JSON, default=dict)  # Free-form content
    links = Column(JSON, default=dict)  # Semantic links to other quants
    aliases = Column(JSON, default=list)  # Alternative names: ["Дриада из леса", "Ивушка"]
    
    # Metadata
    created_at = Column(Integer, nullable=True)  # Turn number
    updated_at = Column(Integer, nullable=True)  # Turn number
    is_game = Column(Boolean, default=False)  # Game-specific vs companion memory
    needs_summarization = Column(Boolean, default=False)  # True if quant is too long and needs condensing
    
    # Relationships
    session = relationship("SessionDB", back_populates="quants")
    
    # Indexes
    __table_args__ = (
        Index("idx_quant_session_id", "session_id", "quant_id"),
        Index("idx_quant_session_type", "session_id", "type"),
    )


class TurnDB(Base):
    """Turn table - conversation exchanges."""
    __tablename__ = "turns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    
    # Content
    user_message = Column(Text, nullable=False)
    agent_reply = Column(Text, nullable=False)
    translated_json = Column(Text, nullable=True)  # English JSON compressed version
    
    # Metadata
    requested_quants = Column(JSON, default=list)  # Quants requested for next turn
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Cost tracking
    cost_gm = Column(Float, default=0.0)
    cost_quantizer = Column(Float, default=0.0)
    cost_summarizer = Column(Float, default=0.0)
    cost_translator = Column(Float, default=0.0)
    cost_total = Column(Float, default=0.0)
    
    # Relationships
    session = relationship("SessionDB", back_populates="turns")
    
    # Indexes
    __table_args__ = (
        Index("idx_turn_session_number", "session_id", "turn_number"),
    )


class SummaryDB(Base):
    """Summary table - condensed conversation history."""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    summary_text = Column(Text, nullable=False)
    
    # Metadata
    turns_start = Column(Integer, nullable=False)
    turns_end = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_full_rewrite = Column(Boolean, default=False)
    
    # Relationships
    session = relationship("SessionDB", back_populates="summaries")
    
    # Indexes
    __table_args__ = (
        Index("idx_summary_session", "session_id"),
    )


class CharacterDB(Base):
    """Character table - RPG character data for game sessions."""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Characteristics (4 suits)
    spades = Column(Integer, default=0, nullable=False)      # ♠ Strength, melee combat
    hearts = Column(Integer, default=0, nullable=False)      # ♥ Magic, magical defense
    diamonds = Column(Integer, default=0, nullable=False)    # ♦ Endurance, physical defense
    clubs = Column(Integer, default=0, nullable=False)       # ♣ Agility, ranged combat
    
    # Experience (auto-leveling, not shown to player)
    spades_xp = Column(Integer, default=0, nullable=False)   # At 10 XP → +1 to spades
    hearts_xp = Column(Integer, default=0, nullable=False)
    diamonds_xp = Column(Integer, default=0, nullable=False)
    clubs_xp = Column(Integer, default=0, nullable=False)
    
    # State
    hp = Column(Integer, default=100, nullable=False)
    max_hp = Column(Integer, default=100, nullable=False)
    mana = Column(Integer, default=50, nullable=False)
    max_mana = Column(Integer, default=50, nullable=False)
    gold = Column(Integer, default=0, nullable=False)
    
    # Inventory
    inventory = Column(JSON, default=list)  # List of items
    equipped = Column(JSON, default=dict)   # Map of equipped items
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_character_session", "session_id"),
    )

