
"""
ImageMagick Wrapper Engine
Provides interfaces to safe subprocess calls to magick/convert.
"""
import subprocess
import logging

LOG = logging.getLogger(__name__)

def get_version():
    try:
        res = subprocess.run(["magick", "--version"], capture_output=True, text=True)
        return res.stdout.splitlines()[0] if res.returncode == 0 else "Unknown"
    except FileNotFoundError:
        return "Not Installed"
