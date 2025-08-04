from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class Notification:
    title: str
    body: str
    app: str
    nid: str
    package: str
    id: UUID = field(default_factory=uuid4)