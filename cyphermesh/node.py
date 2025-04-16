from enum import Enum


class NodeType(Enum):
    PEER = "peer"
    DISCOVERY = "discovery"

    def __str__(self):
        return self.value


class Node:
    def __init__(self, ip: str, port: int, type: NodeType):
        self.ip = ip
        self.port = port
        self.type = type  # 'peer' o 'discovery'

    def address(self) -> str:
        return f"{self.ip}:{self.port}"

    def to_dict(self):
        return {
            "ip": self.ip,
            "port": self.port,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["ip"], data["port"], data["type"])

    def __eq__(self, other):
        return isinstance(other, Node) and self.address() == other.address()

    def __hash__(self):
        return hash(self.address())
