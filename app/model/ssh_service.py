import os
import subprocess
from sys import platform


class SshService:
    def __init__(self) -> None:
        pass

    def open_ssh_directory(self) -> None:
        if platform == "win32":
            path = os.path.join(os.environ["USERPROFILE"], ".ssh")
            os.startfile(path)
        elif platform == "linux":
            path = os.path.join(os.environ["HOME"], ".ssh")
            subprocess.run(["xdg-open", path], check=True)
