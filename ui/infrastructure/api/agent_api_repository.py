from dataclasses import asdict
import httpx
from domain.model.agent_model import Agent, AgentSettings


class AgentApiRepository:
    def __init__(self, endpoint_url: str):
        self._endpoint_url = endpoint_url

    def get_by_id(self, agent_id: str) -> Agent:
        response = httpx.get(self._endpoint_url, timeout=30)
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
            self._endpoint_url,
            json={"data": asdict(agent)},
            timeout=30,
        )
        response.raise_for_status()
