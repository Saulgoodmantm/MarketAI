"""
MarketAI - Advanced AI System for Market Analysis

This package provides:
- Self-training AI capabilities
- Screen and web detection for data collection
- Multi-instance data synchronization
- User and developer modes with authentication
- API integration for market data (AntiPublic, LZT Market, LolzTeam)
- Modern GUI with Autobuy, Market Watch, Analytics, and Settings tabs
"""

from .core import AIEngine, MarketAIModel
from .training import SelfTrainer, DataCollector
from .detection import ScreenDetector, WebDetector
from .data import SharedDataManager
from .config import Settings
from .utils import AuthManager, Profile

__version__ = "1.0.0"
__all__ = [
    'AIEngine',
    'MarketAIModel',
    'SelfTrainer',
    'DataCollector',
    'ScreenDetector',
    'WebDetector',
    'SharedDataManager',
    'Settings',
    'AuthManager',
    'Profile'
]
