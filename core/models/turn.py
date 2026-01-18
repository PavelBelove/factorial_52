"""
Turn model - represents one exchange in the conversation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Turn(BaseModel):
    """
    Turn represents one exchange: user message -> agent reply.
    """
    id: Optional[int] = Field(default=None, description="Database ID")
    session_id: int = Field(..., description="Session this turn belongs to")
    turn_number: int = Field(..., description="Sequential turn number")
    
    # Content
    user_message: str = Field(..., description="User's message")
    agent_reply: str = Field(..., description="Agent's reply")
    
    # Metadata
    requested_quants: List[str] = Field(default_factory=list, description="Quants requested by agent for next turn")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "session_id": 1,
                "turn_number": 5,
                "user_message": "Я захожу в таверну",
                "agent_reply": "Вы входите в уютную таверну...",
                "requested_quants": ["Таверна Атарикс", "Маша", "Бармен"]
            }
        }

