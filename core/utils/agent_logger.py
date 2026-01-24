"""
Agent debug logger - saves last call context and response for each agent.
Only works when settings.debug is True.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.config import settings


def log_agent_call(
    agent_name: str,
    context: List[Dict[str, str]],
    response: Any,
    session_id: Optional[int] = None,
    turn_number: Optional[int] = None
):
    """
    Log agent call to file (overwrites previous).
    
    Args:
        agent_name: Name of agent (gm, quantizer, summarizer, translator)
        context: Full context messages sent to LLM
        response: Response from agent
        session_id: Optional session ID
        turn_number: Optional turn number
    """
    if not settings.debug:
        return
    
    # Create logs/agents directory if not exists
    log_dir = Path("logs/agents")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{agent_name}_last.log"
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write(f"AGENT: {agent_name.upper()}\n")
            f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
            if session_id:
                f.write(f"SESSION: {session_id}\n")
            if turn_number:
                f.write(f"TURN: {turn_number}\n")
            f.write("=" * 80 + "\n\n")
            
            # Context
            f.write("CONTEXT (Input to LLM):\n")
            f.write("=" * 80 + "\n")
            for i, msg in enumerate(context, 1):
                f.write(f"\n[Message {i}] Role: {msg.get('role', 'unknown')}\n")
                f.write("-" * 80 + "\n")
                f.write(msg.get('content', '') + "\n")
            
            f.write("\n" + "=" * 80 + "\n")
            
            # Response
            f.write("\nRESPONSE (Output from LLM):\n")
            f.write("=" * 80 + "\n")
            
            if isinstance(response, dict):
                # Pretty print dict
                f.write(json.dumps(response, ensure_ascii=False, indent=2))
            elif isinstance(response, str):
                f.write(response)
            else:
                f.write(str(response))
            
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("END OF LOG\n")
            f.write("=" * 80 + "\n")
    
    except Exception as e:
        # Silent fail - logging should not break execution
        print(f"Warning: Failed to write agent log for {agent_name}: {e}")

