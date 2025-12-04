"""
MarketAI Main Application - Primary GUI window integrating all tabs and features
Enhanced with futuristic design and animations
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

from .tabs import AutobuyTab, MarketWatchTab, AnalyticsTab, SettingsTab, PortfolioTab


# Futuristic color scheme
COLORS = {
    'primary': '#00D4FF',      # Cyan
    'secondary': '#7B2CBF',    # Purple
    'accent': '#E100FF',       # Magenta
    'success': '#00FF88',      # Neon green
    'warning': '#FFB800',      # Gold
    'danger': '#FF3366',       # Red
    'bg_dark': '#0D1117',      # Dark background
    'bg_card': '#161B22',      # Card background
    'bg_header': '#1C2128',    # Header background
    'text_primary': '#FFFFFF',
    'text_dim': '#8B949E',
    'glow': '#00D4FF'
}


class MarketAIApp:
    """
    Main MarketAI application window.
    Features modern futuristic design with animations and real-time updates.
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
        
        # Configure appearance with dark futuristic theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("MarketAI - Advanced Market Analysis")
        self.root.geometry("1500x950")
        self.root.minsize(1300, 850)
        
        # Set window background
        self.root.configure(fg_color=COLORS['bg_dark'])
        
        # Initialize UI
        self._create_ui()
        
        # Initialize tabs
        self._init_tabs()
        
        # Load saved settings
        self._load_settings()
        
        # Start animations
        self._start_header_animation()
    
    def _create_ui(self):
        """Create the main UI structure with futuristic design."""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create header
        self._create_header()
        
        # Create main content area with tabs
        self._create_content_area()
        
        # Create footer/status bar
        self._create_footer()
    
    def _create_header(self):
        """Create futuristic application header with glow effect."""
        header = ctk.CTkFrame(
            self.main_frame, 
            height=90, 
            corner_radius=0,
            fg_color=COLORS['bg_header']
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Add subtle border glow effect
        glow_line = ctk.CTkFrame(header, height=2, fg_color=COLORS['primary'])
        glow_line.pack(side="bottom", fill="x")
        
        # Logo and title with futuristic styling
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=25, pady=15)
        
        # Animated logo icon
        self.logo_icon = ctk.CTkLabel(
            title_frame,
            text="⚡",
            font=ctk.CTkFont(size=36),
            text_color=COLORS['primary']
        )
        self.logo_icon.pack(side="left", padx=(0, 10))
        
        # Logo text with gradient effect (simulated)
        logo_text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        logo_text_frame.pack(side="left")
        
        logo_label = ctk.CTkLabel(
            logo_text_frame,
            text="MARKET",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS['primary']
        )
        logo_label.pack(side="left")
        
        ai_label = ctk.CTkLabel(
            logo_text_frame,
            text="AI",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS['text_primary']
        )
        ai_label.pack(side="left")
        
        # Subtitle with version
        subtitle = ctk.CTkLabel(
            title_frame,
            text="v2.0 • Advanced Market Analysis & Automation",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_dim']
        )
        subtitle.pack(side="left", padx=25)
        
        # Right side - Status and controls
        controls_frame = ctk.CTkFrame(header, fg_color="transparent")
        controls_frame.pack(side="right", padx=25, pady=15)
        
        # API Status indicators with modern design
        self.api_status_frame = ctk.CTkFrame(
            controls_frame, 
            fg_color=COLORS['bg_card'],
            corner_radius=10
        )
        self.api_status_frame.pack(side="left", padx=15, pady=5)
        
        self.api_indicators = {}
        apis = [
            ("AP", "AntiPublic", COLORS['danger']),
            ("LM", "LZT Market", COLORS['danger']),
            ("LT", "LolzTeam", COLORS['danger'])
        ]
        
        for short, full, color in apis:
            indicator_frame = ctk.CTkFrame(self.api_status_frame, fg_color="transparent")
            indicator_frame.pack(side="left", padx=8, pady=8)
            
            self.api_indicators[short] = ctk.CTkLabel(
                indicator_frame,
                text=f"● {short}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color
            )
            self.api_indicators[short].pack()
        
        # Notification button with badge
        self.notif_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        self.notif_frame.pack(side="left", padx=10)
        
        self.notif_btn = ctk.CTkButton(
            self.notif_frame,
            text="🔔",
            width=50,
            height=50,
            font=ctk.CTkFont(size=22),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['primary'],
            corner_radius=12,
            command=self._show_notifications
        )
        self.notif_btn.pack()
        
        # Time display with modern styling
        time_frame = ctk.CTkFrame(controls_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        time_frame.pack(side="left", padx=10, pady=5)
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text=datetime.now().strftime("%H:%M"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['primary']
        )
        self.time_label.pack(padx=15, pady=8)
        
        # Update time every second
        self._update_time()
    
    def _create_content_area(self):
        """Create main content area with modern tab design."""
        # Tab container with futuristic styling
        self.tab_view = ctk.CTkTabview(
            self.main_frame,
            fg_color=COLORS['bg_card'],
            segmented_button_fg_color=COLORS['bg_dark'],
            segmented_button_selected_color=COLORS['primary'],
            segmented_button_selected_hover_color=COLORS['secondary'],
            segmented_button_unselected_color=COLORS['bg_header'],
            segmented_button_unselected_hover_color=COLORS['bg_card'],
            corner_radius=15
        )
        self.tab_view.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Create tabs with icons
        self.autobuy_frame = self.tab_view.add("⚡ Autobuy")
        self.market_watch_frame = self.tab_view.add("👁️ Market Watch")
        self.portfolio_frame = self.tab_view.add("💼 Portfolio")
        self.analytics_frame = self.tab_view.add("📊 Analytics")
        self.settings_frame = self.tab_view.add("⚙️ Settings")
        
        # Set default tab
        self.tab_view.set("👁️ Market Watch")
    
    def _create_footer(self):
        """Create modern footer/status bar."""
        footer = ctk.CTkFrame(
            self.main_frame, 
            height=40, 
            corner_radius=0,
            fg_color=COLORS['bg_header']
        )
        footer.pack(fill="x", padx=0, pady=0, side="bottom")
        footer.pack_propagate(False)
        
        # Top glow line
        glow_line = ctk.CTkFrame(footer, height=1, fg_color=COLORS['bg_card'])
        glow_line.pack(side="top", fill="x")
        
        # Left side - Status message with icon
        status_frame = ctk.CTkFrame(footer, fg_color="transparent")
        status_frame.pack(side="left", padx=15, pady=8)
        
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['success']
        )
        self.status_indicator.pack(side="left", padx=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="System Ready",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_dim']
        )
        self.status_label.pack(side="left")
        
        # Right side - Version and connection status
        right_frame = ctk.CTkFrame(footer, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=8)
        
        # Connection status
        self.connection_label = ctk.CTkLabel(
            right_frame,
            text="● Online",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['success']
        )
        self.connection_label.pack(side="right", padx=15)
        
        # Version
        version_label = ctk.CTkLabel(
            right_frame,
            text="MarketAI v2.0",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_dim']
        )
        version_label.pack(side="right")
    
    def _start_header_animation(self):
        """Start subtle header animations."""
        self._animate_logo()
    
    def _animate_logo(self):
        """Animate the logo icon."""
        try:
            icons = ["⚡", "🔥", "💎", "✨", "⚡"]
            current_icon = self.logo_icon.cget("text")
            current_idx = icons.index(current_icon) if current_icon in icons else 0
            next_idx = (current_idx + 1) % len(icons)
            self.logo_icon.configure(text=icons[next_idx])
            
            # Schedule next animation frame
            self.root.after(3000, self._animate_logo)
        except Exception:
            pass  # Widget might be destroyed
    
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
        
        # Initialize Portfolio tab
        self.portfolio_tab = PortfolioTab(
            self.portfolio_frame,
            api_manager=self.api_manager,
            on_notification=self._add_notification
        )
        if self.portfolio_tab.frame:
            self.portfolio_tab.frame.pack(fill="both", expand=True)
        
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
        """Update API status indicators with modern colors."""
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
                    text_color=COLORS['success']  # Green = configured
                )
            else:
                self.api_indicators[short].configure(
                    text_color=COLORS['danger']  # Red = not configured
                )
    
    def _show_notifications(self):
        """Show modern notifications popup."""
        # Create notification popup
        popup = ctk.CTkToplevel(self.root)
        popup.title("Notifications")
        popup.geometry("450x550")
        popup.transient(self.root)
        popup.configure(fg_color=COLORS['bg_dark'])
        
        # Header
        header = ctk.CTkFrame(popup, fg_color=COLORS['bg_header'], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(
            header,
            text="🔔 Notifications",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['primary']
        ).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(
            header,
            text="Clear All",
            width=90,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS['danger'],
            hover_color="#CC2952",
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
