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
            
            # Context - show both formatted and RAW JSON
            f.write("CONTEXT (Input to LLM):\n")
            f.write("=" * 80 + "\n\n")
            
            # Formatted view (readable)
            f.write("### FORMATTED VIEW ###\n\n")
            for i, msg in enumerate(context, 1):
                f.write(f"[Message {i}] Role: {msg.get('role', 'unknown')}\n")
                f.write("-" * 80 + "\n")
                content = msg.get('content', '')
                # Truncate very long content
                if len(content) > 10000:
                    f.write(content[:10000] + f"\n... [truncated, {len(content)} total chars]\n")
                else:
                    f.write(content + "\n")
                f.write("\n")
            
            # RAW JSON view
            f.write("\n" + "=" * 80 + "\n")
            f.write("### RAW JSON (Full context as sent to API) ###\n")
            f.write(json.dumps(context, ensure_ascii=False, indent=2))
            
            f.write("\n\n" + "=" * 80 + "\n")
            
            # Response
            f.write("\nRESPONSE (Output from LLM):\n")
            f.write("=" * 80 + "\n")
            
            if isinstance(response, dict):
                # Extract metadata if present
                usage = response.get("usage")
                cost = response.get("cost")
                
                # Print metadata first if present
                if usage or cost:
                    f.write("\n### API METADATA ###\n")
                    if usage:
                        f.write(f"Tokens: {usage.get('prompt_tokens', 'N/A')} prompt + "
                               f"{usage.get('completion_tokens', 'N/A')} completion = "
                               f"{usage.get('total_tokens', 'N/A')} total\n")
                    if cost:
                        f.write(f"Cost: ${cost:.6f}\n")
                    f.write("\n")
                
                # Pretty print full response
                f.write("### FULL RESPONSE (RAW JSON) ###\n")
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

