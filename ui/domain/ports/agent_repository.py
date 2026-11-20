from typing import Protocol
from domain.model.agent_model import Agent


class AgentRepository(Protocol):
    def get_by_id(self, agent_id: str) -> Agent:
        ...

    def save(self, agent: Agent) -> None:
        ...
