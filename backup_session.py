#!/usr/bin/env python3
"""Backup current session to JSON for recovery."""
import json
import sys
from datetime import datetime
from core.database.db_manager import DatabaseManager

def backup_session(session_id: int, output_file: str = None):
    """Backup complete session data."""
    db = DatabaseManager()
    
    # Get session
    session = db.get_session_by_id(session_id)
    if not session:
        print(f"❌ Session {session_id} not found")
        return False
    
    print(f"📦 Backing up session {session_id}...")
    print(f"   Current turn: {session.current_turn}")
    print(f"   Active: {session.is_active}")
    
    # Get all data
    quants = db.get_all_quants(session_id)
    turns = db.get_all_turns(session_id)
    summaries = db.get_all_summaries(session_id)
    
    print(f"   Quants: {len(quants)}")
    print(f"   Turns: {len(turns)}")
    print(f"   Summaries: {len(summaries)}")
    
    # Build backup data
    backup_data = {
        "backup_timestamp": datetime.now().isoformat(),
        "session": {
            "id": session.id,
            "user_id": session.user_id,
            "session_type": session.session_type,
            "current_turn": session.current_turn,
            "is_active": session.is_active,
            "created_at": session.created_at.isoformat()
        },
        "quants": [
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
        ],
        "turns": [
            {
                "turn_number": t.turn_number,
                "user_message": t.user_message,
                "agent_reply": t.agent_reply,
                "requested_quants": t.requested_quants,
                "timestamp": t.timestamp.isoformat()
            }
            for t in turns
        ],
        "summaries": [
            {
                "summary_text": s.summary_text,
                "turns_start": s.turns_start,
                "turns_end": s.turns_end,
                "is_full_rewrite": s.is_full_rewrite,
                "created_at": s.created_at.isoformat()
            }
            for s in summaries
        ]
    }
    
    # Save to file
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/backup_session_{session_id}_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Backup saved to: {output_file}")
    return True

if __name__ == "__main__":
    session_id = int(sys.argv[1]) if len(sys.argv) > 1 else 29
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    backup_session(session_id, output_file)

