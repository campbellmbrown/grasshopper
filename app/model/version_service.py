import logging
import os
from dataclasses import dataclass

import requests

from app.utility.resource_provider import get_resource_path
from app.utility.semver import SemVer

URL = "https://api.github.com/repos/campbellmbrown/grasshopper/releases/latest"
VERSION_PATH = "VERSION"
GIT_SHA_PATH = "GIT_SHA"


@dataclass
class VersionInfo:
    tag: str
    url: str
    publish_date: str


class VersionService:
    def __init__(self) -> None:
        with open(get_resource_path(VERSION_PATH)) as version_file:
            self.current = version_file.read().strip()

        git_sha_path = get_resource_path(GIT_SHA_PATH)
        if not os.path.exists(git_sha_path):
            logging.warning("GIT_SHA file not found. This is likely a build issue (unpublished).")
            git_sha = "unknown"
        else:
            with open(git_sha_path) as git_sha_file:
                git_sha = git_sha_file.read().strip()
        self.git_sha = git_sha

    def get_latest_version(self) -> VersionInfo | None:
        latest_release = self.get_latest_release()
        if latest_release is None:
            return None

        tag_name = latest_release["tag_name"]
        if not isinstance(tag_name, str):
            logging.warning("Latest release tag name is not a string.")
            return None

        tag_name = tag_name.removeprefix("v")
        latest_version = SemVer(tag_name)
        if not latest_version.is_valid:
            logging.warning("Latest release tag name is not in the correct format (%s).", tag_name)
            return None

        this_version = SemVer(self.current)
        assert this_version.is_valid

        if latest_version > this_version:
            logging.info("New version available: %s", tag_name)
            logging.info("Download at: %s", latest_release["html_url"])
            return VersionInfo(
                tag=tag_name,
                url=latest_release["html_url"],
                publish_date=latest_release["published_at"],
            )
        else:
            logging.info("No new version available.")
        return None

    def get_latest_release(self) -> dict | None:
        logging.info("Checking %s...", URL)
        try:
            response = requests.get(URL)
        except requests.exceptions.ConnectionError:
            logging.warning("Failed to get latest release from Github.")
            return None

        response.raise_for_status()
        release = response.json()

        if "tag_name" not in release:
            logging.warning("Failed to get tag name from the latest release.")
            return None

        if "html_url" not in release:
            logging.warning("Failed to get URL from the latest release.")
            return None

        if "published_at" not in release:
            logging.warning("Failed to get publish date from the latest release.")
            return None

        return release
