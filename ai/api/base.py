"""
Base API Client - Common functionality for all API integrations
"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAPIClient:
    """Base class for API clients with common functionality."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = ""):
        """
        Initialize the API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self._last_request_time: Optional[datetime] = None
        self._request_count = 0
        
    def set_api_key(self, api_key: str):
        """Set the API key."""
        self.api_key = api_key
        
    def is_configured(self) -> bool:
        """Check if API is configured with a valid key."""
        return bool(self.api_key)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            Response data or error dict
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)
        
        try:
            self._last_request_time = datetime.now()
            self._request_count += 1
            
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json() if response.text else {},
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'message': response.text[:500] if response.text else 'No response',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'timeout',
                'message': 'Request timed out'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'connection_error',
                'message': 'Failed to connect to server'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'exception',
                'message': str(e)
            }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request('DELETE', endpoint)
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status information."""
        return {
            'configured': self.is_configured(),
            'base_url': self.base_url,
            'request_count': self._request_count,
            'last_request': self._last_request_time.isoformat() if self._last_request_time else None
        }
