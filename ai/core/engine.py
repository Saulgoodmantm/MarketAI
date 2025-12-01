"""
MarketAI Engine - Core AI processing engine
Handles model initialization, training, and inference
"""

import os
import json
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Local imports
from ..data.shared_data import SharedDataManager
from ..config.settings import Settings


class AIEngine:
    """Main AI Engine for MarketAI system."""
    
    def __init__(self, instance_id: Optional[str] = None):
        """
        Initialize the AI Engine.
        
        Args:
            instance_id: Unique identifier for this instance
        """
        self.instance_id = instance_id or self._generate_instance_id()
        self.settings = Settings()
        self.shared_data = SharedDataManager(self.instance_id)
        self.model = None
        self.is_training = False
        self._lock = threading.Lock()
        
    def _generate_instance_id(self) -> str:
        """Generate a unique instance ID based on machine info."""
        import platform
        import uuid
        machine_info = f"{platform.node()}-{uuid.getnode()}-{os.getpid()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    
    def initialize(self) -> bool:
        """
        Initialize the AI engine and load models.
        
        Returns:
            True if initialization successful
        """
        try:
            # Register this instance with shared data system
            self.shared_data.register_instance({
                'instance_id': self.instance_id,
                'start_time': datetime.now().isoformat(),
                'status': 'initializing'
            })
            
            # Load or create model
            self.model = self._load_or_create_model()
            
            # Update status
            self.shared_data.update_instance_status(self.instance_id, 'ready')
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize AI Engine: {e}")
            return False
    
    def _load_or_create_model(self):
        """Load existing model or create a new one."""
        from .model import MarketAIModel
        
        model_path = self.settings.get('model_path')
        if model_path and Path(model_path).exists():
            return MarketAIModel.load(model_path)
        return MarketAIModel()
    
    def train(self, data: Any, epochs: int = 10) -> Dict[str, Any]:
        """
        Train the AI model with provided data.
        
        Args:
            data: Training data
            epochs: Number of training epochs
            
        Returns:
            Training results and metrics
        """
        with self._lock:
            if self.is_training:
                return {'error': 'Training already in progress'}
            self.is_training = True
        
        try:
            # Check for duplicate data across instances
            data_hash = self._compute_data_hash(data)
            if self.shared_data.is_data_processed(data_hash):
                return {
                    'status': 'skipped',
                    'reason': 'Data already processed by another instance'
                }
            
            # Mark data as being processed
            self.shared_data.mark_data_processing(data_hash, self.instance_id)
            
            # Perform training
            results = self.model.train(data, epochs)
            
            # Share training results with other instances
            self.shared_data.share_training_results({
                'instance_id': self.instance_id,
                'data_hash': data_hash,
                'results': results,
                'timestamp': datetime.now().isoformat()
            })
            
            return results
            
        finally:
            self.is_training = False
            self.shared_data.mark_data_completed(data_hash)
    
    def _compute_data_hash(self, data: Any) -> str:
        """Compute a hash for training data to prevent duplicates."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def predict(self, input_data: Any) -> Dict[str, Any]:
        """
        Make predictions using the trained model.
        
        Args:
            input_data: Input data for prediction
            
        Returns:
            Prediction results
        """
        if self.model is None:
            return {'error': 'Model not initialized'}
        return self.model.predict(input_data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            'instance_id': self.instance_id,
            'is_training': self.is_training,
            'model_loaded': self.model is not None,
            'shared_data_status': self.shared_data.get_status()
        }
    
    def sync_with_instances(self) -> bool:
        """
        Synchronize model and data with other running instances.
        
        Returns:
            True if sync successful
        """
        return self.shared_data.sync_all()
    
    def shutdown(self):
        """Gracefully shutdown the engine."""
        self.shared_data.unregister_instance(self.instance_id)
        if self.model:
            self.model.save(self.settings.get('model_path'))
