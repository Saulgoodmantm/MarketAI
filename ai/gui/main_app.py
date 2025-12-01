"""
MarketAI Main Application - Primary GUI window integrating all tabs and features
"""

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.absolute()))

from .tabs import AutobuyTab, MarketWatchTab, AnalyticsTab, SettingsTab


class MarketAIApp:
    """
    Main MarketAI application window.
    Integrates all tabs and provides unified market analysis interface.
    """
    
    def __init__(self, api_manager=None, ai_engine=None):
        """
        Initialize the MarketAI application.
        
        Args:
            api_manager: API manager for market data access
            ai_engine: AI engine for predictions and analysis
        """
        if ctk is None:
            raise ImportError("customtkinter is required for the GUI")
        
        self.api_manager = api_manager
        self.ai_engine = ai_engine
        
        # Application state
        self._is_running = False
        self._notifications = []
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("MarketAI - Advanced Market Analysis")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize UI
        self._create_ui()
        
        # Initialize tabs
        self._init_tabs()
        
        # Load saved settings
        self._load_settings()
    
    def _create_ui(self):
        """Create the main UI structure."""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create header
        self._create_header()
        
        # Create main content area with tabs
        self._create_content_area()
        
        # Create footer/status bar
        self._create_footer()
    
    def _create_header(self):
        """Create application header."""
        header = ctk.CTkFrame(self.main_frame, height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)
        
        # Logo text
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🤖 MARKET",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00D4FF"
        )
        logo_label.pack(side="left")
        
        ai_label = ctk.CTkLabel(
            title_frame,
            text="AI",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        ai_label.pack(side="left")
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Advanced Market Analysis & Prediction",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        subtitle.pack(side="left", padx=20)
        
        # Right side - Status and controls
        controls_frame = ctk.CTkFrame(header, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=10)
        
        # API Status indicators
        self.api_status_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        self.api_status_frame.pack(side="left", padx=20)
        
        self.api_indicators = {}
        apis = [("AP", "AntiPublic"), ("LM", "LZT Market"), ("LT", "LolzTeam")]
        
        for short, full in apis:
            indicator_frame = ctk.CTkFrame(self.api_status_frame, fg_color="transparent")
            indicator_frame.pack(side="left", padx=5)
            
            self.api_indicators[short] = ctk.CTkLabel(
                indicator_frame,
                text=f"● {short}",
                font=ctk.CTkFont(size=10),
                text_color="#FF6B6B"  # Red = not configured
            )
            self.api_indicators[short].pack()
        
        # Notification bell
        self.notif_btn = ctk.CTkButton(
            controls_frame,
            text="🔔",
            width=40,
            height=40,
            command=self._show_notifications
        )
        self.notif_btn.pack(side="left", padx=5)
        
        # Time display
        self.time_label = ctk.CTkLabel(
            controls_frame,
            text=datetime.now().strftime("%H:%M"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.time_label.pack(side="left", padx=10)
        
        # Update time every second
        self._update_time()
    
    def _create_content_area(self):
        """Create main content area with tabs."""
        # Tab container
        self.tab_view = ctk.CTkTabview(
            self.main_frame,
            segmented_button_fg_color="#2B2B2B",
            segmented_button_selected_color="#00D4FF",
            segmented_button_selected_hover_color="#00A8CC"
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs
        self.autobuy_frame = self.tab_view.add("🤖 Autobuy")
        self.market_watch_frame = self.tab_view.add("👁️ Market Watch")
        self.analytics_frame = self.tab_view.add("📊 Analytics")
        self.settings_frame = self.tab_view.add("⚙️ Settings")
        
        # Set default tab
        self.tab_view.set("👁️ Market Watch")
    
    def _create_footer(self):
        """Create footer/status bar."""
        footer = ctk.CTkFrame(self.main_frame, height=30, corner_radius=0)
        footer.pack(fill="x", padx=0, pady=0, side="bottom")
        footer.pack_propagate(False)
        
        # Left side - Status message
        self.status_label = ctk.CTkLabel(
            footer,
            text="Ready",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=10)
        
        # Right side - Version and connection status
        version_label = ctk.CTkLabel(
            footer,
            text="MarketAI v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        version_label.pack(side="right", padx=10)
        
        # Connection status
        self.connection_label = ctk.CTkLabel(
            footer,
            text="● Connected",
            font=ctk.CTkFont(size=10),
            text_color="#2ECC71"
        )
        self.connection_label.pack(side="right", padx=10)
    
    def _init_tabs(self):
        """Initialize all tab components."""
        # Initialize Autobuy tab (disabled by default)
        self.autobuy_tab = AutobuyTab(
            self.autobuy_frame,
            api_manager=self.api_manager,
            on_log=self._log_message
        )
        if self.autobuy_tab.frame:
            self.autobuy_tab.frame.pack(fill="both", expand=True)
        
        # Initialize Market Watch tab
        self.market_watch_tab = MarketWatchTab(
            self.market_watch_frame,
            api_manager=self.api_manager,
            on_notification=self._add_notification
        )
        if self.market_watch_tab.frame:
            self.market_watch_tab.frame.pack(fill="both", expand=True)
        
        # Initialize Analytics tab
        self.analytics_tab = AnalyticsTab(
            self.analytics_frame,
            api_manager=self.api_manager,
            ai_engine=self.ai_engine
        )
        if self.analytics_tab.frame:
            self.analytics_tab.frame.pack(fill="both", expand=True)
        
        # Initialize Settings tab
        self.settings_tab = SettingsTab(
            self.settings_frame,
            api_manager=self.api_manager,
            on_save=self._on_settings_save
        )
        if self.settings_tab.frame:
            self.settings_tab.frame.pack(fill="both", expand=True)
    
    def _update_time(self):
        """Update time display."""
        self.time_label.configure(text=datetime.now().strftime("%H:%M"))
        self.root.after(1000, self._update_time)
    
    def _update_api_status(self):
        """Update API status indicators."""
        if not self.api_manager:
            return
        
        status = self.api_manager.get_status()
        
        indicator_map = {
            'AP': 'antipublic',
            'LM': 'lzt_market',
            'LT': 'lolzteam'
        }
        
        for short, api_name in indicator_map.items():
            api_status = status.get(api_name, {})
            if api_status.get('configured'):
                self.api_indicators[short].configure(
                    text_color="#2ECC71"  # Green = configured
                )
            else:
                self.api_indicators[short].configure(
                    text_color="#FF6B6B"  # Red = not configured
                )
    
    def _show_notifications(self):
        """Show notifications popup."""
        # Create notification popup
        popup = ctk.CTkToplevel(self.root)
        popup.title("Notifications")
        popup.geometry("400x500")
        popup.transient(self.root)
        
        # Header
        header = ctk.CTkFrame(popup)
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Notifications",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            header,
            text="Clear All",
            width=80,
            command=lambda: self._clear_notifications(popup)
        ).pack(side="right", padx=10)
        
        # Notifications list
        notif_scroll = ctk.CTkScrollableFrame(popup)
        notif_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        if not self._notifications:
            ctk.CTkLabel(
                notif_scroll,
                text="No notifications",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            ).pack(pady=50)
        else:
            for notif in self._notifications[-20:]:  # Last 20
                notif_frame = ctk.CTkFrame(notif_scroll)
                notif_frame.pack(fill="x", padx=5, pady=2)
                
                ctk.CTkLabel(
                    notif_frame,
                    text=notif.get('timestamp', datetime.now()).strftime("%H:%M"),
                    font=ctk.CTkFont(size=9),
                    text_color="#888888"
                ).pack(side="left", padx=5)
                
                ctk.CTkLabel(
                    notif_frame,
                    text=f"{notif.get('title', '')}: {notif.get('message', '')}",
                    font=ctk.CTkFont(size=10)
                ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _add_notification(self, notification: Dict[str, Any]):
        """Add a notification."""
        self._notifications.append(notification)
        
        # Update notification button to show unread count
        unread = len(self._notifications)
        if unread > 0:
            self.notif_btn.configure(text=f"🔔 {min(unread, 99)}")
    
    def _clear_notifications(self, popup=None):
        """Clear all notifications."""
        self._notifications = []
        self.notif_btn.configure(text="🔔")
        if popup:
            popup.destroy()
    
    def _log_message(self, message: str):
        """Log a message to status bar."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.configure(text=f"[{timestamp}] {message}")
    
    def _on_settings_save(self):
        """Handle settings save."""
        self._update_api_status()
        self._log_message("Settings saved")
    
    def _load_settings(self):
        """Load saved settings."""
        if hasattr(self, 'settings_tab'):
            self.settings_tab.load_settings()
        
        self._update_api_status()
    
    def _save_settings(self):
        """Save current settings."""
        # Note: Autobuy enabled state is deliberately NOT saved
        settings = {
            'market_watch': self.market_watch_tab.get_config() if self.market_watch_tab else {},
            'autobuy_config': self.autobuy_tab.get_config() if self.autobuy_tab else {},
            # Autobuy enabled state is NOT included for safety
        }
        return settings
    
    def run(self):
        """Run the application main loop."""
        self._is_running = True
        self._log_message("Application started")
        
        # Start main loop
        self.root.mainloop()
    
    def quit(self):
        """Quit the application."""
        self._is_running = False
        
        # Stop any running processes
        if self.autobuy_tab and self.autobuy_tab.is_running():
            self.autobuy_tab._stop_autobuy()
        
        if self.market_watch_tab and self.market_watch_tab.is_watching():
            self.market_watch_tab._stop_watching()
        
        self.root.quit()


def create_app(api_manager=None, ai_engine=None) -> Optional[MarketAIApp]:
    """
    Create and return a MarketAI application instance.
    
    Args:
        api_manager: API manager instance
        ai_engine: AI engine instance
        
    Returns:
        MarketAIApp instance or None if GUI unavailable
    """
    if ctk is None:
        print("[ERROR] customtkinter is required for the GUI")
        print("[*] Install with: pip install customtkinter")
        return None
    
    return MarketAIApp(api_manager=api_manager, ai_engine=ai_engine)


def main():
    """Main entry point for testing."""
    app = create_app()
    if app:
        app.run()


if __name__ == "__main__":
    main()
