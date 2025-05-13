from app.model.ssh_service import SshService
from app.model.version_service import VersionService
from app.settings import Settings


class Model:
    def __init__(self) -> None:
        self.ssh = SshService()
        self.version = VersionService()

        self.settings = Settings()
        self.settings.load()
