"""
Configuration settings for Action Agent
"""

import os
from pathlib import Path

# Base directory for logs
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOG_DIR / "action_agent.log"

# Command execution settings
DEFAULT_TIMEOUT = 1800  # 30 minutes
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB max output

# Allowed command prefixes (for security - can be expanded)
# Empty list means no restrictions for now (development phase)
ALLOWED_COMMAND_PREFIXES = []

# Log level
LOG_LEVEL = os.getenv("ACTION_AGENT_LOG_LEVEL", "INFO").upper()

