"""
LZT Market API Client - Integration with LZT Market
Documentation: https://lzt-market.readme.io/reference/information
"""

from typing import Dict, Any, Optional, List
from .base import BaseAPIClient


class LZTMarketAPI(BaseAPIClient):
    """
    Client for the LZT Market API.
    Provides access to digital marketplace functionality including
    account listings, purchases, and market data.
    """
    
    BASE_URL = "https://api.lzt.market"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LZT Market API client.
        
        Args:
            api_key: LZT Market API key
        """
        super().__init__(api_key=api_key, base_url=self.BASE_URL)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with Bearer token authentication."""
        headers = super()._get_headers()
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    # === Profile & Information ===
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get current user profile information.
        
        Returns:
            User profile data
        """
        return self.get('/me')
    
    def get_market_info(self) -> Dict[str, Any]:
        """
        Get general market information.
        
        Returns:
            Market info and stats
        """
        return self.get('/info')
    
    # === Category Listings ===
    
    def list_categories(self) -> Dict[str, Any]:
        """
        Get all available categories.
        
        Returns:
            List of market categories
        """
        return self.get('/category')
    
    def get_category_items(
        self, 
        category_name: str,
        page: int = 1,
        order_by: str = 'pdate_to_down'
    ) -> Dict[str, Any]:
        """
        Get items from a specific category.
        
        Args:
            category_name: Name of the category (e.g., 'steam', 'origin', 'fortnite')
            page: Page number for pagination
            order_by: Sorting order
            
        Returns:
            List of items in the category
        """
        return self.get(f'/{category_name}', params={
            'page': page,
            'order_by': order_by
        })
    
    # === Popular Categories ===
    
    def get_steam_accounts(self, page: int = 1) -> Dict[str, Any]:
        """Get Steam accounts for sale."""
        return self.get_category_items('steam', page)
    
    def get_fortnite_accounts(self, page: int = 1) -> Dict[str, Any]:
        """Get Fortnite accounts for sale."""
        return self.get_category_items('fortnite', page)
    
    def get_origin_accounts(self, page: int = 1) -> Dict[str, Any]:
        """Get Origin/EA accounts for sale."""
        return self.get_category_items('origin', page)
    
    def get_valorant_accounts(self, page: int = 1) -> Dict[str, Any]:
        """Get Valorant accounts for sale."""
        return self.get_category_items('valorant', page)
    
    def get_genshin_accounts(self, page: int = 1) -> Dict[str, Any]:
        """Get Genshin Impact accounts for sale."""
        return self.get_category_items('genshin-impact', page)
    
    def get_telegram_accounts(self, page: int = 1) -> Dict[str, Any]:
        """Get Telegram accounts for sale."""
        return self.get_category_items('telegram', page)
    
    # === Item Details ===
    
    def get_item(self, item_id: int) -> Dict[str, Any]:
        """
        Get details of a specific item.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item details
        """
        return self.get(f'/item/{item_id}')
    
    def get_item_steam_value(self, item_id: int) -> Dict[str, Any]:
        """
        Get Steam inventory value for an item.
        
        Args:
            item_id: Item ID
            
        Returns:
            Steam inventory value data
        """
        return self.get(f'/item/{item_id}/steam-value')
    
    # === Search & Filtering ===
    
    def search(
        self,
        category: Optional[str] = None,
        pmin: Optional[float] = None,
        pmax: Optional[float] = None,
        title: Optional[str] = None,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for items in the market.
        
        Args:
            category: Category to search in
            pmin: Minimum price
            pmax: Maximum price
            title: Title keyword
            page: Page number
            
        Returns:
            Search results
        """
        params = {'page': page}
        if category:
            params['category'] = category
        if pmin is not None:
            params['pmin'] = pmin
        if pmax is not None:
            params['pmax'] = pmax
        if title:
            params['title'] = title
            
        return self.get('/search', params=params)
    
    # === Purchasing ===
    
    def fast_buy(self, item_id: int, price: float) -> Dict[str, Any]:
        """
        Perform fast purchase of an item.
        
        Args:
            item_id: Item ID to purchase
            price: Expected price
            
        Returns:
            Purchase result
        """
        return self.post(f'/item/{item_id}/fast-buy', data={'price': price})
    
    def check_item(self, item_id: int) -> Dict[str, Any]:
        """
        Check item availability and status before purchase.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item availability status
        """
        return self.post(f'/item/{item_id}/check-account')
    
    def confirm_buy(self, item_id: int) -> Dict[str, Any]:
        """
        Confirm purchase of an item.
        
        Args:
            item_id: Item ID
            
        Returns:
            Purchase confirmation
        """
        return self.post(f'/item/{item_id}/confirm-buy')
    
    # === User Inventory ===
    
    def get_purchased_items(self, page: int = 1) -> Dict[str, Any]:
        """
        Get items purchased by the user.
        
        Args:
            page: Page number
            
        Returns:
            List of purchased items
        """
        return self.get('/purchased', params={'page': page})
    
    def get_listed_items(self, page: int = 1) -> Dict[str, Any]:
        """
        Get items listed for sale by the user.
        
        Args:
            page: Page number
            
        Returns:
            List of listed items
        """
        return self.get('/user/items', params={'page': page})
    
    # === Favorites & Watchlist ===
    
    def add_to_favorites(self, item_id: int) -> Dict[str, Any]:
        """Add item to favorites."""
        return self.post(f'/item/{item_id}/star')
    
    def remove_from_favorites(self, item_id: int) -> Dict[str, Any]:
        """Remove item from favorites."""
        return self.delete(f'/item/{item_id}/star')
    
    def get_favorites(self, page: int = 1) -> Dict[str, Any]:
        """Get favorite items."""
        return self.get('/fave', params={'page': page})
    
    # === Payments ===
    
    def get_payments(self, page: int = 1) -> Dict[str, Any]:
        """
        Get payment history.
        
        Args:
            page: Page number
            
        Returns:
            Payment history
        """
        return self.get('/payments', params={'page': page})
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get current balance.
        
        Returns:
            Balance information
        """
        result = self.get_me()
        if result.get('success'):
            data = result.get('data', {})
            return {
                'success': True,
                'balance': data.get('balance', 0),
                'hold': data.get('hold', 0)
            }
        return result
    
    # === Utility Methods ===
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection and authentication.
        
        Returns:
            Connection test results
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'not_configured',
                'message': 'API key not set'
            }
        
        result = self.get_me()
        if result.get('success'):
            result['message'] = 'Connection successful'
        return result
    
    def get_market_stats(self) -> Dict[str, Any]:
        """
        Get aggregated market statistics.
        
        Returns:
            Market statistics for AI learning
        """
        stats = {
            'categories': {},
            'timestamp': None
        }
        
        # Get basic market info
        info_result = self.get_market_info()
        if info_result.get('success'):
            stats.update(info_result.get('data', {}))
        
        return stats
