import json
from copy import deepcopy

import streamlit as st

from infrastructure.web.pages.platform.tenant_demo_data import DEFAULT_SETTINGS


STATUS_LABELS = {
    "ACTIVE": "Activo",
    "SUSPENDED": "Suspendido",
    "INACTIVE": "Inactivo",
}
PLAN_OPTIONS = ["FREE", "BASIC", "PRO", "ENTERPRISE"]

tenant_code = st.query_params.get("code")

st.title("Editar cliente" if tenant_code else "Crear cliente")
st.caption("Configura la empresa y los parámetros del modelo de chat.")

if st.button(":material/arrow_left_alt: Volver a clientes"):
    st.switch_page("infrastructure/web/pages/platform/tenants.py")

if tenant_code:
    st.warning(
        "La carga del cliente para edición todavía no está conectada al API."
    )
    st.stop()

current_settings = deepcopy(DEFAULT_SETTINGS)
chat_settings = {
    **DEFAULT_SETTINGS["chat"],
    **current_settings.get("chat", {}),
}

st.subheader("Empresa")
name = st.text_input(
    "Nombre de la empresa",
    max_chars=200,
    placeholder="Nombre de la organización",
)

columns = st.columns(2)
status = columns[0].selectbox(
    "Estado",
    options=list(STATUS_LABELS),
    format_func=lambda value: STATUS_LABELS[value],
    filter_mode=None
)
plan = columns[1].selectbox(
    "Plan",
    options=PLAN_OPTIONS,
    format_func=lambda value: value.replace("_", " ").title(),
    filter_mode=None
)

(model_tab,) = st.tabs(["Configuración del modelo"])
with model_tab:
    chat_columns = st.columns(2)
    chat_provider = chat_columns[0].text_input(
        "Proveedor",
        value=chat_settings["provider"],
        key="chat_provider",
    )
    chat_model = chat_columns[1].text_input(
        "Modelo",
        value=chat_settings["model"],
        key="chat_model",
    )
    chat_base_url = chat_columns[0].text_input(
        "URL base",
        value=chat_settings["base_url"],
        key="chat_base_url",
    )
    chat_api_key = chat_columns[1].text_input(
        "Clave API",
        value=chat_settings.get("api_key", ""),
        type="password",
        key="chat_api_key",
        help="Se incluye en el payload; no se persiste desde esta página.",
    )
    chat_temperature = chat_columns[0].number_input(
        "Temperatura",
        min_value=0.0,
        max_value=2.0,
        value=float(chat_settings["temperature"]),
        step=0.1,
        key="chat_temperature",
    )
    chat_timeout = chat_columns[1].number_input(
        "Tiempo de espera (segundos)",
        min_value=1,
        value=int(chat_settings["timeout"]),
        step=1,
        key="chat_timeout",
    )
    chat_max_retries = chat_columns[0].number_input(
        "Reintentos máximos",
        min_value=0,
        value=int(chat_settings["max_retries"]),
        step=1,
        key="chat_max_retries",
    )

if st.button(
    "Preparar configuración",
    type="primary",
    width="stretch",
):
    if not name.strip():
        st.error("Completa el nombre de la empresa.")
    elif not chat_provider.strip() or not chat_model.strip():
        st.error("Completa el proveedor y el modelo de chat.")
    else:
        settings = deepcopy(current_settings)
        settings["chat"] = {
            "provider": chat_provider.strip(),
            "model": chat_model.strip(),
            "base_url": chat_base_url.strip(),
            "api_key": chat_api_key,
            "temperature": chat_temperature,
            "timeout": chat_timeout,
            "max_retries": chat_max_retries,
        }
        payload = {
            "name": name.strip(),
            "status": status,
            "plan": plan,
            "settings": settings,
        }
        preview_payload = deepcopy(payload)
        preview_payload["settings"]["chat"]["api_key"] = (
            "***" if chat_api_key else ""
        )
        st.session_state["tenant_form_payload"] = json.dumps(
            preview_payload,
            ensure_ascii=False,
            indent=2,
        )

if payload_json := st.session_state.get("tenant_form_payload"):
    st.info("La persistencia del cliente en el API aún no está conectada.")
    st.subheader("Configuración preparada")
    st.code(payload_json, language="json")
