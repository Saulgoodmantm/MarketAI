#!/usr/bin/env python3
"""
MarketAI Setup - Installs dependencies and configures the system
Run this first to set up all required dependencies.

To create executable:
    pyinstaller --onefile --name Setup setup.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class SetupManager:
    """Manages MarketAI setup and dependency installation."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.requirements_file = self.base_dir / "requirements.txt"
        self.python_cmd = sys.executable
        
    def print_banner(self):
        """Print setup banner."""
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
║                    SETUP INSTALLER v1.0                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"[ERROR] Python 3.8+ required. Found: {version.major}.{version.minor}")
            return False
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_pip(self) -> bool:
        """Check if pip is available."""
        try:
            result = subprocess.run(
                [self.python_cmd, "-m", "pip", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"[OK] pip is available")
                return True
        except Exception as e:
            print(f"[ERROR] pip check failed: {e}")
        return False
    
    def upgrade_pip(self):
        """Upgrade pip to latest version."""
        print("\n[*] Upgrading pip...")
        subprocess.run(
            [self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True
        )
        print("[OK] pip upgraded")
    
    def install_requirements(self) -> bool:
        """Install requirements from requirements.txt."""
        if not self.requirements_file.exists():
            print(f"[ERROR] requirements.txt not found at {self.requirements_file}")
            return False
        
        print("\n[*] Installing dependencies from requirements.txt...")
        print("[*] This may take several minutes...")
        
        try:
            result = subprocess.run(
                [self.python_cmd, "-m", "pip", "install", "-r", str(self.requirements_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("[OK] All dependencies installed successfully")
                return True
            else:
                print(f"[WARNING] Some dependencies may have failed to install")
                print(f"[*] Errors: {result.stderr[:500] if result.stderr else 'None'}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"[ERROR] Installation failed: {e}")
            return False
    
    def create_directories(self):
        """Create required directories."""
        print("\n[*] Creating required directories...")
        
        directories = [
            "shared_data",
            "shared_data/models",
            "shared_data/training",
            "shared_data/training_data",
            "shared_data/instances",
            "shared_data/errors",
            "profiles",
            "logs"
        ]
        
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  [+] {dir_name}/")
        
        print("[OK] Directories created")
    
    def initialize_config(self):
        """Initialize default configuration."""
        print("\n[*] Initializing configuration...")
        
        config_file = self.base_dir / "shared_data" / "config.json"
        
        if not config_file.exists():
            import json
            
            default_config = {
                "model_path": "shared_data/models/market_ai.model",
                "model_version": "1.0.0",
                "training": {
                    "enabled": True,
                    "auto_train": True,
                    "epochs": 10,
                    "batch_size": 32,
                    "learning_rate": 0.001,
                    "min_samples": 100
                },
                "detection": {
                    "screen": {
                        "enabled": True,
                        "interval": 1.0,
                        "ocr_enabled": True,
                        "object_detection_enabled": True
                    },
                    "web": {
                        "enabled": True,
                        "headless": True,
                        "timeout": 30000
                    }
                },
                "shared_data": {
                    "path": "shared_data",
                    "sync_interval": 60,
                    "max_history": 1000
                },
                "ui": {
                    "theme": "dark",
                    "accent_color": "#00D4FF",
                    "animations": True
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print("[OK] Configuration initialized")
        else:
            print("[OK] Configuration already exists")
    
    def initialize_profiles(self):
        """Initialize default user profiles."""
        print("\n[*] Initializing user profiles...")
        
        profiles_file = self.base_dir / "profiles" / "profiles.json"
        
        if not profiles_file.exists():
            import json
            import hashlib
            from datetime import datetime
            
            def hash_creds(username, password):
                combined = f"{username}:{password}:marketai_salt_v1"
                return hashlib.sha256(combined.encode()).hexdigest()
            
            profiles = {
                "admin": {
                    "id": "admin",
                    "name": "Administrator",
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "auth_hash": hash_creds("admin", "marketai_admin_2024"),
                    "permissions": ["*"]
                },
                "developer": {
                    "id": "developer",
                    "name": "Developer",
                    "role": "developer",
                    "created_at": datetime.now().isoformat(),
                    "auth_hash": hash_creds("developer", "dev_access_key"),
                    "permissions": [
                        "train_model", "view_data", "edit_config",
                        "view_logs", "manage_detection", "export_data", "view_metrics"
                    ]
                },
                "user": {
                    "id": "user",
                    "name": "Default User",
                    "role": "user",
                    "created_at": datetime.now().isoformat(),
                    "auth_hash": hash_creds("user", "user_access"),
                    "permissions": ["view_data", "view_metrics", "run_predictions"]
                }
            }
            
            with open(profiles_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            
            print("[OK] User profiles created:")
            print("     - admin (full access)")
            print("     - developer (development access)")
            print("     - user (basic access)")
        else:
            print("[OK] User profiles already exist")
    
    def verify_installation(self) -> bool:
        """Verify that installation is working."""
        print("\n[*] Verifying installation...")
        
        try:
            # Try importing the main module
            sys.path.insert(0, str(self.base_dir))
            from ai import AIEngine, Settings
            
            # Initialize settings
            settings = Settings()
            
            print("[OK] Core modules imported successfully")
            print("[OK] Settings initialized")
            return True
            
        except ImportError as e:
            print(f"[WARNING] Module import issue: {e}")
            print("[*] Some features may require additional setup")
            return True  # Non-fatal
        except Exception as e:
            print(f"[WARNING] Verification issue: {e}")
            return True
    
    def print_completion(self):
        """Print completion message."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                   SETUP COMPLETE!                            ║
║                                                              ║
║  Next steps:                                                 ║
║                                                              ║
║  For Developers:                                             ║
║    Run: python dev.py                                        ║
║    Or:  Dev.exe (after building)                             ║
║                                                              ║
║  For Users:                                                  ║
║    Run: python user_version.py                               ║
║    Or:  UserVersion.exe (after building)                     ║
║                                                              ║
║  To build executables:                                       ║
║    pip install pyinstaller                                   ║
║    pyinstaller --onefile --name Setup setup.py               ║
║    pyinstaller --onefile --name Dev dev.py                   ║
║    pyinstaller --onefile --name UserVersion user_version.py  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    def run(self):
        """Run the setup process."""
        self.print_banner()
        
        print(f"\n[*] System: {platform.system()} {platform.release()}")
        print(f"[*] Architecture: {platform.machine()}")
        print(f"[*] Base Directory: {self.base_dir}\n")
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        if not self.check_pip():
            return False
        
        # Upgrade pip
        self.upgrade_pip()
        
        # Install dependencies
        self.install_requirements()
        
        # Create directories
        self.create_directories()
        
        # Initialize configuration
        self.initialize_config()
        
        # Initialize profiles
        self.initialize_profiles()
        
        # Verify installation
        self.verify_installation()
        
        # Print completion
        self.print_completion()
        
        return True


def main():
    """Main entry point."""
    setup = SetupManager()
    success = setup.run()
    
    if not success:
        print("\n[!] Setup encountered errors. Please review the output above.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
