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

    # Application
    url_host: HttpUrl

    # Le indicamos a Pydantic que extraiga los valores desde el archivo .env
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore"  # ToDo: Evaluar si dejar o quitar para que sea estricto
    )


# Única instancia global para toda la app
settings = Settings()
