import os
import subprocess
import sys

version_path = "VERSION"
if hasattr(sys, "_MEIPASS"):
    version_path = os.path.join(sys._MEIPASS, version_path)
with open(version_path) as version_file:
    __version__ = version_file.read().strip()

GIT_SHA = subprocess.check_output(["git", "rev-parse", "--short=8", "HEAD"]).decode("utf-8").strip()
