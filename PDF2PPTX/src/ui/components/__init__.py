"""
Modern UI components for PDF2PPTX v3.0

This module provides Material Design 3 inspired components for the application.
All components follow the design specifications and accessibility guidelines.
"""

from .modern_widgets import (
    ModernButton,
    ModernCard,
    ModernTextField,
    ModernProgressBar,
    ModernDropZone,
    ModernTabBar,
    MaterialColors,
    MaterialIcons
)

from .theme_manager import (
    ThemeManager,
    Theme
)

from .animations import (
    AnimationManager,
    FadeInOut,
    ScaleInOut,
    SlideInOut
)

__all__ = [
    'ModernButton',
    'ModernCard',
    'ModernTextField',
    'ModernProgressBar',
    'ModernDropZone',
    'ModernTabBar',
    'MaterialColors',
    'MaterialIcons',
    'ThemeManager',
    'Theme',
    'AnimationManager',
    'FadeInOut',
    'ScaleInOut',
    'SlideInOut'
]