"""
Autobuy Tab - Automated purchasing functionality (disabled by default)
Note: This tab is disabled by default and the enabled state is never saved to settings.
"""

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

from typing import Dict, Any, Optional, Callable
from datetime import datetime


class AutobuyTab:
    """
    Autobuy tab for automated market purchases.
    
    IMPORTANT: This tab is disabled by default and the enabled state
    is never persisted to settings for safety reasons.
    """
    
    def __init__(self, parent, api_manager=None, on_log: Optional[Callable] = None):
        """
        Initialize the Autobuy tab.
        
        Args:
            parent: Parent widget
            api_manager: API manager instance
            on_log: Callback for logging messages
        """
        self.parent = parent
        self.api_manager = api_manager
        self.on_log = on_log or (lambda x: None)
        
        # CRITICAL: Always disabled by default, never saved
        self._enabled = False
        self._running = False
        
        # Autobuy configuration (volatile, not persisted)
        self._config = {
            'categories': [],
            'max_price': 0.0,
            'min_price': 0.0,
            'keywords': [],
            'auto_confirm': False,
            'delay_seconds': 5
        }
        
        # Activity log
        self._activity_log = []
        
        # Build UI
        self.frame = self._create_ui()
        
    def _create_ui(self):
        """Create the Autobuy tab UI."""
        if ctk is None:
            return None
            
        frame = ctk.CTkFrame(self.parent)
        
        # Header with warning
        header = ctk.CTkFrame(frame)
        header.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            header,
            text="🤖 AUTOBUY",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)
        
        warning_label = ctk.CTkLabel(
            header,
            text="⚠️ Disabled by default - Use with caution!",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B6B"
        )
        warning_label.pack(side="right", padx=10)
        
        # Main content in two columns
        content = ctk.CTkFrame(frame)
        content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left column - Configuration
        left_col = ctk.CTkFrame(content)
        left_col.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self._create_config_section(left_col)
        
        # Right column - Status and Log
        right_col = ctk.CTkFrame(content)
        right_col.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self._create_status_section(right_col)
        
        return frame
    
    def _create_config_section(self, parent):
        """Create configuration section."""
        if ctk is None:
            return
            
        # Enable/Disable toggle
        toggle_frame = ctk.CTkFrame(parent)
        toggle_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            toggle_frame,
            text="Autobuy Status:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        self.enable_switch = ctk.CTkSwitch(
            toggle_frame,
            text="Enable Autobuy",
            command=self._toggle_enabled,
            onvalue=True,
            offvalue=False
        )
        self.enable_switch.pack(side="left", padx=10)
        # Ensure disabled by default
        self.enable_switch.deselect()
        
        self.status_indicator = ctk.CTkLabel(
            toggle_frame,
            text="● DISABLED",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FF6B6B"
        )
        self.status_indicator.pack(side="right", padx=10)
        
        # Category selection
        cat_frame = ctk.CTkFrame(parent)
        cat_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            cat_frame,
            text="Target Categories:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        # Category checkboxes
        categories = ['steam', 'fortnite', 'origin', 'valorant', 'genshin-impact', 'telegram']
        self.category_vars = {}
        
        cat_grid = ctk.CTkFrame(cat_frame)
        cat_grid.pack(fill="x", padx=5, pady=5)
        
        for i, cat in enumerate(categories):
            var = ctk.BooleanVar(value=False)
            self.category_vars[cat] = var
            cb = ctk.CTkCheckBox(
                cat_grid,
                text=cat.capitalize(),
                variable=var,
                command=self._update_categories
            )
            cb.grid(row=i//3, column=i%3, padx=10, pady=2, sticky="w")
        
        # Price range
        price_frame = ctk.CTkFrame(parent)
        price_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            price_frame,
            text="Price Range:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        price_inputs = ctk.CTkFrame(price_frame)
        price_inputs.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(price_inputs, text="Min:").pack(side="left", padx=5)
        self.min_price_entry = ctk.CTkEntry(price_inputs, width=80, placeholder_text="0.00")
        self.min_price_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(price_inputs, text="Max:").pack(side="left", padx=5)
        self.max_price_entry = ctk.CTkEntry(price_inputs, width=80, placeholder_text="100.00")
        self.max_price_entry.pack(side="left", padx=5)
        
        # Keywords filter
        kw_frame = ctk.CTkFrame(parent)
        kw_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            kw_frame,
            text="Keywords (comma separated):",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=5, pady=2)
        
        self.keywords_entry = ctk.CTkEntry(kw_frame, placeholder_text="Enter keywords...")
        self.keywords_entry.pack(fill="x", padx=5, pady=5)
        
        # Auto-confirm option
        self.auto_confirm_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            parent,
            text="Auto-confirm purchases (RISKY!)",
            variable=self.auto_confirm_var,
            text_color="#FF6B6B"
        ).pack(anchor="w", padx=15, pady=5)
        
        # Start/Stop buttons
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Start Autobuy",
            command=self._start_autobuy,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            state="disabled"
        )
        self.start_btn.pack(side="left", padx=10, pady=5, expand=True, fill="x")
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Stop",
            command=self._stop_autobuy,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=10, pady=5, expand=True, fill="x")
    
    def _create_status_section(self, parent):
        """Create status and log section."""
        if ctk is None:
            return
            
        # Status display
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="Current Status",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=5, pady=5)
        
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="Autobuy is disabled",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.pack(anchor="w", padx=10, pady=5)
        
        # Statistics
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        stats = [
            ("Items Checked:", "0"),
            ("Purchases Made:", "0"),
            ("Total Spent:", "$0.00"),
            ("Session Time:", "00:00:00")
        ]
        
        self.stat_labels = {}
        for label, value in stats:
            row = ctk.CTkFrame(stats_frame)
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=11)).pack(side="left")
            self.stat_labels[label] = ctk.CTkLabel(
                row, 
                text=value, 
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#00D4FF"
            )
            self.stat_labels[label].pack(side="right")
        
        # Activity log
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            log_frame,
            text="Activity Log",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=5, pady=5)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.configure(state="disabled")
        
        # Clear log button
        ctk.CTkButton(
            log_frame,
            text="Clear Log",
            command=self._clear_log,
            height=25,
            font=ctk.CTkFont(size=10)
        ).pack(anchor="e", padx=5, pady=5)
    
    def _toggle_enabled(self):
        """Toggle autobuy enabled state."""
        self._enabled = self.enable_switch.get()
        
        if self._enabled:
            self.status_indicator.configure(text="● ENABLED", text_color="#2ECC71")
            self.start_btn.configure(state="normal")
            self._add_log("Autobuy ENABLED - Ready to start")
        else:
            self.status_indicator.configure(text="● DISABLED", text_color="#FF6B6B")
            self.start_btn.configure(state="disabled")
            self._stop_autobuy()
            self._add_log("Autobuy DISABLED")
    
    def _update_categories(self):
        """Update selected categories."""
        self._config['categories'] = [
            cat for cat, var in self.category_vars.items() if var.get()
        ]
    
    def _start_autobuy(self):
        """Start the autobuy process."""
        if not self._enabled:
            self._add_log("Cannot start - Autobuy is disabled")
            return
        
        # Validate configuration
        try:
            min_price = float(self.min_price_entry.get() or 0)
            max_price = float(self.max_price_entry.get() or 0)
        except ValueError:
            self._add_log("ERROR: Invalid price values")
            return
        
        if not self._config['categories']:
            self._add_log("ERROR: No categories selected")
            return
        
        if max_price > 0 and min_price > max_price:
            self._add_log("ERROR: Min price cannot be greater than max price")
            return
        
        self._config['min_price'] = min_price
        self._config['max_price'] = max_price
        self._config['keywords'] = [
            k.strip() for k in self.keywords_entry.get().split(',') if k.strip()
        ]
        self._config['auto_confirm'] = self.auto_confirm_var.get()
        
        self._running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_text.configure(text="Autobuy is RUNNING...")
        
        self._add_log("=" * 40)
        self._add_log("AUTOBUY STARTED")
        self._add_log(f"Categories: {', '.join(self._config['categories'])}")
        self._add_log(f"Price range: ${min_price:.2f} - ${max_price:.2f}")
        if self._config['keywords']:
            self._add_log(f"Keywords: {', '.join(self._config['keywords'])}")
        self._add_log("=" * 40)
        
        # Note: Actual autobuy logic would run in a separate thread
        # This is a placeholder for the UI logic
    
    def _stop_autobuy(self):
        """Stop the autobuy process."""
        if self._running:
            self._running = False
            self.stop_btn.configure(state="disabled")
            if self._enabled:
                self.start_btn.configure(state="normal")
            self.status_text.configure(text="Autobuy stopped")
            self._add_log("AUTOBUY STOPPED")
    
    def _add_log(self, message: str):
        """Add message to activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self._activity_log.append(log_entry)
        
        if self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", log_entry + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        
        # Also call external log callback
        self.on_log(log_entry)
    
    def _clear_log(self):
        """Clear the activity log."""
        self._activity_log = []
        if self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.
        
        Note: Enabled state is NOT included as it should never be saved.
        """
        return {
            'categories': self._config['categories'],
            'min_price': self._config['min_price'],
            'max_price': self._config['max_price'],
            'keywords': self._config['keywords'],
            # Deliberately NOT including enabled state
        }
    
    def load_config(self, config: Dict[str, Any]):
        """
        Load configuration (but NOT enabled state).
        
        Args:
            config: Configuration dictionary
        """
        # Load settings but NEVER enable from saved config
        if 'categories' in config:
            for cat in config['categories']:
                if cat in self.category_vars:
                    self.category_vars[cat].set(True)
            self._config['categories'] = config['categories']
        
        if 'min_price' in config:
            self.min_price_entry.delete(0, 'end')
            self.min_price_entry.insert(0, str(config['min_price']))
            self._config['min_price'] = config['min_price']
        
        if 'max_price' in config:
            self.max_price_entry.delete(0, 'end')
            self.max_price_entry.insert(0, str(config['max_price']))
            self._config['max_price'] = config['max_price']
        
        # CRITICAL: Never restore enabled state
        self._enabled = False
        self.enable_switch.deselect()
        self.status_indicator.configure(text="● DISABLED", text_color="#FF6B6B")
        self.start_btn.configure(state="disabled")
    
    def is_enabled(self) -> bool:
        """Check if autobuy is enabled (runtime only, never persisted)."""
        return self._enabled
    
    def is_running(self) -> bool:
        """Check if autobuy is currently running."""
        return self._running
