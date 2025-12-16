"""
Checkpointer setup for state persistence
"""

import os
from pathlib import Path
from typing import Optional

from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer(db_path: Optional[str] = None) -> SqliteSaver:
    """
    Get or create SQLite checkpointer for state persistence
    
    Args:
        db_path: Path to SQLite database (defaults to storage/checkpoints/agent_state.db)
        
    Returns:
        SqliteSaver instance
    """
    if db_path is None:
        # Default path: storage/checkpoints/agent_state.db
        base_dir = Path(__file__).parent.parent.parent.parent
        db_path = str(base_dir / "storage" / "checkpoints" / "agent_state.db")
    
    # Ensure directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create checkpointer
    checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{db_path}")
    
    return checkpointer

