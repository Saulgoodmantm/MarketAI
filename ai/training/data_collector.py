"""
Data Collector Module - Collects and stores training data
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from filelock import FileLock


class DataCollector:
    """
    Collects and manages training data for the AI system.
    Supports multi-instance synchronization.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the data collector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.storage_path = Path(self.config.get('storage_path', 'shared_data/training_data'))
        self.batch_size = self.config.get('batch_size', 50)
        self._pending_data: List[Dict] = []
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def add_sample(self, sample: Dict[str, Any]) -> bool:
        """
        Add a training sample to the collection.
        
        Args:
            sample: Training sample data
            
        Returns:
            True if added successfully
        """
        try:
            sample['collected_at'] = datetime.now().isoformat()
            self._pending_data.append(sample)
            
            # Auto-save when batch is full
            if len(self._pending_data) >= self.batch_size:
                self._save_batch()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to add sample: {e}")
            return False
    
    def add_samples(self, samples: List[Dict[str, Any]]) -> int:
        """
        Add multiple training samples.
        
        Args:
            samples: List of training samples
            
        Returns:
            Number of samples added successfully
        """
        added = 0
        for sample in samples:
            if self.add_sample(sample):
                added += 1
        return added
    
    def _save_batch(self):
        """Save pending data as a batch file."""
        if not self._pending_data:
            return
        
        batch_file = self.storage_path / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        lock_file = self.storage_path / ".lock"
        
        with FileLock(str(lock_file)):
            with open(batch_file, 'w') as f:
                json.dump({
                    'samples': self._pending_data,
                    'count': len(self._pending_data),
                    'saved_at': datetime.now().isoformat()
                }, f, indent=2)
        
        self._pending_data = []
    
    def get_pending_data(self) -> Dict[str, Any]:
        """
        Get all pending training data.
        
        Returns:
            Dictionary containing pending samples
        """
        # Load any saved batches
        all_samples = list(self._pending_data)
        
        for batch_file in self.storage_path.glob("batch_*.json"):
            try:
                with open(batch_file, 'r') as f:
                    batch = json.load(f)
                    all_samples.extend(batch.get('samples', []))
            except Exception as e:
                print(f"[WARNING] Failed to load batch {batch_file}: {e}")
        
        return {
            'samples': all_samples,
            'count': len(all_samples)
        }
    
    def clear_processed(self, data_hash: str):
        """Mark data as processed and clear it."""
        processed_file = self.storage_path / "processed.json"
        lock_file = self.storage_path / ".lock"
        
        with FileLock(str(lock_file)):
            processed = {}
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    processed = json.load(f)
            
            processed[data_hash] = datetime.now().isoformat()
            
            with open(processed_file, 'w') as f:
                json.dump(processed, f, indent=2)
    
    def get_status(self) -> Dict[str, Any]:
        """Get collector status."""
        batch_files = list(self.storage_path.glob("batch_*.json"))
        
        return {
            'pending_samples': len(self._pending_data),
            'saved_batches': len(batch_files),
            'storage_path': str(self.storage_path),
            'batch_size': self.batch_size
        }
