#!/usr/bin/env python3
"""
MarketAI Developer Version - Full access with authentication
Provides developer tools for training, configuration, and monitoring.

To create executable:
    pyinstaller --onefile --name Dev dev.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.absolute()))


class DevConsole:
    """Developer console for MarketAI."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.auth_manager = None
        self.engine = None
        self.trainer = None
        self.is_authenticated = False
        
    def print_banner(self):
        """Print developer console banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗    ║
║     ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝    ║
║     ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║       ║
║     ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║       ║
║     ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║       ║
║     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝       ║
║                        A I                                   ║
║                                                              ║
║              DEVELOPER CONSOLE v1.0                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def authenticate(self) -> bool:
        """Authenticate developer."""
        print("\n[*] Developer Authentication Required")
        print("[*] Contact administrator for credentials\n")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                
                # Import auth manager
                from ai.utils.auth import AuthManager
                self.auth_manager = AuthManager()
                
                token = self.auth_manager.authenticate(username, password)
                
                if token:
                    profile = self.auth_manager.get_current_profile()
                    if profile.role in ['admin', 'developer']:
                        print(f"\n[OK] Authenticated as {profile.name} ({profile.role})")
                        self.is_authenticated = True
                        return True
                    else:
                        print("[ERROR] Developer or admin access required")
                        self.auth_manager.logout()
                else:
                    print(f"[ERROR] Authentication failed ({max_attempts - attempt - 1} attempts remaining)")
                    
            except ImportError:
                print("[WARNING] Auth module not available, using fallback")
                # Fallback authentication
                if self._fallback_auth(username, password):
                    self.is_authenticated = True
                    return True
            except Exception as e:
                print(f"[ERROR] {e}")
        
        return False
    
    def _fallback_auth(self, username: str, password: str) -> bool:
        """Fallback authentication when module not available."""
        import hashlib
        
        profiles_file = self.base_dir / "profiles" / "profiles.json"
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles = json.load(f)
            
            combined = f"{username}:{password}:marketai_salt_v1"
            auth_hash = hashlib.sha256(combined.encode()).hexdigest()
            
            for profile_id, profile in profiles.items():
                if profile.get('auth_hash') == auth_hash:
                    if profile.get('role') in ['admin', 'developer']:
                        print(f"\n[OK] Authenticated as {profile.get('name')} ({profile.get('role')})")
                        return True
        
        return False
    
    def initialize_engine(self):
        """Initialize the AI engine."""
        print("\n[*] Initializing AI Engine...")
        
        try:
            from ai import AIEngine, SelfTrainer
            
            self.engine = AIEngine()
            if self.engine.initialize():
                print(f"[OK] Engine initialized (Instance: {self.engine.instance_id[:8]}...)")
                
                self.trainer = SelfTrainer(self.engine)
                print("[OK] Self-trainer ready")
            else:
                print("[WARNING] Engine initialization incomplete")
                
        except ImportError as e:
            print(f"[WARNING] Could not import AI modules: {e}")
            print("[*] Some features may be limited")
    
    def show_menu(self):
        """Show main menu."""
        menu = """
