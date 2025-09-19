"""
Animation System for PDF2PPTX v3.0

Smooth animations and transitions for modern UI components with easing functions
and animation management.
"""

from __future__ import annotations
import tkinter as tk
import threading
import time
import math
from typing import Callable, Optional, Any, Dict, List
from enum import Enum
from dataclasses import dataclass


class EasingType(Enum):
    """Animation easing types"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


@dataclass
class AnimationConfig:
    """Animation configuration"""
    duration: float = 0.3  # seconds
    easing: EasingType = EasingType.EASE_OUT
    delay: float = 0.0
    repeat: int = 1
    reverse: bool = False


class EasingFunctions:
    """Collection of easing functions for smooth animations"""

    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation"""
        return t

    @staticmethod
    def ease_in(t: float) -> float:
        """Ease in (cubic)"""
        return t * t * t

    @staticmethod
    def ease_out(t: float) -> float:
        """Ease out (cubic)"""
        return 1 - (1 - t) ** 3

    @staticmethod
    def ease_in_out(t: float) -> float:
        """Ease in out (cubic)"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - (-2 * t + 2) ** 3 / 2

    @staticmethod
    def bounce(t: float) -> float:
        """Bounce easing"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    @staticmethod
    def elastic(t: float) -> float:
        """Elastic easing"""
        if t == 0 or t == 1:
            return t
        return -(2 ** (10 * (t - 1))) * math.sin((t - 1.1) * 5 * math.pi)

    @classmethod
    def get_easing_function(cls, easing_type: EasingType) -> Callable[[float], float]:
        """Get easing function by type"""
        mapping = {
            EasingType.LINEAR: cls.linear,
            EasingType.EASE_IN: cls.ease_in,
            EasingType.EASE_OUT: cls.ease_out,
            EasingType.EASE_IN_OUT: cls.ease_in_out,
            EasingType.BOUNCE: cls.bounce,
            EasingType.ELASTIC: cls.elastic
        }
        return mapping.get(easing_type, cls.ease_out)


class Animation:
    """Base animation class"""

    def __init__(self, widget: tk.Widget, config: AnimationConfig,
                 update_callback: Callable[[float], None],
                 complete_callback: Optional[Callable[[], None]] = None):
        self.widget = widget
        self.config = config
        self.update_callback = update_callback
        self.complete_callback = complete_callback
        self.is_running = False
        self.is_paused = False
        self.start_time = 0.0
        self.pause_time = 0.0
        self.current_repeat = 0

    def start(self):
        """Start the animation"""
        if self.is_running:
            return

        self.is_running = True
        self.is_paused = False
        self.start_time = time.time() + self.config.delay
        self.current_repeat = 0
        self._animate()

    def stop(self):
        """Stop the animation"""
        self.is_running = False
        self.is_paused = False

    def pause(self):
        """Pause the animation"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()

    def resume(self):
        """Resume the animation"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            # Adjust start time to account for pause duration
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration

    def _animate(self):
        """Main animation loop"""
        if not self.is_running:
            return

        if self.is_paused:
            # Schedule next frame during pause
            self.widget.after(16, self._animate)  # ~60 FPS
            return

        current_time = time.time()
        if current_time < self.start_time:
            # Animation hasn't started yet (delay)
            self.widget.after(16, self._animate)
            return

        elapsed = current_time - self.start_time
        progress = min(1.0, elapsed / self.config.duration)

        # Apply easing
        easing_func = EasingFunctions.get_easing_function(self.config.easing)
        eased_progress = easing_func(progress)

        # Handle reverse
        if self.config.reverse and self.current_repeat % 2 == 1:
            eased_progress = 1.0 - eased_progress

        # Update animation
        try:
            self.update_callback(eased_progress)
        except Exception as e:
            print(f"Animation update error: {e}")
            self.stop()
            return

        if progress >= 1.0:
            # Animation cycle complete
            self.current_repeat += 1

            if self.current_repeat < self.config.repeat:
                # Start next repeat
                self.start_time = time.time()
                self.widget.after(16, self._animate)
            else:
                # Animation complete
                self.is_running = False
                if self.complete_callback:
                    try:
                        self.complete_callback()
                    except Exception as e:
                        print(f"Animation complete callback error: {e}")
        else:
            # Continue animation
            self.widget.after(16, self._animate)


