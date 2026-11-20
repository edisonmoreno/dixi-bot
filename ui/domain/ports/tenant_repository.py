from typing import Protocol
from domain.model.tenant_model import Tenant


class TenantRepository(Protocol):
    def get_by_id(self, tenant_id: str) -> Tenant:
        ...

    def find_all(self) -> list[Tenant]:
        ...

    def save(self, agent: Tenant) -> None:
        ...
