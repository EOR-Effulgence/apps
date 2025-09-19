"""
Runtime hook for Tkinter to fix Tcl/Tk data directory issues in PyInstaller.
This hook ensures that Tcl and Tk can find their data directories.
"""

import os
import sys
import tempfile
import shutil

def fix_tkinter_paths():
    """Fix Tkinter paths for PyInstaller bundled applications."""
    if getattr(sys, 'frozen', False):
        # We are running in a PyInstaller bundle
        bundle_dir = sys._MEIPASS

        # Try to set environment variables to bypass Tcl initialization
        # This is a workaround for missing Tcl data directories

        # Create temporary dummy directories if needed
        temp_dir = tempfile.gettempdir()
        dummy_tcl = os.path.join(temp_dir, 'tcl8.6')
        dummy_tk = os.path.join(temp_dir, 'tk8.6')

        # Create minimal dummy directories
        try:
            if not os.path.exists(dummy_tcl):
                os.makedirs(dummy_tcl, exist_ok=True)
                # Create a minimal init.tcl file
                with open(os.path.join(dummy_tcl, 'init.tcl'), 'w') as f:
                    f.write('# Dummy init.tcl\n')

            if not os.path.exists(dummy_tk):
                os.makedirs(dummy_tk, exist_ok=True)
                # Create a minimal tk.tcl file
                with open(os.path.join(dummy_tk, 'tk.tcl'), 'w') as f:
                    f.write('# Dummy tk.tcl\n')
        except Exception:
            pass  # Silently fail if we can't create dummy files

        # Set environment variables
        os.environ['TCL_LIBRARY'] = dummy_tcl
        os.environ['TK_LIBRARY'] = dummy_tk

        # Also try to find actual Tcl/Tk directories in bundle
        tcl_data_path = os.path.join(bundle_dir, '_tcl_data')
        tk_data_path = os.path.join(bundle_dir, '_tk_data')

        if os.path.exists(tcl_data_path):
            os.environ['TCL_LIBRARY'] = tcl_data_path

        if os.path.exists(tk_data_path):
            os.environ['TK_LIBRARY'] = tk_data_path

        # Look for any tcl/tk directories in bundle
        try:
            for item in os.listdir(bundle_dir):
                item_path = os.path.join(bundle_dir, item)
                if os.path.isdir(item_path):
                    if 'tcl' in item.lower() and os.path.exists(os.path.join(item_path, 'init.tcl')):
                        os.environ['TCL_LIBRARY'] = item_path
                    elif 'tk' in item.lower() and os.path.exists(os.path.join(item_path, 'tk.tcl')):
                        os.environ['TK_LIBRARY'] = item_path
        except Exception:
            pass  # Silently continue if directory listing fails

# Call the fix function
fix_tkinter_paths()