╔══════════════════════════════════════════════════════════════╗
║                    DEVELOPER MENU                            ║
╠══════════════════════════════════════════════════════════════╣
║  [1] Start AI Training                                       ║
║  [2] Start Auto-Training Mode                                ║
║  [3] View System Status                                      ║
║  [4] Manage Detection (Screen/Web)                           ║
║  [5] View/Edit Configuration                                 ║
║  [6] Manage User Profiles                                    ║
║  [7] View Training History                                   ║
║  [8] View Error Logs                                         ║
║  [9] Sync with Other Instances                               ║
║  [10] Export Data                                            ║
║  [0] Exit                                                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(menu)
    
    def start_training(self):
        """Start manual training session."""
        print("\n[*] Manual Training Mode")
        print("=" * 50)
        
        if not self.engine:
            print("[ERROR] Engine not initialized")
            return
        
        try:
            epochs = input("Number of epochs (default 10): ").strip()
            epochs = int(epochs) if epochs else 10
            
            print(f"\n[*] Starting training for {epochs} epochs...")
            
            # Create sample training data
            sample_data = {
                'samples': [
                    {'type': 'market_data', 'value': i, 'timestamp': datetime.now().isoformat()}
                    for i in range(100)
                ]
            }
            
            results = self.engine.train(sample_data, epochs=epochs)
            
            print("\n[*] Training Results:")
            print(json.dumps(results, indent=2, default=str))
            
        except Exception as e:
            print(f"[ERROR] Training failed: {e}")
    
    def start_auto_training(self):
        """Start autonomous training mode."""
        print("\n[*] Autonomous Training Mode")
        print("=" * 50)
        
        if not self.trainer:
            print("[ERROR] Trainer not initialized")
            return
        
        print("[*] Starting auto-training...")
        print("[*] Press Ctrl+C to stop\n")
        
        try:
            self.trainer.start()
            
            while self.trainer.is_running:
                status = self.trainer.get_status()
                print(f"\r[*] Status: Running | Data collected: Processing...", end='', flush=True)
                import time
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n[*] Stopping auto-training...")
            self.trainer.stop()
            print("[OK] Auto-training stopped")
    
    def view_status(self):
        """View system status."""
        print("\n[*] System Status")
        print("=" * 50)
        
        if self.engine:
            status = self.engine.get_status()
            print(f"\nInstance ID: {status.get('instance_id', 'N/A')[:16]}...")
            print(f"Is Training: {status.get('is_training', False)}")
            print(f"Model Loaded: {status.get('model_loaded', False)}")
            
            shared_status = status.get('shared_data_status', {})
            print(f"\nShared Data Path: {shared_status.get('shared_path', 'N/A')}")
            print(f"Active Instances: {shared_status.get('active_instances', 0)}")
            print(f"Error Count: {shared_status.get('errors_count', 0)}")
        else:
            print("[WARNING] Engine not initialized")
        
        # Show system info
        import platform
        print(f"\nSystem: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
    
    def manage_detection(self):
        """Manage screen and web detection."""
        print("\n[*] Detection Management")
        print("=" * 50)
        
        submenu = """
        [1] Start Screen Detection
        [2] Stop Screen Detection
        [3] Start Web Detection
        [4] Stop Web Detection
        [5] Add URL to Monitor
        [6] View Detection Status
        [0] Back
        """
        print(submenu)
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            if self.trainer and self.trainer.screen_detector:
                self.trainer.screen_detector.start()
                print("[OK] Screen detection started")
        elif choice == '2':
            if self.trainer and self.trainer.screen_detector:
                self.trainer.screen_detector.stop()
                print("[OK] Screen detection stopped")
        elif choice == '3':
            if self.trainer and self.trainer.web_detector:
                self.trainer.web_detector.start()
                print("[OK] Web detection started")
        elif choice == '4':
            if self.trainer and self.trainer.web_detector:
                self.trainer.web_detector.stop()
                print("[OK] Web detection stopped")
        elif choice == '5':
            url = input("Enter URL: ").strip()
            if url and self.trainer and self.trainer.web_detector:
                self.trainer.web_detector.add_target_url(url)
                print(f"[OK] Added: {url}")
        elif choice == '6':
            if self.trainer:
                print("\nScreen Detector:", self.trainer.screen_detector.get_status())
                print("Web Detector:", self.trainer.web_detector.get_status())
    
    def manage_config(self):
        """View and edit configuration."""
        print("\n[*] Configuration Management")
        print("=" * 50)
        
        config_file = self.base_dir / "shared_data" / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("\nCurrent Configuration:")
            print(json.dumps(config, indent=2))
            
            edit = input("\nEdit configuration? (y/n): ").strip().lower()
            if edit == 'y':
                key = input("Setting key (e.g., training.epochs): ").strip()
                value = input("New value: ").strip()
                
                # Parse value
                try:
                    value = json.loads(value)
                except:
                    pass  # Keep as string
                
                # Update config
                keys = key.split('.')
                target = config
                for k in keys[:-1]:
                    target = target.setdefault(k, {})
                target[keys[-1]] = value
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("[OK] Configuration updated")
        else:
            print("[WARNING] Configuration file not found")
    
    def manage_profiles(self):
        """Manage user profiles."""
        print("\n[*] Profile Management")
        print("=" * 50)
        
        profiles_file = self.base_dir / "profiles" / "profiles.json"
        
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles = json.load(f)
            
            print("\nExisting Profiles:")
            for pid, profile in profiles.items():
                print(f"  - {pid}: {profile.get('name')} ({profile.get('role')})")
            
            submenu = """
            [1] Create New Profile
            [2] Delete Profile
            [3] Update Permissions
            [0] Back
            """
            print(submenu)
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                name = input("Display name: ").strip()
                role = input("Role (admin/developer/user): ").strip()
                
                if username and password and name and role:
                    import hashlib
                    combined = f"{username}:{password}:marketai_salt_v1"
                    auth_hash = hashlib.sha256(combined.encode()).hexdigest()
                    
                    profiles[username] = {
                        'id': username,
                        'name': name,
                        'role': role,
                        'created_at': datetime.now().isoformat(),
                        'auth_hash': auth_hash,
                        'permissions': self._get_default_permissions(role)
                    }
                    
                    with open(profiles_file, 'w') as f:
                        json.dump(profiles, f, indent=2)
                    
                    print(f"[OK] Profile '{username}' created")
                    
            elif choice == '2':
                username = input("Username to delete: ").strip()
                if username in profiles and username != 'admin':
                    del profiles[username]
                    with open(profiles_file, 'w') as f:
                        json.dump(profiles, f, indent=2)
                    print(f"[OK] Profile '{username}' deleted")
                else:
                    print("[ERROR] Cannot delete this profile")
    
    def _get_default_permissions(self, role: str) -> list:
        """Get default permissions for a role."""
        permissions_map = {
            'admin': ['*'],
            'developer': [
                'train_model', 'view_data', 'edit_config',
                'view_logs', 'manage_detection', 'export_data', 'view_metrics'
            ],
            'user': ['view_data', 'view_metrics', 'run_predictions']
        }
        return permissions_map.get(role, [])
    
    def view_training_history(self):
        """View training history."""
        print("\n[*] Training History")
        print("=" * 50)
        
        results_file = self.base_dir / "shared_data" / "training" / "results.json"
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            print(f"\nTotal training sessions: {len(results)}")
            
            for i, result in enumerate(results[-10:]):  # Last 10
                print(f"\n[{i+1}] Instance: {result.get('instance_id', 'N/A')[:8]}...")
                print(f"    Timestamp: {result.get('timestamp', 'N/A')}")
                if 'results' in result:
                    print(f"    Status: {result['results'].get('status', 'N/A')}")
        else:
            print("[*] No training history available")
    
    def view_errors(self):
        """View error logs."""
        print("\n[*] Error Logs")
        print("=" * 50)
        
        errors_file = self.base_dir / "shared_data" / "errors" / "log.json"
        
        if errors_file.exists():
            with open(errors_file, 'r') as f:
                errors = json.load(f)
            
            print(f"\nTotal errors: {len(errors)}")
            
            for error in errors[-10:]:  # Last 10
                print(f"\n[{error.get('timestamp', 'N/A')}]")
                print(f"  Instance: {error.get('instance_id', 'N/A')[:8]}...")
                print(f"  Error: {error.get('error', 'N/A')}")
        else:
            print("[*] No errors logged")
    
    def sync_instances(self):
        """Sync with other instances."""
        print("\n[*] Synchronizing with other instances...")
        
        if self.engine:
            if self.engine.sync_with_instances():
                print("[OK] Synchronization complete")
                
                # Show active instances
                instances = self.engine.shared_data.get_active_instances()
                print(f"\nActive instances: {len(instances)}")
                for inst in instances:
                    print(f"  - {inst.get('instance_id', 'N/A')[:8]}... ({inst.get('status', 'unknown')})")
            else:
                print("[ERROR] Synchronization failed")
        else:
            print("[ERROR] Engine not initialized")
    
    def export_data(self):
        """Export training data."""
        print("\n[*] Export Data")
        print("=" * 50)
        
        export_path = self.base_dir / "exports"
        export_path.mkdir(exist_ok=True)
        
        export_file = export_path / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'training_results': [],
            'errors': [],
            'config': {}
        }
        
        # Gather data
        results_file = self.base_dir / "shared_data" / "training" / "results.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                export_data['training_results'] = json.load(f)
        
        errors_file = self.base_dir / "shared_data" / "errors" / "log.json"
        if errors_file.exists():
            with open(errors_file, 'r') as f:
                export_data['errors'] = json.load(f)
        
        config_file = self.base_dir / "shared_data" / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                export_data['config'] = json.load(f)
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"[OK] Data exported to: {export_file}")
    
    def run(self):
        """Run the developer console."""
        self.print_banner()
        
        # Authenticate
        if not self.authenticate():
            print("\n[ERROR] Authentication failed. Exiting.")
            input("\nPress Enter to exit...")
            return
        
        # Initialize engine
        self.initialize_engine()
        
        # Main loop
        while True:
            self.show_menu()
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.start_training()
            elif choice == '2':
                self.start_auto_training()
            elif choice == '3':
                self.view_status()
            elif choice == '4':
                self.manage_detection()
            elif choice == '5':
                self.manage_config()
            elif choice == '6':
                self.manage_profiles()
            elif choice == '7':
                self.view_training_history()
            elif choice == '8':
                self.view_errors()
            elif choice == '9':
                self.sync_instances()
            elif choice == '10':
                self.export_data()
            elif choice == '0':
                print("\n[*] Shutting down...")
                if self.engine:
                    self.engine.shutdown()
                break
            else:
                print("[!] Invalid choice")
            
            input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    console = DevConsole()
    console.run()


if __name__ == "__main__":
    main()
