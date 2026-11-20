from application.config import settings
from domain.use_case.agent_use_case import AgentUseCase
from domain.use_case.tenant_use_case import TenantUseCase
from infrastructure.api.agent_api_repository import AgentApiRepository
from infrastructure.api.tenant_api_repository import TenantApiRepository
from infrastructure.api.api_config_model import ApiConfig


def _build_api_config(path: str) -> ApiConfig:
    endpoint_url = f"{str(settings.url_host).rstrip('/')}/{path.lstrip('/')}"
    return ApiConfig(
        url=endpoint_url,
        headers={
            "x-api-key": settings.url_api_key.get_secret_value()
        },
        timeout=settings.url_timeout_seconds
    )


def build_agent_use_case() -> AgentUseCase:
    repository = AgentApiRepository(_build_api_config("agent"))
    return AgentUseCase(repository)


def build_tenant_use_case() -> TenantUseCase:
    repository = TenantApiRepository(_build_api_config("tenants"))
    return TenantUseCase(repository)
