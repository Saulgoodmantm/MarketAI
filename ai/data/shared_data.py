"""
Shared Data Manager - Manages data synchronization across AI instances
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from filelock import FileLock


class SharedDataManager:
    """
    Manages shared data across multiple AI instances.
    Prevents duplicate training and synchronizes model updates.
    """
    
    # Class-level shared path
    SHARED_DATA_PATH = Path("shared_data")
    
    def __init__(self, instance_id: str, shared_path: Optional[str] = None):
        """
        Initialize the shared data manager.
        
        Args:
            instance_id: Unique identifier for this instance
            shared_path: Path to shared data directory
        """
        self.instance_id = instance_id
        self.shared_path = Path(shared_path) if shared_path else self.SHARED_DATA_PATH
        
        # Create shared directories
        self.shared_path.mkdir(parents=True, exist_ok=True)
        (self.shared_path / "instances").mkdir(exist_ok=True)
        (self.shared_path / "training").mkdir(exist_ok=True)
        (self.shared_path / "models").mkdir(exist_ok=True)
        (self.shared_path / "errors").mkdir(exist_ok=True)
        
        # Lock file for coordination
        self._lock_file = self.shared_path / ".lock"
        
    def _get_lock(self) -> FileLock:
        """Get file lock for synchronized operations."""
        return FileLock(str(self._lock_file), timeout=30)
    
    def register_instance(self, info: Dict[str, Any]) -> bool:
        """
        Register this instance in the shared registry.
        
        Args:
            info: Instance information
            
        Returns:
            True if registration successful
        """
        try:
            with self._get_lock():
                instances_file = self.shared_path / "instances" / "registry.json"
                
                registry = {}
                if instances_file.exists():
                    with open(instances_file, 'r') as f:
                        registry = json.load(f)
                
                registry[self.instance_id] = {
                    **info,
                    'registered_at': datetime.now().isoformat(),
                    'last_heartbeat': datetime.now().isoformat()
                }
                
                with open(instances_file, 'w') as f:
                    json.dump(registry, f, indent=2)
                
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to register instance: {e}")
            return False
    
    def unregister_instance(self, instance_id: str):
        """Remove an instance from the registry."""
        try:
            with self._get_lock():
                instances_file = self.shared_path / "instances" / "registry.json"
                
                if instances_file.exists():
                    with open(instances_file, 'r') as f:
                        registry = json.load(f)
                    
                    if instance_id in registry:
                        del registry[instance_id]
                        
                        with open(instances_file, 'w') as f:
                            json.dump(registry, f, indent=2)
                            
        except Exception as e:
            print(f"[ERROR] Failed to unregister instance: {e}")
    
    def update_instance_status(self, instance_id: str, status: str):
        """Update instance status."""
        try:
            with self._get_lock():
                instances_file = self.shared_path / "instances" / "registry.json"
                
                if instances_file.exists():
                    with open(instances_file, 'r') as f:
                        registry = json.load(f)
                    
                    if instance_id in registry:
                        registry[instance_id]['status'] = status
                        registry[instance_id]['last_heartbeat'] = datetime.now().isoformat()
                        
                        with open(instances_file, 'w') as f:
                            json.dump(registry, f, indent=2)
                            
        except Exception as e:
            print(f"[ERROR] Failed to update instance status: {e}")
    
    def get_active_instances(self) -> List[Dict[str, Any]]:
        """Get list of all active instances."""
        try:
            instances_file = self.shared_path / "instances" / "registry.json"
            
            if instances_file.exists():
                with open(instances_file, 'r') as f:
                    registry = json.load(f)
                return list(registry.values())
            
            return []
            
        except Exception as e:
            print(f"[ERROR] Failed to get active instances: {e}")
            return []
    
    def is_data_processed(self, data_hash: str) -> bool:
        """
        Check if data has already been processed by any instance.
        
        Args:
            data_hash: Hash of the training data
            
        Returns:
            True if data has been processed
        """
        try:
            processed_file = self.shared_path / "training" / "processed.json"
            
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    processed = json.load(f)
                return data_hash in processed
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to check processed data: {e}")
            return False
    
    def mark_data_processing(self, data_hash: str, instance_id: str):
        """Mark data as being processed by an instance."""
        try:
            with self._get_lock():
                processing_file = self.shared_path / "training" / "processing.json"
                
                processing = {}
                if processing_file.exists():
                    with open(processing_file, 'r') as f:
                        processing = json.load(f)
                
                processing[data_hash] = {
                    'instance_id': instance_id,
                    'started_at': datetime.now().isoformat()
                }
                
                with open(processing_file, 'w') as f:
                    json.dump(processing, f, indent=2)
                    
        except Exception as e:
            print(f"[ERROR] Failed to mark data processing: {e}")
    
    def mark_data_completed(self, data_hash: str):
        """Mark data processing as completed."""
        try:
            with self._get_lock():
                # Add to processed
                processed_file = self.shared_path / "training" / "processed.json"
                
                processed = {}
                if processed_file.exists():
                    with open(processed_file, 'r') as f:
                        processed = json.load(f)
                
                processed[data_hash] = {
                    'completed_at': datetime.now().isoformat()
                }
                
                with open(processed_file, 'w') as f:
                    json.dump(processed, f, indent=2)
                
                # Remove from processing
                processing_file = self.shared_path / "training" / "processing.json"
                if processing_file.exists():
                    with open(processing_file, 'r') as f:
                        processing = json.load(f)
                    
                    if data_hash in processing:
                        del processing[data_hash]
                        
                        with open(processing_file, 'w') as f:
                            json.dump(processing, f, indent=2)
                            
        except Exception as e:
            print(f"[ERROR] Failed to mark data completed: {e}")
    
    def share_training_results(self, results: Dict[str, Any]):
        """Share training results with other instances."""
        try:
            with self._get_lock():
                results_file = self.shared_path / "training" / "results.json"
                
                all_results = []
                if results_file.exists():
                    with open(results_file, 'r') as f:
                        all_results = json.load(f)
                
                all_results.append(results)
                
                # Keep only last 1000 results
                all_results = all_results[-1000:]
                
                with open(results_file, 'w') as f:
                    json.dump(all_results, f, indent=2)
                    
        except Exception as e:
            print(f"[ERROR] Failed to share training results: {e}")
    
    def get_training_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent training results from all instances."""
        try:
            results_file = self.shared_path / "training" / "results.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    all_results = json.load(f)
                return all_results[-limit:]
            
            return []
            
        except Exception as e:
            print(f"[ERROR] Failed to get training results: {e}")
            return []
    
    def log_error(self, error_info: Dict[str, Any]):
        """Log an error to shared storage."""
        try:
            with self._get_lock():
                errors_file = self.shared_path / "errors" / "log.json"
                
                errors = []
                if errors_file.exists():
                    with open(errors_file, 'r') as f:
                        errors = json.load(f)
                
                error_info['instance_id'] = self.instance_id
                error_info['timestamp'] = datetime.now().isoformat()
                errors.append(error_info)
                
                # Keep only last 500 errors
                errors = errors[-500:]
                
                with open(errors_file, 'w') as f:
                    json.dump(errors, f, indent=2)
                    
        except Exception as e:
            print(f"[ERROR] Failed to log error: {e}")
    
    def get_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors from all instances."""
        try:
            errors_file = self.shared_path / "errors" / "log.json"
            
            if errors_file.exists():
                with open(errors_file, 'r') as f:
                    errors = json.load(f)
                return errors[-limit:]
            
            return []
            
        except Exception as e:
            print(f"[ERROR] Failed to get errors: {e}")
            return []
    
    def is_error_known(self, error_hash: str) -> bool:
        """Check if an error has already been logged."""
        try:
            known_errors_file = self.shared_path / "errors" / "known.json"
            
            if known_errors_file.exists():
                with open(known_errors_file, 'r') as f:
                    known = json.load(f)
                return error_hash in known
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to check known errors: {e}")
            return False
    
    def mark_error_known(self, error_hash: str, error_info: Dict[str, Any]):
        """Mark an error as known to prevent duplicate handling."""
        try:
            with self._get_lock():
                known_errors_file = self.shared_path / "errors" / "known.json"
                
                known = {}
                if known_errors_file.exists():
                    with open(known_errors_file, 'r') as f:
                        known = json.load(f)
                
                known[error_hash] = {
                    **error_info,
                    'first_seen': datetime.now().isoformat()
                }
                
                with open(known_errors_file, 'w') as f:
                    json.dump(known, f, indent=2)
                    
        except Exception as e:
            print(f"[ERROR] Failed to mark error as known: {e}")
    
    def sync_all(self) -> bool:
        """Synchronize all data with shared storage."""
        try:
            # Update heartbeat
            self.update_instance_status(self.instance_id, 'syncing')
            
            # Clean up stale instances (no heartbeat in 5 minutes)
            self._cleanup_stale_instances()
            
            self.update_instance_status(self.instance_id, 'ready')
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to sync: {e}")
            return False
    
    def _cleanup_stale_instances(self):
        """Remove instances that haven't sent heartbeat recently."""
        try:
            from datetime import datetime, timedelta
            
            with self._get_lock():
                instances_file = self.shared_path / "instances" / "registry.json"
                
                if instances_file.exists():
                    with open(instances_file, 'r') as f:
                        registry = json.load(f)
                    
                    stale_threshold = datetime.now() - timedelta(minutes=5)
                    to_remove = []
                    
                    for instance_id, info in registry.items():
                        last_heartbeat = datetime.fromisoformat(info.get('last_heartbeat', '2000-01-01'))
                        if last_heartbeat < stale_threshold:
                            to_remove.append(instance_id)
                    
                    for instance_id in to_remove:
                        del registry[instance_id]
                    
                    if to_remove:
                        with open(instances_file, 'w') as f:
                            json.dump(registry, f, indent=2)
                            
        except Exception as e:
            print(f"[ERROR] Failed to cleanup stale instances: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get shared data manager status."""
        return {
            'instance_id': self.instance_id,
            'shared_path': str(self.shared_path),
            'active_instances': len(self.get_active_instances()),
            'errors_count': len(self.get_errors())
        }
