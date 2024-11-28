import os
import sys

version_path = "VERSION"
if hasattr(sys, "_MEIPASS"):
    version_path = os.path.join(sys._MEIPASS, version_path)
with open(version_path) as version_file:
    __version__ = version_file.read().strip()
