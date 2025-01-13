from app.config_file import ConfigFile

DEFAULT_THEME = "light"
DEFAULT_PROMPT_TO_DOWNLOAD_NEW_VERSION = True


class Settings:
    """Settings for the application. These are saved to disk and loaded on startup."""

    def __init__(
        self, theme: str = DEFAULT_THEME, prompt_to_download_new_version: bool = DEFAULT_PROMPT_TO_DOWNLOAD_NEW_VERSION
    ):
        self.theme = theme
        self.prompt_to_download_new_version = prompt_to_download_new_version
        self.source = ConfigFile("settings.json")

    def set_theme(self, theme: str):
        self.theme = theme
        self.save()

    def set_prompt_to_download_new_version(self, value: bool):
        self.prompt_to_download_new_version = value
        self.save()

    def load(self):
        self._from_json(self.source.load())

    def save(self):
        self.source.save(self._to_json())

    def _to_json(self):
        return {"theme": self.theme, "prompt_to_download_new_version": self.prompt_to_download_new_version}

    def _from_json(self, json: dict):
        if "theme" in json:
            self.theme = json["theme"]
        if "prompt_to_download_new_version" in json:
            self.prompt_to_download_new_version = json["prompt_to_download_new_version"]
