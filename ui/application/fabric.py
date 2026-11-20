from application.config import settings
from domain.use_case.agent_use_case import AgentUseCase
from domain.use_case.tenant_use_case import TenantUseCase
from infrastructure.api.agent_api_repository import AgentApiRepository
from infrastructure.api.tenant_api_repository import TenantApiRepository


def get_agent_use_case() -> AgentUseCase:
    base_url = str(settings.url_host).rstrip("/")
    endpoint_url = f"{base_url}/agent"
    repository = AgentApiRepository(endpoint_url)
    return AgentUseCase(repository)


def get_tenant_use_case() -> TenantUseCase:
    base_url = str(settings.url_host).rstrip("/")
    endpoint_url = f"{base_url}/tenants"
    repository = TenantApiRepository(endpoint_url)
    return TenantUseCase(repository)
