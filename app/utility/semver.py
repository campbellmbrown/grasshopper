class SemVer:
    def __init__(self, version: str):
        self.raw = version
        splits = version.split(".")
        if len(splits) != 3:
            self.is_valid = False
            return
        try:
            self.major = int(splits[0])
            self.minor = int(splits[1])
            self.patch = int(splits[2])
            self.is_valid = True
        except ValueError:
            self.is_valid = False

    def __lt__(self, other: "SemVer"):
        if self.major < other.major:
            return True
        if self.major == other.major:
            if self.minor < other.minor:
                return True
            if self.minor == other.minor:
                if self.patch < other.patch:
                    return True
        return False

    def __eq__(self, other: "SemVer"):
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch

    def __str__(self):
        return self.raw
