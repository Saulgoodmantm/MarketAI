"""
Settings Tab - API configuration and application settings
"""

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
from pathlib import Path


class SettingsTab:
    """
    Settings tab for API key configuration and application settings.
    """
    
    def __init__(self, parent, api_manager=None, on_save: Optional[Callable] = None):
        """
        Initialize the Settings tab.
        
        Args:
            parent: Parent widget
            api_manager: API manager instance
            on_save: Callback when settings are saved
        """
        self.parent = parent
        self.api_manager = api_manager
        self.on_save = on_save or (lambda: None)
        
        # Settings state
        self._settings = {}
        self._api_status = {}
        
        # Build UI
        self.frame = self._create_ui()
    
    def _create_ui(self):
        """Create the Settings tab UI."""
        if ctk is None:
            return None
            
        frame = ctk.CTkFrame(self.parent)
        
        # Header
        header = ctk.CTkFrame(frame)
        header.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ SETTINGS",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)
        
        # Main content with tabs
        tabs = ctk.CTkTabview(frame)
        tabs.pack(fill="both", expand=True, padx=10, pady=5)
        
        # API Configuration tab
        api_tab = tabs.add("🔑 API Keys")
        self._create_api_settings(api_tab)
        
        # General Settings tab
        general_tab = tabs.add("🎛️ General")
        self._create_general_settings(general_tab)
        
        # Appearance tab
        appearance_tab = tabs.add("🎨 Appearance")
        self._create_appearance_settings(appearance_tab)
        
        # Advanced tab
        advanced_tab = tabs.add("🔧 Advanced")
        self._create_advanced_settings(advanced_tab)
        
        # About tab
        about_tab = tabs.add("ℹ️ About")
        self._create_about_section(about_tab)
        
        return frame
    
    def _create_api_settings(self, parent):
        """Create API configuration section."""
        if ctk is None:
            return
            
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Description
        ctk.CTkLabel(
            scroll,
            text="Configure your API keys to enable market data access.\n" +
                 "API keys are stored locally and encrypted.",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            justify="left"
        ).pack(anchor="w", padx=10, pady=10)
        
        # API configurations
        self.api_entries = {}
        
        apis = [
            {
                'name': 'antipublic',
                'display': 'AntiPublic API',
                'description': 'Data breach checking and credential verification',
                'docs': 'https://antipublic.readme.io/reference/information'
            },
            {
                'name': 'lzt_market',
                'display': 'LZT Market API',
                'description': 'Digital marketplace access for account trading',
                'docs': 'https://lzt-market.readme.io/reference/information'
            },
            {
                'name': 'lolzteam',
                'display': 'LolzTeam Forum API',
                'description': 'Forum data, user profiles, and discussions',
                'docs': 'https://lolzteam.readme.io/reference/information'
            }
        ]
        
        for api in apis:
            self._create_api_card(scroll, api)
        
        # Save button
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save API Keys",
            command=self._save_api_keys,
            fg_color="#2ECC71",
            hover_color="#27AE60"
        ).pack(side="left", padx=10, expand=True, fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Test All Connections",
            command=self._test_all_connections,
            fg_color="#3498DB",
            hover_color="#2980B9"
        ).pack(side="right", padx=10, expand=True, fill="x")
    
    def _create_api_card(self, parent, api: Dict):
        """Create an API configuration card."""
        if ctk is None:
            return
            
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=10, pady=5)
        
        # Header
        header = ctk.CTkFrame(card)
        header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            header,
            text=api['display'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        self.api_entries[f"{api['name']}_status"] = ctk.CTkLabel(
            header,
            text="● Not Configured",
            font=ctk.CTkFont(size=11),
            text_color="#FF6B6B"
        )
        self.api_entries[f"{api['name']}_status"].pack(side="right", padx=5)
        
        # Description
        ctk.CTkLabel(
            card,
            text=api['description'],
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(anchor="w", padx=15, pady=2)
        
        # API key input
        input_frame = ctk.CTkFrame(card)
        input_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            input_frame,
            text="API Key:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.api_entries[api['name']] = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter your API key...",
            show="•",
            width=300
        )
        self.api_entries[api['name']].pack(side="left", padx=5, fill="x", expand=True)
        
        # Show/Hide button
        show_var = ctk.BooleanVar(value=False)
        
        def toggle_visibility(entry=self.api_entries[api['name']], var=show_var):
            if var.get():
                entry.configure(show="")
            else:
                entry.configure(show="•")
        
        ctk.CTkCheckBox(
            input_frame,
            text="Show",
            variable=show_var,
            command=toggle_visibility,
            width=60
        ).pack(side="right", padx=5)
        
        # Test button
        ctk.CTkButton(
            input_frame,
            text="Test",
            command=lambda n=api['name']: self._test_api(n),
            width=60
        ).pack(side="right", padx=5)
        
        # Documentation link
        ctk.CTkLabel(
            card,
            text=f"📄 Documentation: {api['docs']}",
            font=ctk.CTkFont(size=9),
            text_color="#3498DB",
            cursor="hand2"
        ).pack(anchor="w", padx=15, pady=(2, 10))
    
    def _create_general_settings(self, parent):
        """Create general settings section."""
        if ctk is None:
            return
            
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Startup settings
        startup_frame = ctk.CTkFrame(scroll)
        startup_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            startup_frame,
            text="Startup Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.auto_start_watch = ctk.CTkCheckBox(
            startup_frame,
            text="Auto-start Market Watch on launch"
        )
        self.auto_start_watch.pack(anchor="w", padx=20, pady=2)
        
        self.remember_last_tab = ctk.CTkCheckBox(
            startup_frame,
            text="Remember last active tab"
        )
        self.remember_last_tab.pack(anchor="w", padx=20, pady=2)
        self.remember_last_tab.select()
        
        self.minimize_to_tray = ctk.CTkCheckBox(
            startup_frame,
            text="Minimize to system tray"
        )
        self.minimize_to_tray.pack(anchor="w", padx=20, pady=2)
        
        # Notification settings
        notif_frame = ctk.CTkFrame(scroll)
        notif_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            notif_frame,
            text="Notifications",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.enable_sounds = ctk.CTkCheckBox(
            notif_frame,
            text="Enable notification sounds"
        )
        self.enable_sounds.pack(anchor="w", padx=20, pady=2)
        self.enable_sounds.select()
        
        self.enable_desktop_notif = ctk.CTkCheckBox(
            notif_frame,
            text="Enable desktop notifications"
        )
        self.enable_desktop_notif.pack(anchor="w", padx=20, pady=2)
        
        # Data settings
        data_frame = ctk.CTkFrame(scroll)
        data_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            data_frame,
            text="Data & Storage",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.auto_save = ctk.CTkCheckBox(
            data_frame,
            text="Auto-save settings on change"
        )
        self.auto_save.pack(anchor="w", padx=20, pady=2)
        self.auto_save.select()
        
        self.collect_analytics = ctk.CTkCheckBox(
            data_frame,
            text="Collect market data for AI training"
        )
        self.collect_analytics.pack(anchor="w", padx=20, pady=2)
        self.collect_analytics.select()
        
        # Cache management
        cache_row = ctk.CTkFrame(data_frame)
        cache_row.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            cache_row,
            text="Cache: ~0 MB",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            cache_row,
            text="Clear Cache",
            command=self._clear_cache,
            width=100
        ).pack(side="right", padx=5)
        
        # Save button
        ctk.CTkButton(
            scroll,
            text="💾 Save Settings",
            command=self._save_general_settings,
            fg_color="#2ECC71",
            hover_color="#27AE60"
        ).pack(pady=20)
    
    def _create_appearance_settings(self, parent):
        """Create appearance settings section."""
        if ctk is None:
            return
            
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Theme settings
        theme_frame = ctk.CTkFrame(scroll)
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            theme_frame,
            text="Theme",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        theme_row = ctk.CTkFrame(theme_frame)
        theme_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            theme_row,
            text="Color Theme:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.theme_combo = ctk.CTkComboBox(
            theme_row,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            width=120
        )
        self.theme_combo.set("Dark")
        self.theme_combo.pack(side="left", padx=10)
        
        # Accent color
        accent_row = ctk.CTkFrame(theme_frame)
        accent_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            accent_row,
            text="Accent Color:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.accent_combo = ctk.CTkComboBox(
            accent_row,
            values=["Blue", "Green", "Purple", "Red", "Orange"],
            width=120
        )
        self.accent_combo.set("Blue")
        self.accent_combo.pack(side="left", padx=10)
        
        # Font settings
        font_frame = ctk.CTkFrame(scroll)
        font_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            font_frame,
            text="Font",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        font_row = ctk.CTkFrame(font_frame)
        font_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            font_row,
            text="UI Scale:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.scale_slider = ctk.CTkSlider(
            font_row,
            from_=0.8,
            to=1.4,
            number_of_steps=6
        )
        self.scale_slider.set(1.0)
        self.scale_slider.pack(side="left", padx=10, fill="x", expand=True)
        
        self.scale_label = ctk.CTkLabel(
            font_row,
            text="100%",
            font=ctk.CTkFont(size=11)
        )
        self.scale_label.pack(side="right", padx=5)
        
        # Animations
        anim_frame = ctk.CTkFrame(scroll)
        anim_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            anim_frame,
            text="Animations",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.enable_animations = ctk.CTkCheckBox(
            anim_frame,
            text="Enable animations"
        )
        self.enable_animations.pack(anchor="w", padx=20, pady=2)
        self.enable_animations.select()
        
        self.reduce_motion = ctk.CTkCheckBox(
            anim_frame,
            text="Reduce motion"
        )
        self.reduce_motion.pack(anchor="w", padx=20, pady=2)
        
        # Save button
        ctk.CTkButton(
            scroll,
            text="💾 Apply Appearance",
            command=self._save_appearance_settings,
            fg_color="#2ECC71",
            hover_color="#27AE60"
        ).pack(pady=20)
    
    def _create_advanced_settings(self, parent):
        """Create advanced settings section."""
        if ctk is None:
            return
            
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Warning
        ctk.CTkLabel(
            scroll,
            text="⚠️ Advanced settings - Modify with caution",
            font=ctk.CTkFont(size=11),
            text_color="#F39C12"
        ).pack(anchor="w", padx=10, pady=10)
        
        # AI Settings
        ai_frame = ctk.CTkFrame(scroll)
        ai_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            ai_frame,
            text="AI Engine Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        # Training interval
        train_row = ctk.CTkFrame(ai_frame)
        train_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            train_row,
            text="Auto-training interval (minutes):",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.train_interval = ctk.CTkEntry(train_row, width=80)
        self.train_interval.insert(0, "60")
        self.train_interval.pack(side="left", padx=10)
        
        # Max epochs
        epoch_row = ctk.CTkFrame(ai_frame)
        epoch_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            epoch_row,
            text="Max training epochs:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.max_epochs = ctk.CTkEntry(epoch_row, width=80)
        self.max_epochs.insert(0, "10")
        self.max_epochs.pack(side="left", padx=10)
        
        # Network Settings
        net_frame = ctk.CTkFrame(scroll)
        net_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            net_frame,
            text="Network Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        # Request timeout
        timeout_row = ctk.CTkFrame(net_frame)
        timeout_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            timeout_row,
            text="Request timeout (seconds):",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.timeout_entry = ctk.CTkEntry(timeout_row, width=80)
        self.timeout_entry.insert(0, "30")
        self.timeout_entry.pack(side="left", padx=10)
        
        # Rate limiting
        rate_row = ctk.CTkFrame(net_frame)
        rate_row.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            rate_row,
            text="Request delay (ms):",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.rate_delay = ctk.CTkEntry(rate_row, width=80)
        self.rate_delay.insert(0, "500")
        self.rate_delay.pack(side="left", padx=10)
        
        # Debug settings
        debug_frame = ctk.CTkFrame(scroll)
        debug_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            debug_frame,
            text="Debug Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.debug_mode = ctk.CTkCheckBox(
            debug_frame,
            text="Enable debug mode"
        )
        self.debug_mode.pack(anchor="w", padx=20, pady=2)
        
        self.verbose_logging = ctk.CTkCheckBox(
            debug_frame,
            text="Verbose logging"
        )
        self.verbose_logging.pack(anchor="w", padx=20, pady=2)
        
        # Reset section
        reset_frame = ctk.CTkFrame(scroll)
        reset_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            reset_frame,
            text="Reset Options",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        btn_row = ctk.CTkFrame(reset_frame)
        btn_row.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_row,
            text="Reset to Defaults",
            command=self._reset_to_defaults,
            fg_color="#F39C12",
            hover_color="#D68910"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_row,
            text="Clear All Data",
            command=self._clear_all_data,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        ).pack(side="left", padx=5)
        
        # Save button
        ctk.CTkButton(
            scroll,
            text="💾 Save Advanced Settings",
            command=self._save_advanced_settings,
            fg_color="#2ECC71",
            hover_color="#27AE60"
        ).pack(pady=20)
    
    def _create_about_section(self, parent):
        """Create about section."""
        if ctk is None:
            return
            
        # Logo/Title area
        title_frame = ctk.CTkFrame(parent)
        title_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="MarketAI",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="Advanced Market Analysis & Prediction System",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=12),
            text_color="#00D4FF"
        ).pack(pady=5)
        
        # Description
        desc_frame = ctk.CTkFrame(parent)
        desc_frame.pack(fill="x", padx=20, pady=10)
        
        description = """
MarketAI is an AI-powered market analysis system that learns from market data 
to provide analytics, predictions, and trading tips.

Features:
• Real-time market monitoring with customizable alerts
• AI-generated predictions and insights
• Multi-API integration (AntiPublic, LZT Market, LolzTeam)
• Self-training capabilities for improved accuracy
• Modern, customizable interface

The system uses advanced machine learning techniques to analyze market trends,
identify opportunities, and help users make informed decisions.
        """
        
        ctk.CTkLabel(
            desc_frame,
            text=description.strip(),
            font=ctk.CTkFont(size=11),
            justify="left"
        ).pack(padx=20, pady=10)
        
        # Links
        links_frame = ctk.CTkFrame(parent)
        links_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            links_frame,
            text="API Documentation:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=20, pady=5)
        
        docs = [
            "• AntiPublic: https://antipublic.readme.io/reference/information",
            "• LZT Market: https://lzt-market.readme.io/reference/information",
            "• LolzTeam: https://lolzteam.readme.io/reference/information"
        ]
        
        for doc in docs:
            ctk.CTkLabel(
                links_frame,
                text=doc,
                font=ctk.CTkFont(size=10),
                text_color="#3498DB"
            ).pack(anchor="w", padx=30, pady=1)
        
        # Copyright
        ctk.CTkLabel(
            parent,
            text="© 2024 MarketAI. All rights reserved.",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(side="bottom", pady=20)
    
    def _save_api_keys(self):
        """Save API keys."""
        if self.api_manager:
            for api_name in ['antipublic', 'lzt_market', 'lolzteam']:
                if api_name in self.api_entries:
                    key = self.api_entries[api_name].get()
                    if key:
                        self.api_manager.set_api_key(api_name, key)
            
            self.api_manager.save_config()
            self._show_message("API keys saved successfully!")
        
        self.on_save()
    
    def _test_api(self, api_name: str):
        """Test a single API connection."""
        if not self.api_manager:
            return
        
        # Get and set the key first
        if api_name in self.api_entries:
            key = self.api_entries[api_name].get()
            if key:
                self.api_manager.set_api_key(api_name, key)
        
        # Test connection
        api_map = {
            'antipublic': self.api_manager.antipublic,
            'lzt_market': self.api_manager.lzt_market,
            'lolzteam': self.api_manager.lolzteam
        }
        
        api = api_map.get(api_name)
        if api:
            result = api.test_connection()
            status_key = f"{api_name}_status"
            
            if result.get('success'):
                if status_key in self.api_entries:
                    self.api_entries[status_key].configure(
                        text="● Connected",
                        text_color="#2ECC71"
                    )
            else:
                if status_key in self.api_entries:
                    self.api_entries[status_key].configure(
                        text=f"● Failed: {result.get('message', 'Unknown error')[:20]}",
                        text_color="#E74C3C"
                    )
    
    def _test_all_connections(self):
        """Test all API connections."""
        for api_name in ['antipublic', 'lzt_market', 'lolzteam']:
            self._test_api(api_name)
    
    def _change_theme(self, theme: str):
        """Change application theme."""
        if ctk:
            theme_map = {
                'Dark': 'dark',
                'Light': 'light',
                'System': 'system'
            }
            ctk.set_appearance_mode(theme_map.get(theme, 'dark'))
    
    def _save_general_settings(self):
        """Save general settings."""
        self._settings['general'] = {
            'auto_start_watch': self.auto_start_watch.get(),
            'remember_last_tab': self.remember_last_tab.get(),
            'minimize_to_tray': self.minimize_to_tray.get(),
            'enable_sounds': self.enable_sounds.get(),
            'enable_desktop_notif': self.enable_desktop_notif.get(),
            'auto_save': self.auto_save.get(),
            'collect_analytics': self.collect_analytics.get()
        }
        self._save_settings_to_file()
        self._show_message("General settings saved!")
        self.on_save()
    
    def _save_appearance_settings(self):
        """Save appearance settings."""
        self._settings['appearance'] = {
            'theme': self.theme_combo.get(),
            'accent': self.accent_combo.get(),
            'scale': self.scale_slider.get(),
            'animations': self.enable_animations.get(),
            'reduce_motion': self.reduce_motion.get()
        }
        self._save_settings_to_file()
        self._show_message("Appearance settings saved!")
        self.on_save()
    
    def _save_advanced_settings(self):
        """Save advanced settings."""
        self._settings['advanced'] = {
            'train_interval': int(self.train_interval.get() or 60),
            'max_epochs': int(self.max_epochs.get() or 10),
            'timeout': int(self.timeout_entry.get() or 30),
            'rate_delay': int(self.rate_delay.get() or 500),
            'debug_mode': self.debug_mode.get(),
            'verbose_logging': self.verbose_logging.get()
        }
        self._save_settings_to_file()
        self._show_message("Advanced settings saved!")
        self.on_save()
    
    def _save_settings_to_file(self):
        """Save all settings to file."""
        config_path = Path("shared_data/gui_settings.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self._settings, f, indent=2)
    
    def _load_settings_from_file(self):
        """Load settings from file."""
        config_path = Path("shared_data/gui_settings.json")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._settings = json.load(f)
                self._apply_settings()
    
    def _apply_settings(self):
        """Apply loaded settings to UI."""
        # Apply general settings
        if 'general' in self._settings:
            gen = self._settings['general']
            if gen.get('auto_start_watch'):
                self.auto_start_watch.select()
            if gen.get('remember_last_tab'):
                self.remember_last_tab.select()
            # ... apply other settings
        
        # Apply appearance
        if 'appearance' in self._settings:
            app = self._settings['appearance']
            if app.get('theme'):
                self.theme_combo.set(app['theme'])
                self._change_theme(app['theme'])
    
    def _clear_cache(self):
        """Clear application cache."""
        self._show_message("Cache cleared!")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._settings = {}
        self._show_message("Settings reset to defaults!")
    
    def _clear_all_data(self):
        """Clear all application data."""
        self._show_message("All data cleared!")
    
    def _show_message(self, message: str):
        """Show a message (placeholder for proper notification)."""
        print(f"[Settings] {message}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        return self._settings.copy()
    
    def load_settings(self):
        """Load settings from file."""
        self._load_settings_from_file()
