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


@dataclass
class PortForward:
    """A port forwarding connection to a server using SSH."""

    DEFAULT_SSH_PORT = 22
    DEFAULT_FORWARD_PORT = 8080

    name: str
    notes: str
    local_port: int
    target_host: str
    target_port: int
    remote_server_user: str
    remote_server_host: str
    remote_server_port: int
    key: str

    def to_dict(self) -> dict:
        """Convert the port forward to a dictionary."""
        return {
            "name": self.name,
            "notes": self.notes,
            "local_port": self.local_port,
            "target_host": self.target_host,
            "target_port": self.target_port,
            "remote_server_user": self.remote_server_user,
            "remote_server_host": self.remote_server_host,
            "remote_server_port": self.remote_server_port,
            "key": self.key,
        }

    def copy(self) -> "PortForward":
        """Create a copy of the port forward."""
        return PortForward(
            name=self.name,
            notes=self.notes,
            local_port=self.local_port,
            target_host=self.target_host,
            target_port=self.target_port,
            remote_server_user=self.remote_server_user,
            remote_server_host=self.remote_server_host,
            remote_server_port=self.remote_server_port,
            key=self.key,
        )

    @staticmethod
    def default() -> "PortForward":
        """Get a port forward containing default values."""
        return PortForward(
            name="",
            notes="",
            local_port=PortForward.DEFAULT_FORWARD_PORT,
            target_host="",
            target_port=PortForward.DEFAULT_FORWARD_PORT,
            remote_server_user="",
            remote_server_host="",
            remote_server_port=PortForward.DEFAULT_SSH_PORT,
            key="",
        )

    @staticmethod
    def from_dict(data: dict) -> "PortForward":
        """Create a port forward from a dictionary. If a key is not present, the default value will be used."""
        port_forward = PortForward.default()
        port_forward.name = data.get("name", port_forward.name)
        port_forward.notes = data.get("notes", port_forward.notes)
        port_forward.local_port = data.get("local_port", port_forward.local_port)
        port_forward.target_host = data.get("target_host", port_forward.target_host)
        port_forward.target_port = data.get("target_port", port_forward.target_port)
        port_forward.remote_server_user = data.get("remote_server_user", port_forward.remote_server_user)
        port_forward.remote_server_host = data.get("remote_server_host", port_forward.remote_server_host)
        port_forward.remote_server_port = data.get("remote_server_port", port_forward.remote_server_port)
        port_forward.key = data.get("key", port_forward.key)
        return port_forward
