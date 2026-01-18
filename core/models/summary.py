"""
Summary model - condensed version of conversation history.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Summary(BaseModel):
    """
    Summary - condensed history of conversation.
    Created by Summarizer agent when raw turns window becomes too large.
    """
    id: Optional[int] = Field(default=None, description="Database ID")
    session_id: int = Field(..., description="Session this summary belongs to")
    
    # Content
    summary_text: str = Field(..., description="Condensed narrative with =quant= markers")
    
    # Metadata
    turns_start: int = Field(..., description="First turn number in this summary")
    turns_end: int = Field(..., description="Last turn number in this summary")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_full_rewrite: bool = Field(default=False, description="Whether this is a full rewrite or append")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "session_id": 1,
                "summary_text": "Игрок прибыл в город =Атарикс=. Познакомился с =Маша= в =Таверна Атарикс=...",
                "turns_start": 1,
                "turns_end": 10,
                "is_full_rewrite": False
            }
        }

