import json
import base64


def decode_base64(texto_base64: str) -> str:
    """Decodifica cualquier cadena Base64 resolviendo caracteres URL y padding."""
    texto_base64 += "=" * (-len(texto_base64) % 4)
    raw = base64.urlsafe_b64decode(texto_base64.encode("ascii"))
    return json.loads(raw)
