"""
Compatibility alias for vision module.
This file maintains backward compatibility for legacy code.
"""
from core.vision_engine import VisionEngine

# Create a singleton instance for find_template function
_vision_engine = VisionEngine()

def find_template(template_path, threshold=0.8, region=None):
    """
    Find template in screenshot (backward compatibility function).
    
    Args:
        template_path: Path to template image
        threshold: Matching threshold (0.0 to 1.0)
        region: Optional region tuple (x, y, width, height)
    
    Returns:
        Tuple (x, y) if found, None otherwise
    """
    return _vision_engine.find_template(template_path, threshold, region)

__all__ = ['VisionEngine', 'find_template']
