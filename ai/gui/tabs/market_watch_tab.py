"""
Market Watch Tab - Monitor market listings and receive notifications
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
    Replaces the autobuy notify feature with customizable watch settings.
    """
    
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
        
        # Market data cache
        self._market_data = {}
        self._last_update = None
        
        # Build UI
        self.frame = self._create_ui()
    
    def _create_ui(self):
        """Create the Market Watch tab UI."""
        if ctk is None:
            return None
            
        frame = ctk.CTkFrame(self.parent)
        
        # Header
        header = ctk.CTkFrame(frame)
        header.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            header,
            text="👁️ MARKET WATCH",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)
        
        self.status_label = ctk.CTkLabel(
            header,
            text="● Not Watching",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.status_label.pack(side="right", padx=10)
        
        # Main content
        content = ctk.CTkFrame(frame)
        content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left column - Watch List Configuration
        left_col = ctk.CTkFrame(content, width=350)
        left_col.pack(side="left", fill="y", padx=5, pady=5)
        left_col.pack_propagate(False)
        
        self._create_watch_config(left_col)
        
        # Right column - Market View and Notifications
        right_col = ctk.CTkFrame(content)
        right_col.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self._create_market_view(right_col)
        
        return frame
    
    def _create_watch_config(self, parent):
        """Create watch configuration section."""
        if ctk is None:
            return
            
        # Title
        ctk.CTkLabel(
            parent,
            text="Watch Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        # Game/Category selection
        cat_frame = ctk.CTkFrame(parent)
        cat_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            cat_frame,
            text="Select Games/Categories:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        # Scrollable category list
        cat_scroll = ctk.CTkScrollableFrame(cat_frame, height=150)
        cat_scroll.pack(fill="x", padx=5, pady=5)
        
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
        
        for name, key, icon in games:
            var = ctk.BooleanVar(value=False)
            self.game_vars[key] = var
            ctk.CTkCheckBox(
                cat_scroll,
                text=f"{icon} {name}",
                variable=var
            ).pack(anchor="w", padx=5, pady=2)
        
        # Price filter
        price_frame = ctk.CTkFrame(parent)
        price_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            price_frame,
            text="Price Range:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        price_row = ctk.CTkFrame(price_frame)
        price_row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(price_row, text="$").pack(side="left")
        self.min_price = ctk.CTkEntry(price_row, width=70, placeholder_text="Min")
        self.min_price.pack(side="left", padx=2)
        
        ctk.CTkLabel(price_row, text=" - $").pack(side="left")
        self.max_price = ctk.CTkEntry(price_row, width=70, placeholder_text="Max")
        self.max_price.pack(side="left", padx=2)
        
        # Stats to watch
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            stats_frame,
            text="Stats to Watch:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        self.stat_vars = {}
        stats = [
            ('New Listings', 'new_listings'),
            ('Price Drops', 'price_drops'),
            ('High Value Items', 'high_value'),
            ('Rare Items', 'rare_items'),
            ('Trusted Sellers', 'trusted_sellers')
        ]
        
        for name, key in stats:
            var = ctk.BooleanVar(value=key == 'new_listings')
            self.stat_vars[key] = var
            ctk.CTkCheckBox(
                stats_frame,
                text=name,
                variable=var
            ).pack(anchor="w", padx=10, pady=1)
        
        # Notification settings
        notif_frame = ctk.CTkFrame(parent)
        notif_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            notif_frame,
            text="Notification Settings:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        self.sound_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            notif_frame,
            text="Sound alerts",
            variable=self.sound_var
        ).pack(anchor="w", padx=10, pady=1)
        
        self.desktop_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            notif_frame,
            text="Desktop notifications",
            variable=self.desktop_var
        ).pack(anchor="w", padx=10, pady=1)
        
        # Update interval
        interval_frame = ctk.CTkFrame(parent)
        interval_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            interval_frame,
            text="Update Interval (seconds):",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        self.interval_slider = ctk.CTkSlider(
            interval_frame,
            from_=10,
            to=300,
            number_of_steps=58,
            command=self._update_interval_label
        )
        self.interval_slider.set(30)
        self.interval_slider.pack(fill="x", padx=5, pady=2)
        
        self.interval_label = ctk.CTkLabel(
            interval_frame,
            text="30 seconds",
            font=ctk.CTkFont(size=10)
        )
        self.interval_label.pack(anchor="w", padx=5)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Start Watching",
            command=self._start_watching,
            fg_color="#2ECC71",
            hover_color="#27AE60"
        )
        self.start_btn.pack(fill="x", padx=5, pady=2)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Stop Watching",
            command=self._stop_watching,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            state="disabled"
        )
        self.stop_btn.pack(fill="x", padx=5, pady=2)
    
    def _create_market_view(self, parent):
        """Create market view and notifications section."""
        if ctk is None:
            return
            
        # Tab view for Market and Notifications
        tabs = ctk.CTkTabview(parent)
        tabs.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Market Listings tab
        market_tab = tabs.add("📊 Market Listings")
        self._create_market_listings(market_tab)
        
        # Notifications tab
        notif_tab = tabs.add("🔔 Notifications")
        self._create_notifications_view(notif_tab)
        
        # Statistics tab
        stats_tab = tabs.add("📈 Statistics")
        self._create_statistics_view(stats_tab)
    
    def _create_market_listings(self, parent):
        """Create market listings view."""
        if ctk is None:
            return
            
        # Header with refresh
        header = ctk.CTkFrame(parent)
        header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            header,
            text="Current Market Listings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        self.last_update_label = ctk.CTkLabel(
            header,
            text="Last update: Never",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.last_update_label.pack(side="right", padx=5)
        
        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            command=self._refresh_market,
            width=80,
            height=25,
            font=ctk.CTkFont(size=10)
        ).pack(side="right", padx=5)
        
        # Listings display
        self.listings_frame = ctk.CTkScrollableFrame(parent)
        self.listings_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Placeholder
        ctk.CTkLabel(
            self.listings_frame,
            text="Select categories and start watching to see listings",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=50)
    
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
        self.interval_label.configure(text=f"{int(value)} seconds")
    
    def _start_watching(self):
        """Start market watching."""
        # Get selected categories
        categories = [cat for cat, var in self.game_vars.items() if var.get()]
        
        if not categories:
            self._add_notification("Warning", "Please select at least one category to watch", "warning")
            return
        
        self._is_watching = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="● Watching...", text_color="#2ECC71")
        
        # Start watching thread
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()
        
        self._add_notification("Started", f"Now watching: {', '.join(categories)}", "info")
    
    def _stop_watching(self):
        """Stop market watching."""
        self._is_watching = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="● Stopped", text_color="#888888")
        
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
        """Check market for updates."""
        if not self.api_manager:
            return
        
        categories = [cat for cat, var in self.game_vars.items() if var.get()]
        
        for category in categories:
            try:
                result = self.api_manager.get_category_data(category, 1)
                if result.get('success'):
                    items = result.get('data', {}).get('items', [])
                    self._process_market_items(category, items)
            except Exception as e:
                print(f"[Market Check Error] {category}: {e}")
        
        self._last_update = datetime.now()
        if self.last_update_label:
            self.last_update_label.configure(
                text=f"Last update: {self._last_update.strftime('%H:%M:%S')}"
            )
    
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
                    if self.stat_vars.get('new_listings', ctk.BooleanVar()).get():
                        self._add_notification(
                            "New Listing",
                            f"[{category}] {item.get('title', 'Unknown')} - ${price:.2f}",
                            "new"
                        )
                
                # Store item
                if category not in self._market_data:
                    self._market_data[category] = {}
                self._market_data[category][item_id] = item
    
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
