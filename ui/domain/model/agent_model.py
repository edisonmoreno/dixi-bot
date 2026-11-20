from dataclasses import dataclass, field


@dataclass
class AgentSettings:
    provider: str = ""
    model: str = ""
    temperature: float = 0.05
    timeout: int = 30
    max_tokens: int = 1000
    max_retries: int = 5


@dataclass
class Agent:
    name: str = ""
    description: str = ""
    instructions: str = ""
    tone: str = ""
    language: str = ""
    settings: AgentSettings = field(default_factory=AgentSettings)
