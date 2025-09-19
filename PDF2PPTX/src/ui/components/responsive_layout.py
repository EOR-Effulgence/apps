"""
Responsive Layout System for PDF2PPTX v3.0

Adaptive layout management that responds to window size changes and
provides different layouts for various screen sizes.
"""

from __future__ import annotations
import tkinter as tk
from typing import Dict, List, Tuple, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass


class BreakpointSize(Enum):
    """Screen size breakpoints"""
    XS = "xs"    # < 576px
    SM = "sm"    # 576px - 768px
    MD = "md"    # 768px - 992px
    LG = "lg"    # 992px - 1200px
    XL = "xl"    # >= 1200px


@dataclass
class Breakpoint:
    """Breakpoint configuration"""
    min_width: int
    max_width: Optional[int] = None
    columns: int = 12
    gutter: int = 16


class ResponsiveGrid:
    """Responsive grid system for widget layout"""

    BREAKPOINTS = {
        BreakpointSize.XS: Breakpoint(0, 575, 4, 8),
        BreakpointSize.SM: Breakpoint(576, 767, 8, 12),
        BreakpointSize.MD: Breakpoint(768, 991, 12, 16),
        BreakpointSize.LG: Breakpoint(992, 1199, 12, 20),
        BreakpointSize.XL: Breakpoint(1200, None, 12, 24)
    }

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.current_breakpoint = BreakpointSize.MD
        self.widgets: List[ResponsiveWidget] = []
        self._setup_resize_handler()

    def _setup_resize_handler(self):
        """Setup window resize handler"""
        self.parent.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """Handle window resize"""
        if event.widget == self.parent:
            new_breakpoint = self._get_current_breakpoint()
            if new_breakpoint != self.current_breakpoint:
                self.current_breakpoint = new_breakpoint
                self._relayout()

    def _get_current_breakpoint(self) -> BreakpointSize:
        """Determine current breakpoint based on window width"""
        width = self.parent.winfo_width()

        for size, breakpoint in self.BREAKPOINTS.items():
            if breakpoint.min_width <= width:
                if breakpoint.max_width is None or width <= breakpoint.max_width:
                    return size

        return BreakpointSize.MD

    def add_widget(self, widget: tk.Widget, col_config: Dict[BreakpointSize, int],
                   row: int = 0, sticky: str = "ew") -> 'ResponsiveWidget':
        """Add a widget with responsive column configuration"""
        responsive_widget = ResponsiveWidget(widget, col_config, row, sticky)
        self.widgets.append(responsive_widget)
        self._relayout()
        return responsive_widget

    def _relayout(self):
        """Relayout all widgets based on current breakpoint"""
        breakpoint = self.BREAKPOINTS[self.current_breakpoint]

        # Clear current layout
        for widget_info in self.widgets:
            widget_info.widget.grid_forget()

        # Apply new layout
        current_row = 0
        current_col = 0

        for widget_info in self.widgets:
            cols = widget_info.get_columns_for_breakpoint(self.current_breakpoint)

            # Check if widget fits in current row
            if current_col + cols > breakpoint.columns:
                current_row += 1
                current_col = 0

            # Grid the widget
            widget_info.widget.grid(
                row=current_row + widget_info.row_offset,
                column=current_col,
                columnspan=cols,
                sticky=widget_info.sticky,
                padx=breakpoint.gutter // 2,
                pady=breakpoint.gutter // 2
            )

            current_col += cols

        # Configure column weights
        for i in range(breakpoint.columns):
            self.parent.grid_columnconfigure(i, weight=1)


class ResponsiveWidget:
    """Wrapper for responsive widget configuration"""

    def __init__(self, widget: tk.Widget, col_config: Dict[BreakpointSize, int],
                 row_offset: int = 0, sticky: str = "ew"):
        self.widget = widget
        self.col_config = col_config
        self.row_offset = row_offset
        self.sticky = sticky

    def get_columns_for_breakpoint(self, breakpoint: BreakpointSize) -> int:
        """Get column span for specific breakpoint"""
        # Try to get exact breakpoint configuration
        if breakpoint in self.col_config:
            return self.col_config[breakpoint]

        # Fall back to larger breakpoints
        fallback_order = [BreakpointSize.XL, BreakpointSize.LG, BreakpointSize.MD,
                         BreakpointSize.SM, BreakpointSize.XS]

        for fallback in fallback_order:
            if fallback in self.col_config:
                return self.col_config[fallback]

        # Default to full width
        return ResponsiveGrid.BREAKPOINTS[breakpoint].columns


