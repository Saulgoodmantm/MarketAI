"""
API Manager - Centralized management of all API integrations
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from .antipublic import AntiPublicAPI
from .lzt_market import LZTMarketAPI
from .lolzteam import LolzTeamAPI


class APIManager:
    """
    Centralized manager for all API integrations.
    Handles API configuration, authentication, and data aggregation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the API manager.
        
        Args:
            config_path: Path to API configuration file
        """
        self.config_path = Path(config_path) if config_path else Path("shared_data/api_config.json")
        
        # Initialize API clients
        self.antipublic = AntiPublicAPI()
        self.lzt_market = LZTMarketAPI()
        self.lolzteam = LolzTeamAPI()
        
        # Load saved configuration
        self._load_config()
        
    def _load_config(self):
        """Load API configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Set API keys from config
                if config.get('antipublic_key'):
                    self.antipublic.set_api_key(config['antipublic_key'])
                if config.get('lzt_market_key'):
                    self.lzt_market.set_api_key(config['lzt_market_key'])
                if config.get('lolzteam_key'):
                    self.lolzteam.set_api_key(config['lolzteam_key'])
                    
            except Exception as e:
                print(f"[WARNING] Failed to load API config: {e}")
    
    def save_config(self):
        """Save current API configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'antipublic_key': self.antipublic.api_key or '',
                'lzt_market_key': self.lzt_market.api_key or '',
                'lolzteam_key': self.lolzteam.api_key or '',
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save API config: {e}")
            return False
    
    def set_api_key(self, api_name: str, api_key: str) -> bool:
        """
        Set API key for a specific API.
        
        Args:
            api_name: Name of the API ('antipublic', 'lzt_market', 'lolzteam')
            api_key: API key value
            
        Returns:
            True if successful
        """
        api_map = {
            'antipublic': self.antipublic,
            'lzt_market': self.lzt_market,
            'lolzteam': self.lolzteam
        }
        
        if api_name in api_map:
            api_map[api_name].set_api_key(api_key)
            return True
        return False
    
    def test_all_connections(self) -> Dict[str, Any]:
        """
        Test connections to all configured APIs.
        
        Returns:
            Results for each API
        """
        results = {}
        
        if self.antipublic.is_configured():
            results['antipublic'] = self.antipublic.test_connection()
        else:
            results['antipublic'] = {'success': False, 'message': 'Not configured'}
        
        if self.lzt_market.is_configured():
            results['lzt_market'] = self.lzt_market.test_connection()
        else:
            results['lzt_market'] = {'success': False, 'message': 'Not configured'}
        
        if self.lolzteam.is_configured():
            results['lolzteam'] = self.lolzteam.test_connection()
        else:
            results['lolzteam'] = {'success': False, 'message': 'Not configured'}
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all API connections.
        
        Returns:
            Status for each API
        """
        return {
            'antipublic': {
                'configured': self.antipublic.is_configured(),
                'status': self.antipublic.get_status()
            },
            'lzt_market': {
                'configured': self.lzt_market.is_configured(),
                'status': self.lzt_market.get_status()
            },
            'lolzteam': {
                'configured': self.lolzteam.is_configured(),
                'status': self.lolzteam.get_status()
            }
        }
    
    # === Aggregated Market Data ===
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get aggregated market overview from all sources.
        
        Returns:
            Combined market data for AI analysis
        """
        overview = {
            'timestamp': datetime.now().isoformat(),
            'sources': {},
            'aggregated': {}
        }
        
        # Get LZT Market data
        if self.lzt_market.is_configured():
            try:
                market_info = self.lzt_market.get_market_info()
                if market_info.get('success'):
                    overview['sources']['lzt_market'] = market_info.get('data', {})
            except Exception as e:
                overview['sources']['lzt_market'] = {'error': str(e)}
        
        # Get LolzTeam forum data
        if self.lolzteam.is_configured():
            try:
                forum_stats = self.lolzteam.get_forum_stats()
                overview['sources']['lolzteam'] = forum_stats
            except Exception as e:
                overview['sources']['lolzteam'] = {'error': str(e)}
        
        return overview
    
    def get_market_listings(
        self,
        category: Optional[str] = None,
        page: int = 1,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get market listings with optional filters.
        
        Args:
            category: Category filter
            page: Page number
            min_price: Minimum price filter
            max_price: Maximum price filter
            
        Returns:
            List of market items
        """
        if not self.lzt_market.is_configured():
            return {'success': False, 'message': 'LZT Market not configured'}
        
        return self.lzt_market.search(
            category=category,
            page=page,
            pmin=min_price,
            pmax=max_price
        )
    
    def get_category_data(self, category: str, page: int = 1) -> Dict[str, Any]:
        """
        Get data for a specific market category.
        
        Args:
            category: Category name
            page: Page number
            
        Returns:
            Category items
        """
        if not self.lzt_market.is_configured():
            return {'success': False, 'message': 'LZT Market not configured'}
        
        return self.lzt_market.get_category_items(category, page)
    
    # === Data Collection for AI ===
    
    def collect_training_data(self) -> Dict[str, Any]:
        """
        Collect market data for AI training.
        
        Returns:
            Collected data samples
        """
        training_data = {
            'timestamp': datetime.now().isoformat(),
            'samples': [],
            'sources': []
        }
        
        # Collect from LZT Market
        if self.lzt_market.is_configured():
            try:
                # Get various category data
                categories = ['steam', 'fortnite', 'valorant', 'genshin-impact']
                for cat in categories:
                    result = self.lzt_market.get_category_items(cat, 1)
                    if result.get('success'):
                        items = result.get('data', {}).get('items', [])
                        for item in items[:10]:  # Limit to 10 per category
                            training_data['samples'].append({
                                'type': 'market_listing',
                                'category': cat,
                                'data': item,
                                'source': 'lzt_market'
                            })
                training_data['sources'].append('lzt_market')
            except Exception as e:
                print(f"[WARNING] LZT Market collection failed: {e}")
        
        # Collect from LolzTeam
        if self.lolzteam.is_configured():
            try:
                # Get recent threads
                result = self.lolzteam.get_threads(page=1)
                if result.get('success'):
                    threads = result.get('data', {}).get('threads', [])
                    for thread in threads[:10]:
                        training_data['samples'].append({
                            'type': 'forum_thread',
                            'data': thread,
                            'source': 'lolzteam'
                        })
                training_data['sources'].append('lolzteam')
            except Exception as e:
                print(f"[WARNING] LolzTeam collection failed: {e}")
        
        return training_data
    
    def get_available_categories(self) -> List[str]:
        """
        Get list of available market categories.
        
        Returns:
            List of category names
        """
        categories = [
            'steam', 'fortnite', 'origin', 'valorant', 
            'genshin-impact', 'telegram', 'vk', 'discord',
            'instagram', 'tiktok', 'twitter', 'youtube'
        ]
        return categories
