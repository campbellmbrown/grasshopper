import os
from sys import platform

if platform == "win32":
    SSH_DIR = os.path.join(os.environ["USERPROFILE"], ".ssh")
elif platform == "linux":
    SSH_DIR = os.path.join(os.environ["HOME"], ".ssh")
else:
    raise NotImplementedError(f"Platform '{platform}' is not supported")
