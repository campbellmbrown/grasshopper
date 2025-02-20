from dataclasses import dataclass
from enum import Enum


class DeviceType(str, Enum):
    AZURE = "Azure"
    COMPUTER = "Computer"
    RASPBERRY_PI = "Raspberry Pi"
    SERVER = "Server"


DEVICE_TYPE_ICONS = {
    DeviceType.AZURE: "azure.png",
    DeviceType.COMPUTER: "laptop.png",
    DeviceType.RASPBERRY_PI: "rpi.png",
    DeviceType.SERVER: "server.png",
}


@dataclass
class DirectConnection:
    """A direct connection to a server using SSH."""

    DEFAULT_PORT = 22
    DEFAULT_DEVICE_TYPE = DeviceType.SERVER

    device_type: str
    name: str
    user: str
    host: str
    port: int
    key: str
    notes: str

    def command(self) -> str:
        """Get the command to connect to the server."""
        key_arg = f"-i {self.key}" if self.key else ""
        return f"ssh {key_arg} {self.user}@{self.host} -p{self.port}"

    def to_dict(self) -> dict:
        """Convert the direct connection to a dictionary."""
        return {
            "device_type": self.device_type,
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
            device_type=self.device_type,
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
            device_type=DirectConnection.DEFAULT_DEVICE_TYPE,
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
        device_type = data.get("device_type")
        if device_type is not None and device_type in DeviceType:
            direct_connection.device_type = device_type
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

    def command(self) -> str:
        key_arg = f"-i {self.key}" if self.key else ""
        remote_server_arg = f"{self.remote_server_user}@{self.remote_server_host} -p{self.remote_server_port}"
        return f"ssh -N -L {self.local_port}:{self.target_host}:{self.target_port} {remote_server_arg} {key_arg}"

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


@dataclass
class ProxyJump:
    DEFAULT_TARGET_PORT = 22
    DEFAULT_JUMP_PORT = 22
    DEFAULT_DEVICE_TYPE = DeviceType.SERVER

    device_type: str
    name: str
    notes: str
    target_user: str
    target_host: str
    target_port: int
    jump_user: str
    jump_host: str
    jump_port: int
    key: str

    def command(self) -> str:
        key_arg = f"-i {self.key}" if self.key else ""
        jump_arg = f"-J {self.jump_user}@{self.jump_host}:{self.jump_port}"
        target_arg = f"{self.target_user}@{self.target_host} -p{self.target_port}"
        return f"ssh {key_arg} {jump_arg} {target_arg}"

    def to_dict(self) -> dict:
        """Convert the proxy jump to a dictionary."""
        return {
            "device_type": self.device_type,
            "name": self.name,
            "notes": self.notes,
            "target_user": self.target_user,
            "target_host": self.target_host,
            "target_port": self.target_port,
            "jump_user": self.jump_user,
            "jump_host": self.jump_host,
            "jump_port": self.jump_port,
            "key": self.key,
        }

    def copy(self) -> "ProxyJump":
        """Create a copy of the proxy jump."""
        return ProxyJump(
            device_type=self.device_type,
            name=self.name,
            notes=self.notes,
            target_user=self.target_user,
            target_host=self.target_host,
            target_port=self.target_port,
            jump_user=self.jump_user,
            jump_host=self.jump_host,
            jump_port=self.jump_port,
            key=self.key,
        )

    @staticmethod
    def default() -> "ProxyJump":
        """Get a proxy jump containing default values."""
        return ProxyJump(
            device_type=ProxyJump.DEFAULT_DEVICE_TYPE,
            name="",
            notes="",
            target_user="",
            target_host="",
            target_port=ProxyJump.DEFAULT_TARGET_PORT,
            jump_user="",
            jump_host="",
            jump_port=ProxyJump.DEFAULT_JUMP_PORT,
            key="",
        )

    @staticmethod
    def from_dict(data: dict) -> "ProxyJump":
        """Create a proxy jump from a dictionary. If a key is not present, the default value will be used."""
        proxy_jump = ProxyJump.default()
        device_type = data.get("device_type")
        if device_type is not None and device_type in DeviceType:
            proxy_jump.device_type = device_type
        proxy_jump.name = data.get("name", proxy_jump.name)
        proxy_jump.notes = data.get("notes", proxy_jump.notes)
        proxy_jump.target_user = data.get("target_user", proxy_jump.target_user)
        proxy_jump.target_host = data.get("target_host", proxy_jump.target_host)
        proxy_jump.target_port = data.get("target_port", proxy_jump.target_port)
        proxy_jump.jump_user = data.get("jump_user", proxy_jump.jump_user)
        proxy_jump.jump_host = data.get("jump_host", proxy_jump.jump_host)
        proxy_jump.jump_port = data.get("jump_port", proxy_jump.jump_port)
        proxy_jump.key = data.get("key", proxy_jump.key)
        return proxy_jump
