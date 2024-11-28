from dataclasses import dataclass


@dataclass
class DirectConnection:
    """A direct connection to a server using SSH."""

    DEFAULT_PORT = 22
    DEFAULT_TYPE = "Server"

    name: str
    user: str
    host: str
    port: int
    key: str
    notes: str

    def to_dict(self) -> dict:
        """Convert the direct connection to a dictionary."""
        return {
            "name": self.name,
            "user": self.user,
            "host": self.host,
            "port": self.port,
            "key": self.key,
            "notes": self.notes,
        }

    def copy(self) -> "DirectConnection":
        """Create a copy of the direct connection."""
        return DirectConnection(
            name=self.name,
            user=self.user,
            host=self.host,
            port=self.port,
            key=self.key,
            notes=self.notes,
        )

    @staticmethod
    def default() -> "DirectConnection":
        """Get a direct connection containing default values."""
        return DirectConnection(
            name="",
            user="",
            host="",
            port=DirectConnection.DEFAULT_PORT,
            key="",
            notes="",
        )

    @staticmethod
    def from_dict(data: dict) -> "DirectConnection":
        """Create a direct connection from a dictionary. If a key is not present, the default value will be used."""
        direct_connection = DirectConnection.default()
        direct_connection.name = data.get("name", direct_connection.name)
        direct_connection.user = data.get("user", direct_connection.user)
        direct_connection.host = data.get("host", direct_connection.host)
        direct_connection.port = data.get("port", direct_connection.port)
        direct_connection.key = data.get("key", direct_connection.key)
        direct_connection.notes = data.get("notes", direct_connection.notes)
        return direct_connection
