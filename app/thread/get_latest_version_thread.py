from PySide6.QtCore import QThread, Signal

from app.model.model import Model


class GetLatestVersionThread(QThread):
    """Get the latest release from Github and emit a signal if a new version is available."""

    def __init__(self, model: Model) -> None:
        super().__init__()
        self.model = model

    new_version_available = Signal(str, str, str)  # version, url, publish date

    def run(self):
        latest_release = self.model.version.get_latest_version()
        if latest_release is not None:
            self.new_version_available.emit(
                latest_release.tag,
                latest_release.url,
                latest_release.publish_date,
            )
