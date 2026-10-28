"""Chat API controller."""
from psycopg_pool import ConnectionPool

from app.config.config import settings
from app.infrastructure.persistence.db_connection import get_connection_pool
from app.infrastructure.repositories.tenant_repository_adapter import TenantRepositoryAdapter
from app.infrastructure.llm.open_api_sdk import consultar_ia
from app.application.use_cases.find_tenant_use_case import FindTenantUseCase


def get(pool: ConnectionPool):
    """Retrieve the tenant."""
    repository = TenantRepositoryAdapter(pool)
    result = FindTenantUseCase(repository).execute("43001")
    print(result)


if __name__ == "__main__":
    connection_pool = get_connection_pool()
    get(connection_pool)

    payload = {
        "config": {
            "api_key": settings.openai_api_key.get_secret_value(),
            "base_url": str(settings.openai_base_url),
            "timeout": 20.0,
            "max_retries": 5,
        },
        "chat": {
            "model": settings.openai_model,
            "max_completion_tokens": settings.openai_max_completion_tokens,
            "response_format": {"type": "text"},
            "sistema": "Eres un asistente experto en desarrollo de software que responde de forma corta y directa.",
            "usuario": "¿Por qué es buena idea desacoplar el SDK del proveedor en una arquitectura de IA?"
        }
    }

    print("Enviando consulta a la IA configurada...")
    resultado = consultar_ia(payload)
    print("\n--- Respuesta Recibida ---")
    print(resultado)
