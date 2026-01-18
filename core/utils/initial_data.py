"""
Utilities for loading initial game data (summary and quants).
"""
import json
from pathlib import Path
from typing import List, Dict, Any

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_initial_summary(world_name: str = "default") -> str:
    """
    Load initial summary for a new game session.
    
    Args:
        world_name: Name of world/setting (for future multi-world support)
        
    Returns:
        Initial summary text
        
    Raises:
        FileNotFoundError: If summary file doesn't exist
    """
    summary_path = PROJECT_ROOT / "data" / "initial_summary.md"
    
    if not summary_path.exists():
        raise FileNotFoundError(f"Initial summary file not found: {summary_path}")
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_initial_quants(world_name: str = "default") -> List[Dict[str, Any]]:
    """
    Load initial quants for a new game session.
    
    Args:
        world_name: Name of world/setting (for future multi-world support)
        
    Returns:
        List of quant dictionaries
        
    Raises:
        FileNotFoundError: If quants file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    quants_path = PROJECT_ROOT / "data" / "initial_quants.json"
    
    if not quants_path.exists():
        raise FileNotFoundError(f"Initial quants file not found: {quants_path}")
    
    with open(quants_path, 'r', encoding='utf-8') as f:
        quants = json.load(f)
    
    if not isinstance(quants, list):
        raise ValueError("Initial quants file must contain a JSON array")
    
    return quants


def get_initial_data(world_name: str = "default") -> Dict[str, Any]:
    """
    Get all initial data for a new game session.
    
    Args:
        world_name: Name of world/setting
        
    Returns:
        Dict with 'summary' and 'quants' keys
    """
    return {
        "summary": load_initial_summary(world_name),
        "quants": load_initial_quants(world_name)
    }

