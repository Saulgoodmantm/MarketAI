"""
Authentication Module - Manages user profiles and permissions
"""

import os
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class Profile:
    """User profile with permissions."""
    id: str
    name: str
    role: str  # 'admin', 'developer', 'user'
    created_at: str
    last_login: Optional[str] = None
    permissions: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = self._default_permissions()
    
    def _default_permissions(self) -> List[str]:
        """Get default permissions based on role."""
        permissions_map = {
            'admin': ['*'],  # All permissions
            'developer': [
                'train_model',
                'view_data',
                'edit_config',
                'view_logs',
                'manage_detection',
                'export_data',
                'view_metrics'
            ],
            'user': [
                'view_data',
                'view_metrics',
                'run_predictions'
            ]
        }
        return permissions_map.get(self.role, [])
    
    def has_permission(self, permission: str) -> bool:
        """Check if profile has a specific permission."""
        if '*' in self.permissions:
            return True
        return permission in self.permissions


class AuthManager:
    """
    Manages authentication and authorization for MarketAI.
    Supports multiple profiles with role-based access.
    """
    
    PROFILES_PATH = Path("profiles")
    
    def __init__(self, profiles_path: Optional[str] = None):
        """
        Initialize auth manager.
        
        Args:
            profiles_path: Path to profiles directory
        """
        self.profiles_path = Path(profiles_path) if profiles_path else self.PROFILES_PATH
        self.profiles_path.mkdir(parents=True, exist_ok=True)
        self._current_profile: Optional[Profile] = None
        self._session_token: Optional[str] = None
        
        # Ensure default admin profile exists
        self._ensure_default_profiles()
    
    def _ensure_default_profiles(self):
        """Create default profiles if none exist."""
        profiles_file = self.profiles_path / "profiles.json"
        
        if not profiles_file.exists():
            # Create default profiles
            default_profiles = {
                'admin': {
                    'id': 'admin',
                    'name': 'Administrator',
                    'role': 'admin',
                    'created_at': datetime.now().isoformat(),
                    'auth_hash': self._hash_credentials('admin', 'marketai_admin_2024'),
                    'permissions': ['*']
                },
                'developer': {
                    'id': 'developer',
                    'name': 'Developer',
                    'role': 'developer',
                    'created_at': datetime.now().isoformat(),
                    'auth_hash': self._hash_credentials('developer', 'dev_access_key'),
                    'permissions': [
                        'train_model', 'view_data', 'edit_config',
                        'view_logs', 'manage_detection', 'export_data', 'view_metrics'
                    ]
                }
            }
            
            with open(profiles_file, 'w') as f:
                json.dump(default_profiles, f, indent=2)
    
    def _hash_credentials(self, username: str, password: str) -> str:
        """Hash credentials for secure storage."""
        combined = f"{username}:{password}:marketai_salt_v1"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load all profiles from storage."""
        profiles_file = self.profiles_path / "profiles.json"
        
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_profiles(self, profiles: Dict[str, Any]):
        """Save profiles to storage."""
        profiles_file = self.profiles_path / "profiles.json"
        
        with open(profiles_file, 'w') as f:
            json.dump(profiles, f, indent=2)
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session token if successful, None otherwise
        """
        profiles = self._load_profiles()
        auth_hash = self._hash_credentials(username, password)
        
        for profile_id, profile_data in profiles.items():
            if profile_data.get('auth_hash') == auth_hash:
                # Create session
                self._session_token = secrets.token_hex(32)
                self._current_profile = Profile(
                    id=profile_data['id'],
                    name=profile_data['name'],
                    role=profile_data['role'],
                    created_at=profile_data['created_at'],
                    permissions=profile_data.get('permissions')
                )
                
                # Update last login
                profile_data['last_login'] = datetime.now().isoformat()
                self._save_profiles(profiles)
                
                return self._session_token
        
        return None
    
    def logout(self):
        """Log out current session."""
        self._current_profile = None
        self._session_token = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._current_profile is not None
    
    def get_current_profile(self) -> Optional[Profile]:
        """Get current authenticated profile."""
        return self._current_profile
    
    def check_permission(self, permission: str) -> bool:
        """
        Check if current user has permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if permitted
        """
        if not self._current_profile:
            return False
        return self._current_profile.has_permission(permission)
    
    def create_profile(self, username: str, password: str, name: str, role: str) -> bool:
        """
        Create a new profile.
        
        Args:
            username: Username for the profile
            password: Password for the profile
            name: Display name
            role: Role ('admin', 'developer', 'user')
            
        Returns:
            True if created successfully
        """
        if not self.check_permission('*'):  # Only admins can create profiles
            return False
        
        profiles = self._load_profiles()
        
        if username in profiles:
            return False  # Profile already exists
        
        profiles[username] = {
            'id': username,
            'name': name,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'auth_hash': self._hash_credentials(username, password),
            'permissions': Profile(
                id=username,
                name=name,
                role=role,
                created_at=datetime.now().isoformat()
            ).permissions
        }
        
        self._save_profiles(profiles)
        return True
    
    def delete_profile(self, username: str) -> bool:
        """Delete a profile."""
        if not self.check_permission('*'):
            return False
        
        profiles = self._load_profiles()
        
        if username not in profiles:
            return False
        
        if username == 'admin':
            return False  # Cannot delete primary admin
        
        del profiles[username]
        self._save_profiles(profiles)
        return True
    
    def update_profile_permissions(self, username: str, permissions: List[str]) -> bool:
        """Update profile permissions."""
        if not self.check_permission('*'):
            return False
        
        profiles = self._load_profiles()
        
        if username not in profiles:
            return False
        
        profiles[username]['permissions'] = permissions
        self._save_profiles(profiles)
        return True
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles (without sensitive data)."""
        profiles = self._load_profiles()
        
        return [
            {
                'id': p['id'],
                'name': p['name'],
                'role': p['role'],
                'created_at': p['created_at'],
                'last_login': p.get('last_login')
            }
            for p in profiles.values()
        ]
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change password for a profile."""
        profiles = self._load_profiles()
        
        if username not in profiles:
            return False
        
        old_hash = self._hash_credentials(username, old_password)
        if profiles[username].get('auth_hash') != old_hash:
            return False
        
        profiles[username]['auth_hash'] = self._hash_credentials(username, new_password)
        self._save_profiles(profiles)
        return True
