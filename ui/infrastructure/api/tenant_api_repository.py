from datetime import datetime
import httpx
from domain.model.tenant_model import Tenant


class TenantApiRepository:
    def __init__(self, endpoint_url: str):
        self._endpoint_url = endpoint_url

    def find_all(self) -> list[Tenant]:
        response = httpx.get(self._endpoint_url, timeout=30)
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ValueError(
                "La respuesta del API no contiene un objeto 'data' válido.")

        tenants = []
        for item in payload["data"]:
            if not isinstance(item, dict):
                raise ValueError("Cada elemento de 'data' debe ser un objeto.")
            print(item)
            tenants.append(
                Tenant(
                    id=item["id"],
                    name=item["name"],
                    plan=item["plan"],
                    status=item["status"],
                    created_at=datetime.fromisoformat(item["createdAt"]),
                    updated_at=datetime.fromisoformat(item["updatedAt"])
                )
            )

        return tenants
