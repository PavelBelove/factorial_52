"""
API request/response models.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request to create new session."""
    platform_id: str = Field(..., description="Platform user ID (e.g., telegram ID)")
    platform_type: str = Field(default="telegram", description="Platform type")
    session_type: str = Field(default="game", description="Session type: game or companion")
    world_id: str = Field(default="isekai", description="World ID for game session")


class CreateSessionResponse(BaseModel):
    """Response with created session."""
    session_id: int
    user_id: int
    session_type: str
    message: str = "Session created successfully"


class SendMessageRequest(BaseModel):
    """Request to send message to agent."""
    session_id: int
    message: str
    system_prompt_parts: Optional[Dict[str, str]] = None


class SendMessageResponse(BaseModel):
    """Response from agent."""
    reply: str
    turn_number: int
    quants_used: List[str]
    quants_requested: List[str]


class GetSessionInfoResponse(BaseModel):
    """Session information."""
    session_id: int
    user_id: int
    session_type: str
    current_turn: int
    is_active: bool
    quants_count: int
    summary_length: int


class GetQuantsResponse(BaseModel):
    """List of quants."""
    quants: List[Dict[str, Any]]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str

