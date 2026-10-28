from pathlib import Path
from pydantic import SecretStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    variables de configuración
    """
    # str = Valida que sea texto
    # HttpUrl = Valida que sea una URL válida
    # SecretStr = evita que la clave se imprima por accidente en los logs

    # OpenAI
    openai_base_url: HttpUrl
    openai_model: str
    openai_api_key: SecretStr
    openai_max_completion_tokens: int

    # Postgresql
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_ssl_mode: str
    db_ssl_root_cert: Path = BASE_DIR / "app" / "certs" / "global-bundle.pem"

    # Pool
    db_pool_min_size: int = 1
    db_pool_max_size: int = 5
    # Segundos máximos para abrir una conexión nueva con la base.
    db_connect_timeout: int = 10
    # Segundos máximos que espera una consulta a que se le asigne una conexión libre del pool.
    db_pool_timeout: int = 30
    # Segundos máximos que espera el arranque a que el pool tenga las conexiones listas.
    db_pool_wait_timeout: int = 15

    debug_mode: bool = False  # Valor por defecto si no se define

    # Le indicamos a Pydantic que extraiga los valores desde el archivo .env
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )


# Única instancia global para toda la app
settings = Settings()
