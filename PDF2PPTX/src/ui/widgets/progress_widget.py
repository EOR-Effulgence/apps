"""
Progress tracking widget with enhanced functionality.
Provides reusable progress tracking component for GUI applications.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from threading import Lock


class ProgressWidget:
    """
    Enhanced progress widget with cancellation support and status updates.
    """

    def __init__(self, parent: tk.Widget, width: int = 400):
        self.parent = parent
        self._current_value = 0
        self._maximum = 0
        self._cancelled = False
        self._lock = Lock()
        self._cancel_callback: Optional[Callable[[], None]] = None

        # Create widget frame
        self.frame = tk.Frame(parent)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.frame,
            orient="horizontal",
            length=width,
            mode="determinate"
        )
        self.progress_bar.pack(pady=(0, 5))

        # Status label
        self.status_label = tk.Label(
            self.frame,
            text="準備完了",
            font=("Arial", 9),
            fg="gray"
        )
        self.status_label.pack()

        # Cancel button (initially hidden)
        self.cancel_button = tk.Button(
            self.frame,
            text="キャンセル",
            command=self._on_cancel_clicked,
            state="disabled"
        )
        self.cancel_button.pack(pady=(5, 0))
        self.cancel_button.pack_forget()  # Hide initially

    def pack(self, **kwargs):
        """Pack the widget frame."""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the widget frame."""
        self.frame.grid(**kwargs)

    def set_cancel_callback(self, callback: Callable[[], None]) -> None:
        """Set callback function to call when cancel is requested."""
        self._cancel_callback = callback

    def start_operation(self, maximum: int, status: str = "処理中...") -> None:
        """
        Start a new operation with progress tracking.

        Args:
            maximum: Maximum value for progress
            status: Status text to display
        """
        with self._lock:
            self._maximum = maximum
            self._current_value = 0
            self._cancelled = False

            # Update UI
            self.progress_bar.configure(maximum=maximum, value=0)
            self.status_label.configure(text=status)

            # Show cancel button
            self.cancel_button.configure(state="normal")
            self.cancel_button.pack(pady=(5, 0))

            # Force UI update
            self.parent.update_idletasks()

    def update_progress(self, increment: int = 1, status: Optional[str] = None) -> None:
        """
        Update progress by specified increment.

        Args:
            increment: Amount to increment progress
            status: Optional status text update
        """
        with self._lock:
            if self._cancelled:
                return

            self._current_value = min(self._current_value + increment, self._maximum)

            # Update progress bar
            self.progress_bar.configure(value=self._current_value)

            # Update status if provided
            if status:
                self.status_label.configure(text=status)
            else:
                # Default status with progress
                progress_text = f"処理中... ({self._current_value}/{self._maximum})"
                self.status_label.configure(text=progress_text)

            # Force UI update
            self.parent.update_idletasks()

    def set_progress(self, value: int, status: Optional[str] = None) -> None:
        """
        Set progress to specific value.

        Args:
            value: Progress value to set
            status: Optional status text update
        """
        with self._lock:
            if self._cancelled:
                return

            self._current_value = min(max(value, 0), self._maximum)

            # Update progress bar
            self.progress_bar.configure(value=self._current_value)

            # Update status
            if status:
                self.status_label.configure(text=status)
            else:
                progress_text = f"処理中... ({self._current_value}/{self._maximum})"
                self.status_label.configure(text=progress_text)

            # Force UI update
            self.parent.update_idletasks()

    def complete_operation(self, status: str = "完了") -> None:
        """
        Mark operation as completed.

        Args:
            status: Completion status text
        """
        with self._lock:
            self._current_value = self._maximum
            self.progress_bar.configure(value=self._maximum)
            self.status_label.configure(text=status, fg="green")

            # Hide cancel button
            self.cancel_button.pack_forget()

            # Force UI update
            self.parent.update_idletasks()

    def error_operation(self, status: str = "エラーが発生しました") -> None:
        """
        Mark operation as failed.

        Args:
            status: Error status text
        """
        with self._lock:
            self.status_label.configure(text=status, fg="red")

            # Hide cancel button
            self.cancel_button.pack_forget()

            # Force UI update
            self.parent.update_idletasks()

    def reset(self) -> None:
        """Reset progress to initial state."""
        with self._lock:
            self._current_value = 0
            self._maximum = 0
            self._cancelled = False

            self.progress_bar.configure(value=0, maximum=100)
            self.status_label.configure(text="準備完了", fg="gray")

            # Hide cancel button
            self.cancel_button.configure(state="disabled")
            self.cancel_button.pack_forget()

            # Force UI update
            self.parent.update_idletasks()

    def cancel(self) -> None:
        """Cancel the current operation."""
        with self._lock:
            self._cancelled = True
            self.status_label.configure(text="キャンセルされました", fg="orange")

            # Hide cancel button
            self.cancel_button.pack_forget()

            # Force UI update
            self.parent.update_idletasks()

    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self.cancel()

        # Call cancel callback if set
        if self._cancel_callback:
            try:
                self._cancel_callback()
            except Exception:
                pass  # Ignore callback errors

    @property
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        with self._lock:
            return self._cancelled

    @property
    def current_value(self) -> int:
        """Get current progress value."""
        with self._lock:
            return self._current_value

    @property
    def maximum_value(self) -> int:
        """Get maximum progress value."""
        with self._lock:
            return self._maximum

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        with self._lock:
            if self._maximum == 0:
                return 0.0
            return (self._current_value / self._maximum) * 100.0