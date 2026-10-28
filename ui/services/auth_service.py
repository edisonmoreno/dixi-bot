import streamlit as st
import requests
from utils.crypto import decode_base64


def decode_token(id_token: str):
    """Decode an ID token and return the user's external ID and email."""
    if not id_token or "." not in id_token:
        raise ValueError(
            "El token proporcionado está vacío o no es un JWT válido.")

    try:
        payload_b64 = id_token.split(".")[1]
        payload_claims = decode_base64(payload_b64)

        user_external_id = payload_claims.get("sub", "")
        user_email = payload_claims.get("email", "")
        given_name = payload_claims.get("given_name", "")
        family_name = payload_claims.get("family_name", "")
        user_full_name = (
            payload_claims.get("name")
            or f"{given_name} {family_name}".strip()
            or str(user_email.split("@")[0]).lower()
        )

        return {
            "external_id": user_external_id,
            "email": user_email,
            "given_name": given_name,
            "family_name": family_name,
            "full_name": user_full_name,
        }

    except Exception as e:
        raise ValueError(f"Formato de token corrupto o ilegible: {e}") from e


@st.cache_data(ttl=300, show_spinner=False)
def exchange_code(code: str, config: any) -> str:
    """Exchange an authorization code for an ID token."""
    r = requests.post(
        f"{config['domain']}/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["id_token"]


def logout():
    st.session_state.clear()
    st.session_state["logging_out"] = True
    st.rerun()
