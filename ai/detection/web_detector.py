"""
Web Detector Module - Detects and analyzes web content
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class WebDetector:
    """
    Detects and analyzes web content for training data.
    Supports multiple browsers and headless operation.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the web detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.is_active = False
        self._browser = None
        self._detection_history: List[Dict] = []
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'browser': 'chromium',
            'headless': True,
            'timeout': 30000,  # ms
            'wait_for_load': True,
            'extract_text': True,
            'extract_links': True,
            'extract_images': True,
            'extract_forms': True,
            'max_history': 100,
            'target_urls': []
        }
    
    def start(self) -> bool:
        """Start web detection service."""
        try:
            self.is_active = True
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start web detector: {e}")
            return False
    
    def stop(self):
        """Stop web detection service."""
        self.is_active = False
        if self._browser:
            try:
                self._browser.close()
            except:
                pass
            self._browser = None
    
    def detect(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect and analyze web content.
        
        Args:
            url: URL to analyze (optional)
            
        Returns:
            Detection results
        """
        try:
            content = []
            
            # Analyze target URLs from config
            urls_to_process = [url] if url else self.config.get('target_urls', [])
            
            for target_url in urls_to_process:
                if target_url:
                    page_content = self._analyze_page(target_url)
                    if page_content:
                        content.append(page_content)
            
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'content': content,
                'urls_processed': len(urls_to_process)
            }
            
            # Update history
            self._detection_history.append(result)
            if len(self._detection_history) > self.config['max_history']:
                self._detection_history.pop(0)
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _analyze_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Analyze a single web page."""
        page_data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'elements': []
        }
        
        try:
            # Try using playwright
            try:
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=self.config['headless'])
                    page = browser.new_page()
                    page.goto(url, timeout=self.config['timeout'])
                    
                    if self.config['wait_for_load']:
                        page.wait_for_load_state('networkidle')
                    
                    # Extract content
                    if self.config['extract_text']:
                        texts = self._extract_text_playwright(page)
                        page_data['elements'].extend(texts)
                    
                    if self.config['extract_links']:
                        links = self._extract_links_playwright(page)
                        page_data['elements'].extend(links)
                    
                    if self.config['extract_images']:
                        images = self._extract_images_playwright(page)
                        page_data['elements'].extend(images)
                    
                    if self.config['extract_forms']:
                        forms = self._extract_forms_playwright(page)
                        page_data['elements'].extend(forms)
                    
                    page_data['title'] = page.title()
                    browser.close()
                    
            except ImportError:
                # Fallback to requests + BeautifulSoup
                page_data = self._analyze_page_requests(url)
                
        except Exception as e:
            page_data['error'] = str(e)
        
        return page_data
    
    def _extract_text_playwright(self, page) -> List[Dict]:
        """Extract text content using Playwright."""
        elements = []
        try:
            # Get all text content
            text_content = page.inner_text('body')
            if text_content:
                elements.append({
                    'type': 'text',
                    'content': text_content[:10000],  # Limit size
                    'source': 'body'
                })
            
            # Get headings
            for level in range(1, 7):
                headings = page.query_selector_all(f'h{level}')
                for h in headings:
                    text = h.inner_text()
                    if text:
                        elements.append({
                            'type': 'heading',
                            'level': level,
                            'content': text
                        })
        except Exception as e:
            print(f"[WARNING] Text extraction failed: {e}")
        
        return elements
    
    def _extract_links_playwright(self, page) -> List[Dict]:
        """Extract links using Playwright."""
        elements = []
        try:
            links = page.query_selector_all('a')
            for link in links[:100]:  # Limit number
                href = link.get_attribute('href')
                text = link.inner_text()
                if href:
                    elements.append({
                        'type': 'link',
                        'href': href,
                        'text': text
                    })
        except Exception as e:
            print(f"[WARNING] Link extraction failed: {e}")
        
        return elements
    
    def _extract_images_playwright(self, page) -> List[Dict]:
        """Extract image information using Playwright."""
        elements = []
        try:
            images = page.query_selector_all('img')
            for img in images[:50]:  # Limit number
                src = img.get_attribute('src')
                alt = img.get_attribute('alt')
                if src:
                    elements.append({
                        'type': 'image',
                        'src': src,
                        'alt': alt or ''
                    })
        except Exception as e:
            print(f"[WARNING] Image extraction failed: {e}")
        
        return elements
    
    def _extract_forms_playwright(self, page) -> List[Dict]:
        """Extract form information using Playwright."""
        elements = []
        try:
            forms = page.query_selector_all('form')
            for form in forms:
                action = form.get_attribute('action')
                method = form.get_attribute('method')
                
                # Get form fields
                inputs = form.query_selector_all('input, select, textarea')
                fields = []
                for inp in inputs:
                    field_name = inp.get_attribute('name')
                    field_type = inp.get_attribute('type')
                    if field_name:
                        fields.append({
                            'name': field_name,
                            'type': field_type or 'text'
                        })
                
                elements.append({
                    'type': 'form',
                    'action': action,
                    'method': method or 'GET',
                    'fields': fields
                })
        except Exception as e:
            print(f"[WARNING] Form extraction failed: {e}")
        
        return elements
    
    def _analyze_page_requests(self, url: str) -> Dict[str, Any]:
        """Analyze page using requests and BeautifulSoup."""
        page_data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'elements': []
        }
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            page_data['title'] = title.string if title else ''
            
            # Extract text
            if self.config['extract_text']:
                for p in soup.find_all(['p', 'span', 'div'])[:100]:
                    text = p.get_text(strip=True)
                    if text:
                        page_data['elements'].append({
                            'type': 'text',
                            'content': text[:500]
                        })
            
            # Extract links
            if self.config['extract_links']:
                for a in soup.find_all('a', href=True)[:100]:
                    page_data['elements'].append({
                        'type': 'link',
                        'href': a['href'],
                        'text': a.get_text(strip=True)
                    })
            
            # Extract images
            if self.config['extract_images']:
                for img in soup.find_all('img', src=True)[:50]:
                    page_data['elements'].append({
                        'type': 'image',
                        'src': img['src'],
                        'alt': img.get('alt', '')
                    })
                    
        except ImportError:
            page_data['error'] = 'requests/beautifulsoup not available'
        except Exception as e:
            page_data['error'] = str(e)
        
        return page_data
    
    def add_target_url(self, url: str):
        """Add a URL to monitor."""
        if url not in self.config['target_urls']:
            self.config['target_urls'].append(url)
    
    def remove_target_url(self, url: str):
        """Remove a URL from monitoring."""
        if url in self.config['target_urls']:
            self.config['target_urls'].remove(url)
    
    def get_history(self) -> List[Dict]:
        """Get detection history."""
        return self._detection_history
    
    def get_status(self) -> Dict[str, Any]:
        """Get detector status."""
        return {
            'is_active': self.is_active,
            'config': self.config,
            'history_size': len(self._detection_history),
            'target_urls': len(self.config.get('target_urls', []))
        }