class AnimationManager:
    """Central animation manager"""

    def __init__(self):
        self._animations: Dict[str, Animation] = {}

    def start_animation(self, name: str, animation: Animation):
        """Start a named animation"""
        # Stop existing animation with same name
        if name in self._animations:
            self._animations[name].stop()

        self._animations[name] = animation
        animation.start()

    def stop_animation(self, name: str):
        """Stop a named animation"""
        if name in self._animations:
            self._animations[name].stop()
            del self._animations[name]

    def stop_all_animations(self):
        """Stop all running animations"""
        for animation in self._animations.values():
            animation.stop()
        self._animations.clear()

    def pause_animation(self, name: str):
        """Pause a named animation"""
        if name in self._animations:
            self._animations[name].pause()

    def resume_animation(self, name: str):
        """Resume a named animation"""
        if name in self._animations:
            self._animations[name].resume()

    def is_running(self, name: str) -> bool:
        """Check if animation is running"""
        return name in self._animations and self._animations[name].is_running


class FadeInOut:
    """Fade in/out animation utility"""

    @staticmethod
    def fade_in(widget: tk.Widget, config: Optional[AnimationConfig] = None,
                callback: Optional[Callable[[], None]] = None):
        """Fade in a widget"""
        if config is None:
            config = AnimationConfig()

        # Store original state
        original_state = widget.cget('state') if hasattr(widget, 'state') else 'normal'

        def update(progress: float):
            # Simple fade using widget state (limited in tkinter)
            if progress > 0.5 and widget.cget('state') == 'disabled':
                widget.configure(state='normal')

        def complete():
            widget.configure(state=original_state)
            if callback:
                callback()

        animation = Animation(widget, config, update, complete)
        return animation

    @staticmethod
    def fade_out(widget: tk.Widget, config: Optional[AnimationConfig] = None,
                 callback: Optional[Callable[[], None]] = None):
        """Fade out a widget"""
        if config is None:
            config = AnimationConfig()

        def update(progress: float):
            if progress > 0.5:
                widget.configure(state='disabled')

        def complete():
            if callback:
                callback()

        animation = Animation(widget, config, update, complete)
        return animation


class ScaleInOut:
    """Scale in/out animation utility"""

    @staticmethod
    def scale_in(widget: tk.Widget, config: Optional[AnimationConfig] = None,
                 callback: Optional[Callable[[], None]] = None):
        """Scale in a widget"""
        if config is None:
            config = AnimationConfig()

        # Note: True scaling requires more complex tkinter manipulation
        # This is a simplified version using place geometry manager

        original_width = widget.winfo_reqwidth()
        original_height = widget.winfo_reqheight()

        def update(progress: float):
            # Simple scale simulation
            scale_factor = progress
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # This would need proper geometry management
            pass

        animation = Animation(widget, config, update, callback)
        return animation

    @staticmethod
    def scale_out(widget: tk.Widget, config: Optional[AnimationConfig] = None,
                  callback: Optional[Callable[[], None]] = None):
        """Scale out a widget"""
        if config is None:
            config = AnimationConfig()

        def update(progress: float):
            scale_factor = 1.0 - progress
            # Scale implementation would go here
            pass

        animation = Animation(widget, config, update, callback)
        return animation


class SlideInOut:
    """Slide in/out animation utility"""

    @staticmethod
    def slide_in_from_left(widget: tk.Widget, config: Optional[AnimationConfig] = None,
                           callback: Optional[Callable[[], None]] = None):
        """Slide in from left"""
        if config is None:
            config = AnimationConfig()

        parent = widget.master
        if not parent:
            return None

        # Get original position
        widget.update_idletasks()
        original_x = widget.winfo_x()
        target_x = original_x
        start_x = original_x - widget.winfo_width()

        # Position widget off-screen initially
        widget.place(x=start_x)

        def update(progress: float):
            current_x = start_x + (target_x - start_x) * progress
            widget.place(x=current_x)

        def complete():
            widget.place(x=target_x)
            if callback:
                callback()

        animation = Animation(widget, config, update, complete)
        return animation

    @staticmethod
    def slide_out_to_right(widget: tk.Widget, config: Optional[AnimationConfig] = None,
                           callback: Optional[Callable[[], None]] = None):
        """Slide out to right"""
        if config is None:
            config = AnimationConfig()

        parent = widget.master
        if not parent:
            return None

        # Get current position
        widget.update_idletasks()
        start_x = widget.winfo_x()
        target_x = start_x + widget.winfo_width()

        def update(progress: float):
            current_x = start_x + (target_x - start_x) * progress
            widget.place(x=current_x)

        def complete():
            widget.place_forget()
            if callback:
                callback()

        animation = Animation(widget, config, update, complete)
        return animation


# Global animation manager instance
_animation_manager = None

def get_animation_manager() -> AnimationManager:
    """Get global animation manager instance"""
    global _animation_manager
    if _animation_manager is None:
        _animation_manager = AnimationManager()
    return _animation_manager