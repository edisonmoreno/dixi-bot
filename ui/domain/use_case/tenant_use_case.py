from domain.ports.tenant_repository import TenantRepository
from domain.model.tenant_model import Tenant


class TenantUseCase:
    def __init__(self, repository: TenantRepository):
        self._repository = repository

    def find_all(self) -> list[Tenant]:
        return self._repository.find_all()
