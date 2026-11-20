from dataclasses import dataclass, field


@dataclass
class ApiConfig:
    url: str
    timeout: int
    headers: dict = field(default_factory=dict)
