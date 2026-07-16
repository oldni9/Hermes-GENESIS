from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from hermes.events.priority import EventPriority


@dataclass(slots=True)
class Event:

    name: str

    source: str

    data: dict = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.utcnow)

    priority: EventPriority = EventPriority.NORMAL

    id: str = ""

    def __post_init__(self):

        if not self.id:

            self.id = uuid4().hex