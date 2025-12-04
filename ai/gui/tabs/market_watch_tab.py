"""
Market Watch Tab - Monitor market listings and receive notifications
Enhanced with search functionality and modern futuristic design
"""

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import threading
import time


class MarketWatchTab:
    """
    Market Watch tab for monitoring market listings and receiving notifications.
    Features real-time search, live market data, and modern UI with animations.
    """
    
    # Default keywords for high-value item detection (can be customized)
    DEFAULT_HIGH_VALUE_KEYWORDS = ['rare', 'premium', 'exclusive', 'limited', 'og', 'stacked', 'full access', 'original email']
    MAX_ITEMS_DISPLAY = 100  # Maximum items to display in lists
    
    # Color scheme for futuristic design
    COLORS = {
        'primary': '#00D4FF',      # Cyan
        'secondary': '#7B2CBF',    # Purple
        'accent': '#E100FF',       # Magenta
        'success': '#00FF88',      # Neon green
        'warning': '#FFB800',      # Gold
        'danger': '#FF3366',       # Red
        'bg_dark': '#0D1117',      # Dark background
        'bg_card': '#161B22',      # Card background
        'text_dim': '#8B949E',     # Dimmed text
        'glow': '#00D4FF'          # Glow effect color
    }
    
    def __init__(self, parent, api_manager=None, on_notification: Optional[Callable] = None):
        """
        Initialize the Market Watch tab.
        
        Args:
            parent: Parent widget
            api_manager: API manager instance
            on_notification: Callback for notifications
        """
        self.parent = parent
        self.api_manager = api_manager
        self.on_notification = on_notification or (lambda x: None)
        
        # Watch configuration
        self._watches = []
        self._is_watching = False
        self._watch_thread = None
        self._high_value_keywords = self.DEFAULT_HIGH_VALUE_KEYWORDS.copy()
        
        # Market data cache
        self._market_data = {}
        self._search_results = []
        self._last_update = None
        self._animation_running = False
        
        # Build UI
        self.frame = self._create_ui()
    
    def _create_ui(self):
        """Create the Market Watch tab UI with modern futuristic design."""
        if ctk is None:
            return None
            
        frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Header with gradient effect simulation
        header = ctk.CTkFrame(frame, fg_color=self.COLORS['bg_card'], corner_radius=15)
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Title with glow effect (simulated with colored text)
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        title = ctk.CTkLabel(
            title_frame,
            text="👁️ MARKET WATCH",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.COLORS['primary']
        )
        title.pack(side="left")
        
        # Animated status indicator
        self.status_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20)
        
        self.status_dot = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=self.COLORS['text_dim']
        )
        self.status_dot.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS['text_dim']
        )
        self.status_label.pack(side="left")
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Left column - Search and Configuration
        left_col = ctk.CTkFrame(content, width=380, fg_color=self.COLORS['bg_card'], corner_radius=15)
        left_col.pack(side="left", fill="y", padx=(0, 10), pady=5)
        left_col.pack_propagate(False)
        
        self._create_search_section(left_col)
        self._create_watch_config(left_col)
        
        # Right column - Market View and Results
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(0, 0), pady=5)
        
        self._create_market_view(right_col)
        
        return frame
    
    def _create_search_section(self, parent):
        """Create the search section with real search functionality."""
        if ctk is None:
            return
        
        # Search header
        search_header = ctk.CTkFrame(parent, fg_color="transparent")
        search_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            search_header,
            text="🔍 SEARCH MARKET",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS['primary']
        ).pack(anchor="w")
        
        # Search input with modern design
        search_frame = ctk.CTkFrame(parent, fg_color=self.COLORS['bg_dark'], corner_radius=10)
        search_frame.pack(fill="x", padx=15, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search accounts, games, items...",
            height=45,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            border_width=0
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=15, pady=5)
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        self.search_btn = ctk.CTkButton(
            search_frame,
            text="→",
            width=45,
            height=35,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=self.COLORS['primary'],
            hover_color=self.COLORS['secondary'],
            corner_radius=8,
            command=self._perform_search
        )
        self.search_btn.pack(side="right", padx=10, pady=5)
        
        # Quick filters
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            filter_frame,
            text="Quick Filters:",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS['text_dim']
        ).pack(side="left", padx=5)
        
        # Category dropdown for search
        self.search_category = ctk.CTkComboBox(
            filter_frame,
            values=["All Categories", "Steam", "Fortnite", "Valorant", "Origin/EA", "Genshin Impact", "Telegram"],
            width=130,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=self.COLORS['bg_dark'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['secondary'],
            dropdown_fg_color=self.COLORS['bg_card']
        )
        self.search_category.set("All Categories")
        self.search_category.pack(side="left", padx=5)
        
        # Price range for search
        price_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        price_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(price_frame, text="$", font=ctk.CTkFont(size=11)).pack(side="left")
        self.search_min_price = ctk.CTkEntry(
            price_frame, width=50, height=28, placeholder_text="Min",
            font=ctk.CTkFont(size=10), fg_color=self.COLORS['bg_dark']
        )
        self.search_min_price.pack(side="left", padx=2)
        
        ctk.CTkLabel(price_frame, text="-", font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
        self.search_max_price = ctk.CTkEntry(
            price_frame, width=50, height=28, placeholder_text="Max",
            font=ctk.CTkFont(size=10), fg_color=self.COLORS['bg_dark']
        )
        self.search_max_price.pack(side="left", padx=2)
        
        # Divider
        ctk.CTkFrame(parent, height=2, fg_color=self.COLORS['bg_dark']).pack(fill="x", padx=15, pady=15)
    
    def _create_watch_config(self, parent):
        """Create watch configuration section with modern styling."""
        if ctk is None:
            return
            
        # Section title
        ctk.CTkLabel(
            parent,
            text="⚙️ WATCH SETTINGS",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS['primary']
        ).pack(anchor="w", padx=15, pady=(5, 10))
        
        # Scrollable configuration area
        config_scroll = ctk.CTkScrollableFrame(
            parent, 
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['primary']
        )
        config_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Game/Category selection with icons
        cat_frame = ctk.CTkFrame(config_scroll, fg_color=self.COLORS['bg_dark'], corner_radius=10)
        cat_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            cat_frame,
            text="Select Categories to Monitor:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLORS['text_dim']
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.game_vars = {}
        games = [
            ('Steam', 'steam', '🎮'),
            ('Fortnite', 'fortnite', '🎯'),
            ('Valorant', 'valorant', '🔫'),
            ('Origin/EA', 'origin', '⚽'),
            ('Genshin Impact', 'genshin-impact', '⚔️'),
            ('Telegram', 'telegram', '💬'),
            ('Discord', 'discord', '🎧'),
            ('VK', 'vk', '📱'),
            ('Instagram', 'instagram', '📸'),
            ('TikTok', 'tiktok', '🎵')
        ]
        
        # Create 2-column grid for categories
        cat_grid = ctk.CTkFrame(cat_frame, fg_color="transparent")
        cat_grid.pack(fill="x", padx=10, pady=(0, 10))
        
        for i, (name, key, icon) in enumerate(games):
            var = ctk.BooleanVar(value=False)
            self.game_vars[key] = var
            cb = ctk.CTkCheckBox(
                cat_grid,
                text=f"{icon} {name}",
                variable=var,
                font=ctk.CTkFont(size=11),
                fg_color=self.COLORS['primary'],
                hover_color=self.COLORS['secondary'],
                checkmark_color="white"
            )
            cb.grid(row=i//2, column=i%2, padx=5, pady=3, sticky="w")
        
        # Price filter with modern inputs
        price_frame = ctk.CTkFrame(config_scroll, fg_color=self.COLORS['bg_dark'], corner_radius=10)
        price_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            price_frame,
            text="Price Range Filter:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLORS['text_dim']
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        price_row = ctk.CTkFrame(price_frame, fg_color="transparent")
        price_row.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(price_row, text="$", font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color=self.COLORS['success']).pack(side="left")
        self.min_price = ctk.CTkEntry(
            price_row, width=80, height=32, placeholder_text="Min",
            font=ctk.CTkFont(size=11), fg_color=self.COLORS['bg_card'],
            border_color=self.COLORS['primary']
        )
        self.min_price.pack(side="left", padx=5)
        
        ctk.CTkLabel(price_row, text=" — ", font=ctk.CTkFont(size=12)).pack(side="left")
        
        ctk.CTkLabel(price_row, text="$", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=self.COLORS['success']).pack(side="left")
        self.max_price = ctk.CTkEntry(
            price_row, width=80, height=32, placeholder_text="Max",
            font=ctk.CTkFont(size=11), fg_color=self.COLORS['bg_card'],
            border_color=self.COLORS['primary']
        )
        self.max_price.pack(side="left", padx=5)
        
        # Notification triggers
        notif_frame = ctk.CTkFrame(config_scroll, fg_color=self.COLORS['bg_dark'], corner_radius=10)
        notif_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            notif_frame,
            text="Alert Triggers:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLORS['text_dim']
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.stat_vars = {}
        alerts = [
            ('🆕 New Listings', 'new_listings', True),
            ('📉 Price Drops', 'price_drops', False),
            ('💎 High Value Items', 'high_value', False),
            ('⭐ Rare Items', 'rare_items', False),
            ('✅ Trusted Sellers', 'trusted_sellers', False)
        ]
        
        for name, key, default in alerts:
            var = ctk.BooleanVar(value=default)
            self.stat_vars[key] = var
            ctk.CTkCheckBox(
                notif_frame,
                text=name,
                variable=var,
                font=ctk.CTkFont(size=11),
                fg_color=self.COLORS['warning'] if 'High' in name else self.COLORS['primary'],
                hover_color=self.COLORS['secondary']
            ).pack(anchor="w", padx=15, pady=2)
        
        # Notification settings
        settings_frame = ctk.CTkFrame(config_scroll, fg_color=self.COLORS['bg_dark'], corner_radius=10)
        settings_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            settings_frame,
            text="Notification Settings:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.COLORS['text_dim']
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.sound_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            settings_frame,
            text="🔊 Sound Alerts",
            variable=self.sound_var,
            font=ctk.CTkFont(size=11),
            fg_color=self.COLORS['text_dim'],
            progress_color=self.COLORS['primary']
        ).pack(anchor="w", padx=15, pady=3)
        
        self.desktop_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            settings_frame,
            text="💻 Desktop Notifications",
            variable=self.desktop_var,
            font=ctk.CTkFont(size=11),
            fg_color=self.COLORS['text_dim'],
            progress_color=self.COLORS['primary']
        ).pack(anchor="w", padx=15, pady=3)
        
        # Update interval
        interval_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        interval_row.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            interval_row,
            text="⏱️ Scan Interval:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        self.interval_label = ctk.CTkLabel(
            interval_row,
            text="30s",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.COLORS['primary']
        )
        self.interval_label.pack(side="right", padx=5)
        
        self.interval_slider = ctk.CTkSlider(
            settings_frame,
            from_=10,
            to=120,
            number_of_steps=22,
            command=self._update_interval_label,
            fg_color=self.COLORS['bg_dark'],
            progress_color=self.COLORS['primary'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['secondary']
        )
        self.interval_slider.set(30)
        self.interval_slider.pack(fill="x", padx=15, pady=(0, 15))
        
        # Control buttons with modern styling
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ START WATCHING",
            command=self._start_watching,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.COLORS['success'],
            hover_color="#00CC66",
            corner_radius=10
        )
        self.start_btn.pack(fill="x", pady=3)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ STOP",
            command=self._stop_watching,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.COLORS['danger'],
            hover_color="#CC2952",
            corner_radius=10,
            state="disabled"
        )
        self.stop_btn.pack(fill="x", pady=3)
    
    def _create_market_view(self, parent):
        """Create market view with search results and live listings."""
        if ctk is None:
            return
            
        # Tab view for different views
        tabs = ctk.CTkTabview(
            parent,
            fg_color=self.COLORS['bg_card'],
            segmented_button_fg_color=self.COLORS['bg_dark'],
            segmented_button_selected_color=self.COLORS['primary'],
            segmented_button_selected_hover_color=self.COLORS['secondary'],
            corner_radius=15
        )
        tabs.pack(fill="both", expand=True, pady=5)
        
        # Market Listings tab
        market_tab = tabs.add("📊 Live Market")
        self._create_market_listings(market_tab)
        
        # Search Results tab
        search_tab = tabs.add("🔍 Search Results")
        self._create_search_results_view(search_tab)
        
        # Notifications tab
        notif_tab = tabs.add("🔔 Alerts")
        self._create_notifications_view(notif_tab)
        
        # Statistics tab
        stats_tab = tabs.add("📈 Stats")
        self._create_statistics_view(stats_tab)
    
    def _create_search_results_view(self, parent):
        """Create search results view."""
        if ctk is None:
            return
        
        # Header with result count
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        self.search_result_count = ctk.CTkLabel(
            header,
            text="Enter a search term to find items",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS['text_dim']
        )
        self.search_result_count.pack(side="left", padx=5)
        
        # Sort options
        sort_frame = ctk.CTkFrame(header, fg_color="transparent")
        sort_frame.pack(side="right")
        
        ctk.CTkLabel(sort_frame, text="Sort:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        self.sort_combo = ctk.CTkComboBox(
            sort_frame,
            values=["Newest First", "Price: Low to High", "Price: High to Low"],
            width=140,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color=self.COLORS['bg_dark'],
            button_color=self.COLORS['primary']
        )
        self.sort_combo.set("Newest First")
        self.sort_combo.pack(side="left", padx=5)
        
        # Search results list
        self.search_results_frame = ctk.CTkScrollableFrame(
            parent, 
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['primary']
        )
        self.search_results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Placeholder message
        self.search_placeholder = ctk.CTkLabel(
            self.search_results_frame,
            text="🔍\n\nUse the search bar above to find items\n\nSupported searches:\n• Account names\n• Game titles\n• Keywords like 'rare', 'og', 'stacked'",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS['text_dim'],
            justify="center"
        )
        self.search_placeholder.pack(pady=80)
    
    def _create_market_listings(self, parent):
        """Create market listings view with live data."""
        if ctk is None:
            return
            
        # Header with controls
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Live Market Feed",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS['primary']
        ).pack(side="left", padx=5)
        
        # Last update with animated indicator
        update_frame = ctk.CTkFrame(header, fg_color="transparent")
        update_frame.pack(side="right")
        
        self.live_indicator = ctk.CTkLabel(
            update_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS['text_dim']
        )
        self.live_indicator.pack(side="left", padx=2)
        
        self.last_update_label = ctk.CTkLabel(
            update_frame,
            text="Not updated yet",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS['text_dim']
        )
        self.last_update_label.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            command=self._refresh_market,
            width=35,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color=self.COLORS['bg_dark'],
            hover_color=self.COLORS['primary'],
            corner_radius=8
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Listings display
        self.listings_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['primary']
        )
        self.listings_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initial placeholder - instructions
        self.listings_placeholder = ctk.CTkFrame(self.listings_frame, fg_color="transparent")
        self.listings_placeholder.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            self.listings_placeholder,
            text="📡",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(50, 15))
        
        ctk.CTkLabel(
            self.listings_placeholder,
            text="Select categories and click 'START WATCHING'\nto see live market listings",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_dim'],
            justify="center"
        ).pack()
        
        # Quick start hint
        ctk.CTkLabel(
            self.listings_placeholder,
            text="💡 Tip: You can also use the search bar to find specific items",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS['primary']
        ).pack(pady=20)
    
    def _create_notifications_view(self, parent):
        """Create notifications view."""
        if ctk is None:
            return
            
        # Header
        header = ctk.CTkFrame(parent)
        header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            header,
            text="Recent Notifications",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            header,
            text="Clear All",
            command=self._clear_notifications,
            width=70,
            height=25,
            font=ctk.CTkFont(size=10)
        ).pack(side="right", padx=5)
        
        # Notifications list
        self.notifications_frame = ctk.CTkScrollableFrame(parent)
        self.notifications_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Placeholder
        self.no_notif_label = ctk.CTkLabel(
            self.notifications_frame,
            text="No notifications yet\nStart watching to receive alerts",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.no_notif_label.pack(pady=50)
        
        self._notifications = []
    
    def _create_statistics_view(self, parent):
        """Create statistics view."""
        if ctk is None:
            return
            
        # Stats display
        ctk.CTkLabel(
            parent,
            text="Market Statistics",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        stats_grid = ctk.CTkFrame(parent)
        stats_grid.pack(fill="x", padx=10, pady=5)
        
        self.stats_labels = {}
        stats = [
            ("Items Checked", "0"),
            ("Notifications Sent", "0"),
            ("Price Drops Found", "0"),
            ("New Listings", "0"),
            ("Watch Sessions", "0"),
            ("Total Watch Time", "00:00:00")
        ]
        
        for i, (name, value) in enumerate(stats):
            frame = ctk.CTkFrame(stats_grid)
            frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
            
            ctk.CTkLabel(
                frame,
                text=name,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", padx=10, pady=2)
            
            self.stats_labels[name] = ctk.CTkLabel(
                frame,
                text=value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#00D4FF"
            )
            self.stats_labels[name].pack(anchor="w", padx=10, pady=2)
        
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        
        # AI Insights
        insights_frame = ctk.CTkFrame(parent)
        insights_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            insights_frame,
            text="🧠 AI Market Insights",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.insights_text = ctk.CTkTextbox(
            insights_frame,
            font=ctk.CTkFont(size=11)
        )
        self.insights_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.insights_text.insert("1.0", "AI insights will appear here once you start watching the market.\n\n")
        self.insights_text.insert("end", "The AI analyzes:\n")
        self.insights_text.insert("end", "• Price trends and patterns\n")
        self.insights_text.insert("end", "• Best times to buy\n")
        self.insights_text.insert("end", "• Value opportunities\n")
        self.insights_text.insert("end", "• Seller reputation analysis\n")
        self.insights_text.configure(state="disabled")
    
    def _update_interval_label(self, value):
        """Update interval label."""
        self.interval_label.configure(text=f"{int(value)}s")
    
    def _perform_search(self):
        """Perform market search with API."""
        search_term = self.search_entry.get().strip()
        if not search_term and not self.api_manager:
            return
        
        # Update UI for searching state
        self.search_btn.configure(state="disabled", text="...")
        self.search_result_count.configure(
            text="🔄 Searching...",
            text_color=self.COLORS['warning']
        )
        
        # Perform search in background thread
        threading.Thread(target=self._search_worker, args=(search_term,), daemon=True).start()
    
    def _search_worker(self, search_term: str):
        """Background worker for search."""
        try:
            results = []
            
            # Get category filter
            category_filter = self.search_category.get()
            category_map = {
                "All Categories": None,
                "Steam": "steam",
                "Fortnite": "fortnite",
                "Valorant": "valorant",
                "Origin/EA": "origin",
                "Genshin Impact": "genshin-impact",
                "Telegram": "telegram"
            }
            category = category_map.get(category_filter)
            
            # Get price filters
            try:
                min_price = float(self.search_min_price.get()) if self.search_min_price.get() else None
                max_price = float(self.search_max_price.get()) if self.search_max_price.get() else None
            except ValueError:
                min_price, max_price = None, None
            
            if self.api_manager and self.api_manager.lzt_market.is_configured():
                # Use API search
                result = self.api_manager.lzt_market.search(
                    category=category,
                    pmin=min_price,
                    pmax=max_price,
                    title=search_term,
                    page=1
                )
                
                if result.get('success'):
                    results = result.get('data', {}).get('items', [])
            else:
                # Simulate search results for demo/testing
                results = self._get_demo_search_results(search_term, category, min_price, max_price)
            
            # Store results
            self._search_results = results
            
            # Update UI (schedule on main thread)
            self._update_search_results_ui(results)
            
        except Exception as e:
            print(f"[Search Error] {e}")
            self._update_search_results_ui([])
    
    def _get_demo_search_results(self, search_term: str, category: str, min_price: float, max_price: float) -> List[Dict]:
        """Generate demo search results when API is not configured."""
        import random
        
        demo_items = [
            {"title": f"Steam Account - {search_term} Games", "price": 15.99, "category": "steam", "seller": "TrustedSeller", "rating": 98},
            {"title": f"Fortnite {search_term} Skins Bundle", "price": 25.50, "category": "fortnite", "seller": "GameStore", "rating": 95},
            {"title": f"Valorant {search_term} Rank Account", "price": 45.00, "category": "valorant", "seller": "ProGamer", "rating": 100},
            {"title": f"Origin Premium with {search_term}", "price": 12.99, "category": "origin", "seller": "EASales", "rating": 92},
            {"title": f"Genshin AR55 {search_term}", "price": 89.99, "category": "genshin-impact", "seller": "GenshinPro", "rating": 97},
        ]
        
        # Filter by category if specified
        if category:
            demo_items = [i for i in demo_items if i['category'] == category]
        
        # Filter by price
        if min_price:
            demo_items = [i for i in demo_items if i['price'] >= min_price]
        if max_price:
            demo_items = [i for i in demo_items if i['price'] <= max_price]
        
        # Add item IDs
        for i, item in enumerate(demo_items):
            item['item_id'] = random.randint(100000, 999999)
        
        return demo_items
    
    def _update_search_results_ui(self, results: List[Dict]):
        """Update search results UI (must be called from main thread context)."""
        try:
            # Re-enable search button
            self.search_btn.configure(state="normal", text="→")
            
            # Clear existing results
            for widget in self.search_results_frame.winfo_children():
                widget.destroy()
            
            if not results:
                # Show no results message
                self.search_result_count.configure(
                    text="No results found",
                    text_color=self.COLORS['danger']
                )
                ctk.CTkLabel(
                    self.search_results_frame,
                    text="😔\n\nNo items found matching your search.\n\nTry:\n• Different keywords\n• Broader price range\n• All categories",
                    font=ctk.CTkFont(size=13),
                    text_color=self.COLORS['text_dim'],
                    justify="center"
                ).pack(pady=60)
                return
            
            # Update result count
            self.search_result_count.configure(
                text=f"Found {len(results)} items",
                text_color=self.COLORS['success']
            )
            
            # Display results
            for item in results[:self.MAX_ITEMS_DISPLAY]:
                self._create_item_card(self.search_results_frame, item, show_buy_btn=True)
                
        except Exception as e:
            print(f"[UI Update Error] {e}")
    
    def _create_item_card(self, parent, item: Dict, show_buy_btn: bool = False):
        """Create a modern item card for listings."""
        if ctk is None:
            return
        
        card = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS['bg_dark'],
            corner_radius=12
        )
        card.pack(fill="x", padx=5, pady=4)
        
        # Left side - Item info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Title with truncation
        title = item.get('title', 'Unknown Item')
        if len(title) > 60:
            title = title[:57] + "..."
        
        ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        # Details row
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(anchor="w", pady=(5, 0))
        
        category = item.get('category', 'Unknown').replace('-', ' ').title()
        ctk.CTkLabel(
            details_frame,
            text=f"📁 {category}",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS['text_dim']
        ).pack(side="left", padx=(0, 15))
        
        seller = item.get('seller', 'Unknown')
        rating = item.get('rating', 0)
        rating_color = self.COLORS['success'] if rating >= 95 else (self.COLORS['warning'] if rating >= 80 else self.COLORS['danger'])
        
        ctk.CTkLabel(
            details_frame,
            text=f"👤 {seller}",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS['text_dim']
        ).pack(side="left", padx=(0, 10))
        
        if rating:
            ctk.CTkLabel(
                details_frame,
                text=f"⭐ {rating}%",
                font=ctk.CTkFont(size=10),
                text_color=rating_color
            ).pack(side="left")
        
        # Right side - Price and actions
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=15, pady=10)
        
        price = item.get('price', 0)
        ctk.CTkLabel(
            action_frame,
            text=f"${price:.2f}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.COLORS['success']
        ).pack()
        
        if show_buy_btn:
            item_id = item.get('item_id', item.get('id'))
            buy_btn = ctk.CTkButton(
                action_frame,
                text="🛒 View",
                width=70,
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color=self.COLORS['primary'],
                hover_color=self.COLORS['secondary'],
                corner_radius=8,
                command=lambda id=item_id, i=item: self._view_item(id, i)
            )
            buy_btn.pack(pady=(5, 0))
    
    def _view_item(self, item_id, item: Dict):
        """View/select an item for potential purchase."""
        self._add_notification(
            "Item Selected",
            f"Viewing: {item.get('title', 'Unknown')[:40]} - ${item.get('price', 0):.2f}",
            "info"
        )
        # In a real implementation, this would open item details or add to cart
    
    def _start_watching(self):
        """Start market watching with visual feedback."""
        # Get selected categories
        categories = [cat for cat, var in self.game_vars.items() if var.get()]
        
        if not categories:
            self._add_notification("Warning", "Please select at least one category to watch", "warning")
            return
        
        self._is_watching = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Update status with animation
        self.status_dot.configure(text_color=self.COLORS['success'])
        self.status_label.configure(text="LIVE", text_color=self.COLORS['success'])
        
        # Update live indicator
        if hasattr(self, 'live_indicator'):
            self.live_indicator.configure(text_color=self.COLORS['success'])
        
        # Clear placeholder
        if hasattr(self, 'listings_placeholder'):
            self.listings_placeholder.destroy()
        
        # Start watching thread
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()
        
        # Start animation
        self._start_pulse_animation()
        
        self._add_notification("Started", f"Now watching: {', '.join(categories)}", "info")
    
    def _start_pulse_animation(self):
        """Start pulse animation for live indicator."""
        self._animation_running = True
        self._pulse_animation()
    
    def _pulse_animation(self):
        """Animate the live indicator."""
        if not self._animation_running or not self._is_watching:
            return
        
        try:
            # Toggle between bright and dim
            current = self.status_dot.cget("text_color")
            new_color = self.COLORS['success'] if current == self.COLORS['text_dim'] else self.COLORS['text_dim']
            self.status_dot.configure(text_color=new_color)
            
            if hasattr(self, 'live_indicator'):
                self.live_indicator.configure(text_color=new_color)
            
            # Schedule next pulse
            if hasattr(self, 'frame') and self.frame:
                self.frame.after(800, self._pulse_animation)
        except Exception:
            pass
    
    def _stop_watching(self):
        """Stop market watching."""
        self._is_watching = False
        self._animation_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Update status
        self.status_dot.configure(text_color=self.COLORS['text_dim'])
        self.status_label.configure(text="Stopped", text_color=self.COLORS['text_dim'])
        
        if hasattr(self, 'live_indicator'):
            self.live_indicator.configure(text_color=self.COLORS['text_dim'])
        
        self._add_notification("Stopped", "Market watching has been stopped", "info")
    
    def _watch_loop(self):
        """Main watching loop (runs in separate thread)."""
        while self._is_watching:
            try:
                self._check_market()
                interval = int(self.interval_slider.get())
                time.sleep(interval)
            except Exception as e:
                print(f"[Watch Error] {e}")
                time.sleep(5)
    
    def _check_market(self):
        """Check market for updates and display items."""
        categories = [cat for cat, var in self.game_vars.items() if var.get()]
        all_items = []
        
        for category in categories:
            try:
                if self.api_manager and self.api_manager.lzt_market.is_configured():
                    result = self.api_manager.get_category_data(category, 1)
                    if result.get('success'):
                        items = result.get('data', {}).get('items', [])
                        for item in items:
                            item['category'] = category
                        all_items.extend(items)
                        self._process_market_items(category, items)
                else:
                    # Demo items when API not configured
                    demo_items = self._get_demo_items(category)
                    all_items.extend(demo_items)
                    self._process_market_items(category, demo_items)
            except Exception as e:
                print(f"[Market Check Error] {category}: {e}")
        
        # Update listings display
        self._update_listings_display(all_items)
        
        self._last_update = datetime.now()
        if self.last_update_label:
            self.last_update_label.configure(
                text=f"{self._last_update.strftime('%H:%M:%S')}"
            )
    
    def _get_demo_items(self, category: str) -> List[Dict]:
        """Get demo items for a category when API is not configured."""
        import random
        
        titles = {
            'steam': ["Steam Account 500+ Games", "CS2 Prime Status", "Steam Level 100+", "Rare Steam Account"],
            'fortnite': ["OG Renegade Raider", "Stacked Fortnite Account", "Rare Skins Bundle", "Galaxy Skin Account"],
            'valorant': ["Radiant Account", "Valorant Full Skins", "Diamond Rank Account", "Rare Knife Collection"],
            'origin': ["FIFA 24 Ultimate", "Apex Legends Heirlooms", "Battlefield Premium", "EA Play Pro"],
            'genshin-impact': ["AR60 5-Star Characters", "Genshin Full Archons", "Primogems Stacked", "All Limited 5-Stars"],
            'telegram': ["Telegram Premium", "Old Username Account", "Verified Channel", "Bot Account"],
        }
        
        cat_titles = titles.get(category, ["Account Item"])
        items = []
        
        for title in cat_titles[:3]:  # Only 3 demo items per category
            items.append({
                'item_id': random.randint(100000, 999999),
                'title': title,
                'price': round(random.uniform(5.0, 150.0), 2),
                'category': category,
                'seller': random.choice(['TopSeller', 'ProTrader', 'TrustedStore', 'GameMaster']),
                'rating': random.randint(85, 100)
            })
        
        return items
    
    def _update_listings_display(self, items: List[Dict]):
        """Update the listings display with items."""
        try:
            # Clear existing items
            for widget in self.listings_frame.winfo_children():
                widget.destroy()
            
            if not items:
                ctk.CTkLabel(
                    self.listings_frame,
                    text="No items found in selected categories",
                    font=ctk.CTkFont(size=13),
                    text_color=self.COLORS['text_dim']
                ).pack(pady=50)
                return
            
            # Sort by newest (if no timestamp, keep order)
            # Display items
            for item in items[:self.MAX_ITEMS_DISPLAY]:
                self._create_item_card(self.listings_frame, item, show_buy_btn=True)
                
        except Exception as e:
            print(f"[Display Error] {e}")
    
    def _process_market_items(self, category: str, items: List[Dict]):
        """Process market items and check for notifications."""
        # Check price range
        try:
            min_p = float(self.min_price.get() or 0)
            max_p = float(self.max_price.get() or float('inf'))
        except ValueError:
            min_p, max_p = 0, float('inf')
        
        for item in items:
            price = item.get('price', 0)
            
            if min_p <= price <= max_p:
                # Check if this is a new item we should notify about
                item_id = item.get('item_id', item.get('id'))
                
                if item_id not in self._market_data.get(category, {}):
                    # New listing notification
                    if self.stat_vars.get('new_listings', ctk.BooleanVar()).get():
                        self._add_notification(
                            "New Listing",
                            f"[{category}] {item.get('title', 'Unknown')} - ${price:.2f}",
                            "new"
                        )
                    
                    # Check for high value items using configurable keywords
                    if self.stat_vars.get('high_value', ctk.BooleanVar()).get():
                        title = item.get('title', '').lower()
                        if any(keyword in title for keyword in self._high_value_keywords):
                            self._add_notification(
                                "High Value Item",
                                f"[{category}] {item.get('title', 'Unknown')} - ${price:.2f}",
                                "warning"
                            )
                else:
                    # Existing item - check for price drop
                    old_item = self._market_data[category].get(item_id, {})
                    old_price = old_item.get('price', 0)
                    
                    if old_price > 0 and price < old_price:
                        price_drop_pct = ((old_price - price) / old_price) * 100
                        
                        # Notify if price dropped by more than 5%
                        if self.stat_vars.get('price_drops', ctk.BooleanVar()).get() and price_drop_pct >= 5:
                            self._add_notification(
                                "Price Drop",
                                f"[{category}] {item.get('title', 'Unknown')}: ${old_price:.2f} → ${price:.2f} ({price_drop_pct:.1f}% off)",
                                "new"
                            )
                            
                            # Update stats
                            if hasattr(self, 'stats_labels') and "Price Drops Found" in self.stats_labels:
                                try:
                                    current = int(self.stats_labels["Price Drops Found"].cget("text") or "0")
                                    self.stats_labels["Price Drops Found"].configure(text=str(current + 1))
                                except Exception:
                                    pass
                
                # Store/update item
                if category not in self._market_data:
                    self._market_data[category] = {}
                self._market_data[category][item_id] = item
        
        # Update statistics
        self._update_watch_stats()
    
    def _refresh_market(self):
        """Manually refresh market data."""
        if self.api_manager:
            threading.Thread(target=self._check_market, daemon=True).start()
    
    def _add_notification(self, title: str, message: str, notif_type: str = "info"):
        """Add a notification."""
        notification = {
            'title': title,
            'message': message,
            'type': notif_type,
            'timestamp': datetime.now()
        }
        self._notifications.insert(0, notification)
        
        # Update UI
        if ctk and hasattr(self, 'notifications_frame'):
            # Hide placeholder
            if hasattr(self, 'no_notif_label'):
                self.no_notif_label.pack_forget()
            
            # Create notification widget
            colors = {
                'info': '#3498DB',
                'warning': '#F39C12',
                'new': '#2ECC71',
                'error': '#E74C3C'
            }
            
            notif_frame = ctk.CTkFrame(self.notifications_frame)
            notif_frame.pack(fill="x", padx=5, pady=2)
            
            indicator = ctk.CTkLabel(
                notif_frame,
                text="●",
                font=ctk.CTkFont(size=10),
                text_color=colors.get(notif_type, '#888888')
            )
            indicator.pack(side="left", padx=5)
            
            time_label = ctk.CTkLabel(
                notif_frame,
                text=notification['timestamp'].strftime("%H:%M"),
                font=ctk.CTkFont(size=9),
                text_color="#888888"
            )
            time_label.pack(side="left", padx=5)
            
            title_label = ctk.CTkLabel(
                notif_frame,
                text=f"{title}:",
                font=ctk.CTkFont(size=10, weight="bold")
            )
            title_label.pack(side="left", padx=2)
            
            msg_label = ctk.CTkLabel(
                notif_frame,
                text=message,
                font=ctk.CTkFont(size=10)
            )
            msg_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Call notification callback
        self.on_notification(notification)
    
    def _clear_notifications(self):
        """Clear all notifications."""
        self._notifications = []
        
        if ctk and hasattr(self, 'notifications_frame'):
            for widget in self.notifications_frame.winfo_children():
                widget.destroy()
            
            self.no_notif_label = ctk.CTkLabel(
                self.notifications_frame,
                text="No notifications yet",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            self.no_notif_label.pack(pady=50)
    
    def _update_watch_stats(self):
        """Update watch statistics display."""
        if not hasattr(self, 'stats_labels'):
            return
        
        try:
            # Count total items checked
            total_items = sum(len(items) for items in self._market_data.values())
            if "Items Checked" in self.stats_labels:
                self.stats_labels["Items Checked"].configure(text=str(total_items))
            
            # Count notifications
            if "Notifications Sent" in self.stats_labels:
                self.stats_labels["Notifications Sent"].configure(text=str(len(self._notifications)))
            
            # Count new listings  
            if "New Listings" in self.stats_labels:
                new_count = sum(1 for n in self._notifications if n.get('title') == 'New Listing')
                self.stats_labels["New Listings"].configure(text=str(new_count))
        except Exception:
            pass  # Widget might be destroyed
    
    def get_config(self) -> Dict[str, Any]:
        """Get current watch configuration."""
        return {
            'categories': [cat for cat, var in self.game_vars.items() if var.get()],
            'min_price': self.min_price.get() if self.min_price else '',
            'max_price': self.max_price.get() if self.max_price else '',
            'stats': [stat for stat, var in self.stat_vars.items() if var.get()],
            'sound_enabled': self.sound_var.get() if hasattr(self, 'sound_var') else True,
            'desktop_notifications': self.desktop_var.get() if hasattr(self, 'desktop_var') else False,
            'interval': int(self.interval_slider.get()) if hasattr(self, 'interval_slider') else 30
        }
    
    def load_config(self, config: Dict[str, Any]):
        """Load watch configuration."""
        if 'categories' in config:
            for cat, var in self.game_vars.items():
                var.set(cat in config['categories'])
        
        if 'min_price' in config and self.min_price:
            self.min_price.delete(0, 'end')
            self.min_price.insert(0, config['min_price'])
        
        if 'max_price' in config and self.max_price:
            self.max_price.delete(0, 'end')
            self.max_price.insert(0, config['max_price'])
        
        if 'stats' in config:
            for stat, var in self.stat_vars.items():
                var.set(stat in config['stats'])
        
        if 'interval' in config and hasattr(self, 'interval_slider'):
            self.interval_slider.set(config['interval'])
            self._update_interval_label(config['interval'])
    
    def is_watching(self) -> bool:
        """Check if currently watching."""
        return self._is_watching
