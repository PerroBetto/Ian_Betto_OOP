"""
Manages asset paths for py-installer and python runtime calls.

All paths are relative.
"""
import os
import sys

def create_path(asset_name: str, rel_path: str) -> str:
    """
    Return the path to an asset depending on if the game is built during
    development or .exe

    Args:
        asset_name (str): name of the asset.
            Example: file
        rel_path (str): relative path to the asset.
            Example: /path/to/
    """
    path: str
    if hasattr(sys, '_MEIPASS'):
        # get asset when exported
        path = os.path.join(sys._MEIPASS, asset_name) # type: ignore
    else:
        # get asset during development
        path = os.path.join(os.path.abspath("."), (f"{rel_path}{asset_name}"))
    return path