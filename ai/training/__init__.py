"""
MarketAI Training Module
Self-training capabilities for the AI system.
"""

from .self_trainer import SelfTrainer
from .data_collector import DataCollector

__all__ = ['SelfTrainer', 'DataCollector']
