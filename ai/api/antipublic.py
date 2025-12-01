"""
AntiPublic API Client - Integration with AntiPublic API
Documentation: https://antipublic.readme.io/reference/information
"""

from typing import Dict, Any, Optional, List
from .base import BaseAPIClient


class AntiPublicAPI(BaseAPIClient):
    """
    Client for the AntiPublic API.
    Provides access to data breach information and credential checking.
    """
    
    BASE_URL = "https://antipublic.one/api/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AntiPublic API client.
        
        Args:
            api_key: AntiPublic API key
        """
        super().__init__(api_key=api_key, base_url=self.BASE_URL)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with API key authentication."""
        headers = super()._get_headers()
        if self.api_key:
            headers['Authorization'] = self.api_key
        return headers
    
    # === Account & Information ===
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get account information and available queries.
        
        Returns:
            Account info including available queries count
        """
        return self.get('/info')
    
    def get_version(self) -> Dict[str, Any]:
        """
        Get current API version information.
        
        Returns:
            Version information
        """
        return self.get('/version')
    
    # === Email Checks ===
    
    def check_email(self, email: str) -> Dict[str, Any]:
        """
        Check if an email has been compromised in data breaches.
        
        Args:
            email: Email address to check
            
        Returns:
            Breach information for the email
        """
        return self.post('/emailSearch', data={'email': email})
    
    def check_emails_batch(self, emails: List[str]) -> Dict[str, Any]:
        """
        Check multiple emails for breaches.
        
        Args:
            emails: List of email addresses
            
        Returns:
            Breach information for all emails
        """
        return self.post('/emailSearchBatch', data={'emails': emails})
    
    # === Line Checks ===
    
    def check_lines(self, lines: List[str]) -> Dict[str, Any]:
        """
        Check credential lines (email:password format).
        
        Args:
            lines: List of credential lines
            
        Returns:
            Check results for each line
        """
        return self.post('/checkLines', data={'lines': lines})
    
    def count_lines(self, lines: List[str]) -> Dict[str, Any]:
        """
        Get count of public vs private lines.
        
        Args:
            lines: List of credential lines
            
        Returns:
            Count statistics
        """
        return self.post('/countLines', data={'lines': lines})
    
    # === Access Management ===
    
    def check_access(self) -> Dict[str, Any]:
        """
        Check API access status.
        
        Returns:
            Access status information
        """
        return self.get('/access')
    
    # === Statistics ===
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics about the breach database
        """
        return self.get('/stats')
    
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
        
        result = self.get_info()
        if result.get('success'):
            result['message'] = 'Connection successful'
        return result
    
    def get_remaining_queries(self) -> Optional[int]:
        """
        Get remaining query count.
        
        Returns:
            Number of remaining queries or None if unavailable
        """
        result = self.get_info()
        if result.get('success'):
            return result.get('data', {}).get('queries_left')
        return None
