from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tenant:
    id: str = ""
    name: str = ""
    plan: str = ""
    status: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
