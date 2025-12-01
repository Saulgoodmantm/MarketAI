"""
Self-Trainer Module - Enables AI to train autonomously
"""

import os
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from .data_collector import DataCollector
from ..detection.screen_detector import ScreenDetector
from ..detection.web_detector import WebDetector
from ..data.shared_data import SharedDataManager


class SelfTrainer:
    """
    Autonomous self-training system for MarketAI.
    Continuously collects data and trains the model without human intervention.
    """
    
    def __init__(self, engine, config: Optional[Dict] = None):
        """
        Initialize the self-trainer.
        
        Args:
            engine: AIEngine instance
            config: Configuration dictionary
        """
        self.engine = engine
        self.config = config or self._default_config()
        self.is_running = False
        self._stop_flag = threading.Event()
        self._training_thread = None
        
        # Initialize components
        self.data_collector = DataCollector(self.config.get('data_collection', {}))
        self.screen_detector = ScreenDetector()
        self.web_detector = WebDetector()
        self.shared_data = SharedDataManager(engine.instance_id)
        
        # Callbacks
        self.on_training_complete: Optional[Callable] = None
        self.on_data_collected: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'training_interval': 300,  # seconds between training cycles
            'min_samples': 100,  # minimum samples before training
            'max_epochs': 10,
            'auto_detect_screens': True,
            'auto_detect_web': True,
            'data_collection': {
                'batch_size': 50,
                'storage_path': 'shared_data/training_data'
            }
        }
    
    def start(self):
        """Start the autonomous training loop."""
        if self.is_running:
            return False
        
        self.is_running = True
        self._stop_flag.clear()
        self._training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self._training_thread.start()
        return True
    
    def stop(self):
        """Stop the autonomous training loop."""
        self._stop_flag.set()
        self.is_running = False
        if self._training_thread:
            self._training_thread.join(timeout=30)
    
    def _training_loop(self):
        """Main autonomous training loop."""
        while not self._stop_flag.is_set():
            try:
                # Collect data from various sources
                collected_data = self._collect_all_data()
                
                if collected_data and len(collected_data.get('samples', [])) >= self.config['min_samples']:
                    # Check if this data hasn't been processed by other instances
                    if not self._is_duplicate_data(collected_data):
                        # Train on collected data
                        results = self.engine.train(
                            collected_data,
                            epochs=self.config['max_epochs']
                        )
                        
                        # Notify completion
                        if self.on_training_complete:
                            self.on_training_complete(results)
                        
                        # Share results with other instances
                        self._share_training_results(results)
                
                # Wait for next cycle
                self._stop_flag.wait(timeout=self.config['training_interval'])
                
            except Exception as e:
                if self.on_error:
                    self.on_error(e)
                time.sleep(10)  # Brief pause on error
    
    def _collect_all_data(self) -> Dict[str, Any]:
        """Collect data from all available sources."""
        collected = {'samples': [], 'sources': [], 'timestamp': datetime.now().isoformat()}
        
        # Collect from screen detection
        if self.config.get('auto_detect_screens', True):
            screen_data = self._collect_screen_data()
            if screen_data:
                collected['samples'].extend(screen_data.get('samples', []))
                collected['sources'].append('screen')
        
        # Collect from web detection
        if self.config.get('auto_detect_web', True):
            web_data = self._collect_web_data()
            if web_data:
                collected['samples'].extend(web_data.get('samples', []))
                collected['sources'].append('web')
        
        # Collect from data collector
        stored_data = self.data_collector.get_pending_data()
        if stored_data:
            collected['samples'].extend(stored_data.get('samples', []))
            collected['sources'].append('stored')
        
        if self.on_data_collected:
            self.on_data_collected(collected)
        
        return collected
    
    def _collect_screen_data(self) -> Optional[Dict[str, Any]]:
        """Collect training data from screen detection."""
        try:
            # Detect what's on screen
            detection_result = self.screen_detector.detect()
            
            if detection_result and detection_result.get('elements'):
                return {
                    'samples': [
                        {
                            'type': 'screen_element',
                            'data': elem,
                            'timestamp': datetime.now().isoformat()
                        }
                        for elem in detection_result['elements']
                    ]
                }
        except Exception as e:
            print(f"[WARNING] Screen data collection failed: {e}")
        
        return None
    
    def _collect_web_data(self) -> Optional[Dict[str, Any]]:
        """Collect training data from web detection."""
        try:
            # Detect web content
            web_result = self.web_detector.detect()
            
            if web_result and web_result.get('content'):
                return {
                    'samples': [
                        {
                            'type': 'web_content',
                            'data': content,
                            'timestamp': datetime.now().isoformat()
                        }
                        for content in web_result['content']
                    ]
                }
        except Exception as e:
            print(f"[WARNING] Web data collection failed: {e}")
        
        return None
    
    def _is_duplicate_data(self, data: Dict[str, Any]) -> bool:
        """Check if data has already been processed by any instance."""
        import hashlib
        import json
        
        data_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        return self.shared_data.is_data_processed(data_hash)
    
    def _share_training_results(self, results: Dict[str, Any]):
        """Share training results with other instances."""
        self.shared_data.share_training_results({
            'instance_id': self.engine.instance_id,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    def train_on_data(self, data: Any) -> Dict[str, Any]:
        """
        Manually trigger training on specific data.
        
        Args:
            data: Training data
            
        Returns:
            Training results
        """
        return self.engine.train(data, epochs=self.config['max_epochs'])
    
    def get_status(self) -> Dict[str, Any]:
        """Get current self-trainer status."""
        return {
            'is_running': self.is_running,
            'config': self.config,
            'data_collector_status': self.data_collector.get_status(),
            'screen_detector_status': self.screen_detector.get_status(),
            'web_detector_status': self.web_detector.get_status()
        }
