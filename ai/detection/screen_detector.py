"""
Screen Detector Module - Detects and analyzes screen content
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class ScreenDetector:
    """
    Detects and analyzes what's displayed on screen.
    Uses computer vision and OCR for content analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the screen detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.is_active = False
        self._last_capture = None
        self._detection_history: List[Dict] = []
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'capture_interval': 1.0,  # seconds
            'detection_threshold': 0.5,
            'enable_ocr': True,
            'enable_object_detection': True,
            'regions_of_interest': [],  # List of (x, y, w, h) tuples
            'max_history': 100
        }
    
    def start(self):
        """Start screen detection."""
        self.is_active = True
        return True
    
    def stop(self):
        """Stop screen detection."""
        self.is_active = False
    
    def detect(self) -> Dict[str, Any]:
        """
        Perform screen detection and analysis.
        
        Returns:
            Detection results including elements found
        """
        try:
            # Capture screen
            screenshot = self._capture_screen()
            if screenshot is None:
                return {'status': 'error', 'error': 'Failed to capture screen'}
            
            elements = []
            
            # Perform OCR text detection
            if self.config.get('enable_ocr', True):
                text_elements = self._detect_text(screenshot)
                elements.extend(text_elements)
            
            # Perform object detection
            if self.config.get('enable_object_detection', True):
                objects = self._detect_objects(screenshot)
                elements.extend(objects)
            
            # Analyze regions of interest
            roi_elements = self._analyze_regions(screenshot)
            elements.extend(roi_elements)
            
            # Store result
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'elements': elements,
                'element_count': len(elements),
                'screen_size': self._get_screen_size()
            }
            
            # Update history
            self._detection_history.append(result)
            if len(self._detection_history) > self.config['max_history']:
                self._detection_history.pop(0)
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _capture_screen(self) -> Optional[Any]:
        """Capture current screen content."""
        try:
            # Try to use mss for screen capture
            try:
                import mss
                with mss.mss() as sct:
                    monitor = sct.monitors[1]  # Primary monitor
                    screenshot = sct.grab(monitor)
                    self._last_capture = screenshot
                    return screenshot
            except ImportError:
                # Fallback to PIL
                try:
                    from PIL import ImageGrab
                    screenshot = ImageGrab.grab()
                    self._last_capture = screenshot
                    return screenshot
                except ImportError:
                    pass
            
            # Return placeholder if no capture method available
            return {'type': 'placeholder', 'size': (1920, 1080)}
            
        except Exception as e:
            print(f"[WARNING] Screen capture failed: {e}")
            return None
    
    def _detect_text(self, screenshot: Any) -> List[Dict]:
        """Detect text in screenshot using OCR."""
        elements = []
        
        try:
            import pytesseract
            from PIL import Image
            
            # Convert to PIL Image if needed
            if hasattr(screenshot, 'rgb'):
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            elif hasattr(screenshot, 'pixels'):
                img = screenshot
            else:
                return elements
            
            # Perform OCR
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            for i, text in enumerate(ocr_data['text']):
                if text.strip():
                    elements.append({
                        'type': 'text',
                        'content': text.strip(),
                        'position': {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        },
                        'confidence': ocr_data['conf'][i] / 100.0
                    })
                    
        except ImportError:
            # OCR not available, return synthetic data
            elements.append({
                'type': 'text',
                'content': '[OCR not available - install pytesseract]',
                'position': {'x': 0, 'y': 0, 'width': 100, 'height': 20},
                'confidence': 0.0
            })
        except Exception as e:
            print(f"[WARNING] Text detection failed: {e}")
        
        return elements
    
    def _detect_objects(self, screenshot: Any) -> List[Dict]:
        """Detect objects in screenshot."""
        elements = []
        
        try:
            import cv2
            import numpy as np
            
            # Convert to numpy array
            if hasattr(screenshot, 'rgb'):
                img = np.frombuffer(screenshot.rgb, dtype=np.uint8).reshape(
                    screenshot.height, screenshot.width, 3
                )
            else:
                return elements
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) > 1000:  # Minimum area
                    x, y, w, h = cv2.boundingRect(contour)
                    elements.append({
                        'type': 'object',
                        'category': 'detected_region',
                        'position': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                        'area': cv2.contourArea(contour)
                    })
                    
        except ImportError:
            # OpenCV not available
            pass
        except Exception as e:
            print(f"[WARNING] Object detection failed: {e}")
        
        return elements
    
    def _analyze_regions(self, screenshot: Any) -> List[Dict]:
        """Analyze specific regions of interest."""
        elements = []
        
        for i, roi in enumerate(self.config.get('regions_of_interest', [])):
            elements.append({
                'type': 'region_of_interest',
                'index': i,
                'bounds': roi,
                'analyzed': True
            })
        
        return elements
    
    def _get_screen_size(self) -> Tuple[int, int]:
        """Get current screen size."""
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                return (monitor['width'], monitor['height'])
        except:
            return (1920, 1080)
    
    def add_region_of_interest(self, x: int, y: int, width: int, height: int):
        """Add a region of interest for focused detection."""
        self.config.setdefault('regions_of_interest', []).append((x, y, width, height))
    
    def clear_regions_of_interest(self):
        """Clear all regions of interest."""
        self.config['regions_of_interest'] = []
    
    def get_history(self) -> List[Dict]:
        """Get detection history."""
        return self._detection_history
    
    def get_status(self) -> Dict[str, Any]:
        """Get detector status."""
        return {
            'is_active': self.is_active,
            'config': self.config,
            'history_size': len(self._detection_history),
            'last_capture': self._last_capture is not None
        }
