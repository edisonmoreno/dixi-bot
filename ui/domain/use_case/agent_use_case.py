from domain.ports.agent_repository import AgentRepository
from domain.model.agent_model import Agent


class AgentUseCase:
    def __init__(self, repository: AgentRepository):
        self._repository = repository

    def get_by_id(self, agent_id: str) -> Agent:
        return self._repository.get_by_id(agent_id)
