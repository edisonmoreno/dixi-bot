from dataclasses import asdict
import httpx
from domain.model.agent_model import Agent, AgentSettings
from infrastructure.api.api_config_model import ApiConfig


class AgentApiRepository:
    def __init__(self, api_config: ApiConfig):
        self._api_config = api_config

    def get_by_id(self, agent_id: str) -> Agent:
        response = httpx.get(
            url=self._api_config.url,
            headers=self._api_config.headers,
            timeout=self._api_config.timeout
        )
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
            raise ValueError(
                "La respuesta del API no contiene un objeto 'data' válido.")

        data = payload["data"]
        settings = data.get("settings") or {}

        if not isinstance(settings, dict):
            raise ValueError(
                "La configuración del agente no tiene un formato válido.")

        return Agent(
            name=data.get("name", ""),
            description=data.get("description", ""),
            instructions=data.get("instructions", ""),
            tone=data.get("tone", ""),
            language=data.get("language", ""),
            settings=AgentSettings(
                provider=settings.get("provider", ""),
                model=settings.get("model", ""),
                temperature=float(settings.get("temperature", 0.05)),
                timeout=int(settings.get("timeout", 30)),
                max_tokens=int(settings.get("max_tokens", 1000)),
                max_retries=int(settings.get("max_retries", 5)),
            ),
        )

    def save(self, agent: Agent) -> None:
        response = httpx.put(
            url=self._api_config.url,
            headers=self._api_config.headers,
            timeout=self._api_config.timeout,
            json={"data": asdict(agent)}
        )
        response.raise_for_status()
