"""
IQIDE Client - Phase 4
Local client for connecting to Command Center
"""

from .config import Config
from .api_client import CommandCenterClient
from .formatter import ResultFormatter
from .cli import main

__all__ = ["Config", "CommandCenterClient", "ResultFormatter", "main"]

__version__ = "0.4.0"

