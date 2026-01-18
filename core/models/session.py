"""
Session model - represents a conversation session between user and agent.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SessionType(str, Enum):
    """Types of sessions."""
    GAME = "game"
    COMPANION = "companion"


class Session(BaseModel):
    """
    Session represents a continuous interaction between user and agent.
    Each session has its own memory (quants) and conversation history.
    """
    id: Optional[int] = Field(default=None, description="Database ID")
    user_id: int = Field(..., description="ID of the user")
    session_type: SessionType = Field(default=SessionType.GAME, description="Type of session")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Session state
    current_turn: int = Field(default=0, description="Current turn number")
    is_active: bool = Field(default=True, description="Whether session is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 12345,
                "session_type": "game",
                "current_turn": 25,
                "is_active": True
            }
        }