class ResponsiveContainer(tk.Frame):
    """Container that adapts its layout based on screen size"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid = ResponsiveGrid(self)
        self._adaptive_widgets: List[AdaptiveWidget] = []

    def add_adaptive_widget(self, widget_class, col_config: Dict[BreakpointSize, int],
                          **widget_kwargs) -> 'AdaptiveWidget':
        """Add a widget that adapts to screen size"""
        adaptive_widget = AdaptiveWidget(self, widget_class, col_config, **widget_kwargs)
        self._adaptive_widgets.append(adaptive_widget)
        return adaptive_widget

    def add_responsive_widget(self, widget: tk.Widget,
                             col_config: Dict[BreakpointSize, int],
                             **grid_kwargs) -> ResponsiveWidget:
        """Add an existing widget with responsive behavior"""
        return self.grid.add_widget(widget, col_config, **grid_kwargs)


class AdaptiveWidget:
    """Widget that can change its appearance based on screen size"""

    def __init__(self, parent: ResponsiveContainer, widget_class,
                 col_config: Dict[BreakpointSize, int], **widget_kwargs):
        self.parent = parent
        self.widget_class = widget_class
        self.col_config = col_config
        self.widget_kwargs = widget_kwargs
        self.current_widget: Optional[tk.Widget] = None

        self._create_widget()
        self._add_to_grid()

    def _create_widget(self):
        """Create the widget instance"""
        # Adapt widget parameters based on current breakpoint
        adapted_kwargs = self._adapt_widget_kwargs()
        self.current_widget = self.widget_class(self.parent, **adapted_kwargs)

    def _adapt_widget_kwargs(self) -> Dict[str, Any]:
        """Adapt widget parameters based on current breakpoint"""
        kwargs = self.widget_kwargs.copy()
        breakpoint = self.parent.grid.current_breakpoint

        # Example adaptations based on screen size
        if breakpoint in [BreakpointSize.XS, BreakpointSize.SM]:
            # Mobile/tablet adaptations
            if 'font' in kwargs:
                # Reduce font size for smaller screens
                font_info = kwargs['font']
                if isinstance(font_info, tuple) and len(font_info) >= 2:
                    family, size = font_info[0], font_info[1]
                    kwargs['font'] = (family, max(8, size - 2))

            if 'padx' in kwargs:
                kwargs['padx'] = max(4, kwargs['padx'] // 2)
            if 'pady' in kwargs:
                kwargs['pady'] = max(4, kwargs['pady'] // 2)

        return kwargs

    def _add_to_grid(self):
        """Add widget to responsive grid"""
        if self.current_widget:
            self.parent.grid.add_widget(self.current_widget, self.col_config)

    def update_for_breakpoint(self, breakpoint: BreakpointSize):
        """Update widget for new breakpoint"""
        if self.current_widget:
            # Remove current widget
            self.current_widget.destroy()

            # Create new adapted widget
            self._create_widget()
            self._add_to_grid()


class ResponsiveText:
    """Responsive text utility for different screen sizes"""

    @staticmethod
    def get_text_for_breakpoint(text_config: Dict[BreakpointSize, str],
                               current_breakpoint: BreakpointSize) -> str:
        """Get appropriate text for current breakpoint"""
        if current_breakpoint in text_config:
            return text_config[current_breakpoint]

        # Fallback to progressively larger breakpoints
        fallback_order = [BreakpointSize.XL, BreakpointSize.LG, BreakpointSize.MD,
                         BreakpointSize.SM, BreakpointSize.XS]

        for breakpoint in fallback_order:
            if breakpoint in text_config:
                return text_config[breakpoint]

        # Final fallback
        return list(text_config.values())[0] if text_config else ""

    @staticmethod
    def get_responsive_font(base_size: int, breakpoint: BreakpointSize) -> Tuple[str, int]:
        """Get responsive font size based on breakpoint"""
        size_multipliers = {
            BreakpointSize.XS: 0.75,
            BreakpointSize.SM: 0.85,
            BreakpointSize.MD: 1.0,
            BreakpointSize.LG: 1.1,
            BreakpointSize.XL: 1.2
        }

        multiplier = size_multipliers.get(breakpoint, 1.0)
        adjusted_size = max(8, int(base_size * multiplier))

        return ("Segoe UI", adjusted_size)


class FlexLayout:
    """CSS Flexbox-inspired layout for tkinter"""

    def __init__(self, parent: tk.Widget, direction: str = "row",
                 justify: str = "start", align: str = "stretch"):
        self.parent = parent
        self.direction = direction  # "row" or "column"
        self.justify = justify      # "start", "center", "end", "space-between", "space-around"
        self.align = align          # "start", "center", "end", "stretch"
        self.children: List[Tuple[tk.Widget, Dict[str, Any]]] = []

    def add_child(self, widget: tk.Widget, flex: int = 0, **kwargs):
        """Add a child widget with flex properties"""
        self.children.append((widget, {"flex": flex, **kwargs}))
        self._layout()

    def _layout(self):
        """Apply flexbox-style layout"""
        if not self.children:
            return

        # Calculate available space
        self.parent.update_idletasks()
        if self.direction == "row":
            available_space = self.parent.winfo_width()
        else:
            available_space = self.parent.winfo_height()

        # Calculate flex distribution
        total_flex = sum(props.get("flex", 0) for _, props in self.children)
        fixed_space = 0

        # First pass: calculate fixed space
        for widget, props in self.children:
            if props.get("flex", 0) == 0:
                if self.direction == "row":
                    fixed_space += widget.winfo_reqwidth()
                else:
                    fixed_space += widget.winfo_reqheight()

        flexible_space = max(0, available_space - fixed_space)

        # Second pass: layout widgets
        current_pos = 0
        for i, (widget, props) in enumerate(self.children):
            flex = props.get("flex", 0)

            if flex > 0 and total_flex > 0:
                # Flexible widget
                widget_space = int((flex / total_flex) * flexible_space)
            else:
                # Fixed widget
                if self.direction == "row":
                    widget_space = widget.winfo_reqwidth()
                else:
                    widget_space = widget.winfo_reqheight()

            # Position widget
            if self.direction == "row":
                widget.place(x=current_pos, y=0, width=widget_space,
                           height=self.parent.winfo_height())
            else:
                widget.place(x=0, y=current_pos, width=self.parent.winfo_width(),
                           height=widget_space)

            current_pos += widget_space