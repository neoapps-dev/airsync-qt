from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Device:
    name: str
    ip_address: str
    port: int
    id: UUID = uuid4()
    wallpaper: str = ""
