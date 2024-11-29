import os
import sys

version_path = "resources/VERSION"
git_sha_path = "resources/GIT_SHA"

if hasattr(sys, "_MEIPASS"):
    version_path = os.path.join(sys._MEIPASS, version_path)
with open(version_path) as version_file:
    __version__ = version_file.read().strip()

if hasattr(sys, "_MEIPASS"):
    git_sha_path = os.path.join(sys._MEIPASS, git_sha_path)
if not os.path.exists(git_sha_path):
    GIT_SHA = "unknown"  # Needs to be published to get the Git SHA
else:
    with open(git_sha_path) as git_sha_file:
        GIT_SHA = git_sha_file.read().strip()
