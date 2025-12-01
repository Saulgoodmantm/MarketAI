"""
Portfolio Tab - View purchased items and account management
"""

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime


class PortfolioTab:
    """
    Portfolio tab for viewing purchased items, account balance, and managing inventory.
    """
    
    # Configuration constants
    MAX_ITEMS_DISPLAY = 50  # Maximum items to display in lists
    
    def __init__(self, parent, api_manager=None, on_notification: Optional[Callable] = None):
        """
        Initialize the Portfolio tab.
        
        Args:
            parent: Parent widget
            api_manager: API manager instance
            on_notification: Callback for notifications
        """
        self.parent = parent
        self.api_manager = api_manager
        self.on_notification = on_notification or (lambda x: None)
        
        # Portfolio data
        self._purchased_items = []
        self._balance = {'balance': 0, 'hold': 0}
        self._favorites = []
        self._last_refresh = None
        
        # Build UI
        self.frame = self._create_ui()
    
    def _create_ui(self):
        """Create the Portfolio tab UI."""
        if ctk is None:
            return None
            
        frame = ctk.CTkFrame(self.parent)
        
        # Header
        header = ctk.CTkFrame(frame)
        header.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            header,
            text="💼 PORTFOLIO",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)
        
        # Refresh button
        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            command=self._refresh_portfolio,
            width=100
        ).pack(side="right", padx=10)
        
        self.last_refresh_label = ctk.CTkLabel(
            header,
            text="Last refresh: Never",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.last_refresh_label.pack(side="right", padx=10)
        
        # Main content
        content = ctk.CTkFrame(frame)
        content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top row - Account summary
        summary_frame = ctk.CTkFrame(content, height=100)
        summary_frame.pack(fill="x", padx=5, pady=5)
        summary_frame.pack_propagate(False)
        
        self._create_summary_cards(summary_frame)
        
        # Content area with tabs
        tabs = ctk.CTkTabview(content)
        tabs.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Purchased items tab
        purchased_tab = tabs.add("📦 Purchased Items")
        self._create_purchased_view(purchased_tab)
        
        # Favorites tab
        favorites_tab = tabs.add("⭐ Favorites")
        self._create_favorites_view(favorites_tab)
        
        # Transaction History tab
        history_tab = tabs.add("📜 History")
        self._create_history_view(history_tab)
        
        return frame
    
    def _create_summary_cards(self, parent):
        """Create account summary cards."""
        if ctk is None:
            return
        
        self.summary_labels = {}
        
        cards = [
            ("💰 Balance", "$0.00", "#2ECC71"),
            ("🔒 On Hold", "$0.00", "#F39C12"),
            ("📦 Items Owned", "0", "#00D4FF"),
            ("⭐ Favorites", "0", "#9B59B6")
        ]
        
        for title, value, color in cards:
            card = ctk.CTkFrame(parent)
            card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=11),
                text_color="#888888"
            ).pack(pady=(15, 2))
            
            self.summary_labels[title] = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            )
            self.summary_labels[title].pack(pady=(2, 15))
    
    def _create_purchased_view(self, parent):
        """Create purchased items view."""
        if ctk is None:
            return
        
        # Items list
        self.purchased_frame = ctk.CTkScrollableFrame(parent)
        self.purchased_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Placeholder
        self.no_items_label = ctk.CTkLabel(
            self.purchased_frame,
            text="No purchased items found\nConfigure your API key in Settings to view your inventory",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.no_items_label.pack(pady=50)
    
    def _create_favorites_view(self, parent):
        """Create favorites view."""
        if ctk is None:
            return
        
        # Favorites list
        self.favorites_frame = ctk.CTkScrollableFrame(parent)
        self.favorites_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Placeholder
        ctk.CTkLabel(
            self.favorites_frame,
            text="No favorites yet\nAdd items to your favorites from the Market Watch tab",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=50)
    
    def _create_history_view(self, parent):
        """Create transaction history view."""
        if ctk is None:
            return
        
        # History list
        self.history_frame = ctk.CTkScrollableFrame(parent)
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Placeholder
        ctk.CTkLabel(
            self.history_frame,
            text="No transaction history available\nConfigure your API key to view transaction history",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=50)
    
    def _refresh_portfolio(self):
        """Refresh portfolio data from APIs."""
        if not self.api_manager:
            return
        
        threading.Thread(target=self._fetch_portfolio_data, daemon=True).start()
    
    def _fetch_portfolio_data(self):
        """Fetch portfolio data from APIs in background."""
        try:
            # Get balance
            if self.api_manager.lzt_market.is_configured():
                balance_result = self.api_manager.lzt_market.get_balance()
                if balance_result.get('success'):
                    self._balance = {
                        'balance': balance_result.get('balance', 0),
                        'hold': balance_result.get('hold', 0)
                    }
                
                # Get purchased items
                purchased_result = self.api_manager.lzt_market.get_purchased_items()
                if purchased_result.get('success'):
                    self._purchased_items = purchased_result.get('data', {}).get('items', [])
                
                # Get favorites
                favorites_result = self.api_manager.lzt_market.get_favorites()
                if favorites_result.get('success'):
                    self._favorites = favorites_result.get('data', {}).get('items', [])
            
            # Update UI
            self._update_portfolio_ui()
            self._last_refresh = datetime.now()
            
            if hasattr(self, 'last_refresh_label') and ctk:
                self.last_refresh_label.configure(
                    text=f"Last refresh: {self._last_refresh.strftime('%H:%M:%S')}"
                )
            
        except Exception as e:
            print(f"[Portfolio] Error fetching data: {e}")
    
    def _update_portfolio_ui(self):
        """Update portfolio UI with fetched data."""
        if not ctk:
            return
        
        try:
            # Update summary cards
            if hasattr(self, 'summary_labels'):
                self.summary_labels["💰 Balance"].configure(
                    text=f"${self._balance.get('balance', 0):.2f}"
                )
                self.summary_labels["🔒 On Hold"].configure(
                    text=f"${self._balance.get('hold', 0):.2f}"
                )
                self.summary_labels["📦 Items Owned"].configure(
                    text=str(len(self._purchased_items))
                )
                self.summary_labels["⭐ Favorites"].configure(
                    text=str(len(self._favorites))
                )
            
            # Update purchased items list
            if hasattr(self, 'purchased_frame') and self._purchased_items:
                # Clear existing widgets
                for widget in self.purchased_frame.winfo_children():
                    widget.destroy()
                
                # Add items (limited to MAX_ITEMS_DISPLAY)
                for item in self._purchased_items[:self.MAX_ITEMS_DISPLAY]:
                    self._add_item_card(self.purchased_frame, item)
            
            # Update favorites list
            if hasattr(self, 'favorites_frame') and self._favorites:
                for widget in self.favorites_frame.winfo_children():
                    widget.destroy()
                
                for item in self._favorites[:self.MAX_ITEMS_DISPLAY]:
                    self._add_item_card(self.favorites_frame, item, is_favorite=True)
                    
        except Exception as e:
            print(f"[Portfolio] Error updating UI: {e}")
    
    def _add_item_card(self, parent, item: Dict, is_favorite: bool = False):
        """Add an item card to a frame."""
        if not ctk:
            return
        
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=5, pady=3)
        
        # Item info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        title = item.get('title', 'Unknown Item')[:50]
        ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        category = item.get('category', 'N/A')
        ctk.CTkLabel(
            info_frame,
            text=f"Category: {category}",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(anchor="w")
        
        # Price
        price = item.get('price', 0)
        ctk.CTkLabel(
            card,
            text=f"${price:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ECC71"
        ).pack(side="right", padx=10, pady=5)
        
        # Favorite indicator
        if is_favorite:
            ctk.CTkLabel(
                card,
                text="⭐",
                font=ctk.CTkFont(size=14)
            ).pack(side="right", padx=5)
    
    def get_portfolio_data(self) -> Dict[str, Any]:
        """Get current portfolio data."""
        return {
            'balance': self._balance,
            'purchased_items_count': len(self._purchased_items),
            'favorites_count': len(self._favorites),
            'last_refresh': self._last_refresh.isoformat() if self._last_refresh else None
        }

