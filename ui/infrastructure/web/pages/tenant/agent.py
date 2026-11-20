import streamlit as st
import httpx
from domain.model.agent_model import Agent, AgentSettings
from application.fabric import get_agent_use_case

TONES = ["Profesional", "Amigable", "Casual", "Formal", "Informal",
         "Divertido", "Serio", "Creativo", "Empático", "Optimista"]
LANGUAGES = {"es": "Español",
             "en": "Inglés",
             "pt": "Portugués"}
PROVIDERS = {"openai": "OpenAI",
             "anthropic": "Anthropic",
             "google_genai": "Google"}

try:
    agent_model = get_agent_use_case().get_by_id(agent_id="1")
except (httpx.HTTPError, ValueError) as error:
    st.error(f"No se pudo cargar el agente: {error}")
    st.stop()

st.title("Agente")

name = st.text_input(
    "Nombre del agente",
    placeholder="Ingresa el nombre del agente",
    max_chars=100,
    required=True,
    value=agent_model.name
)
description = st.text_area(
    "Descripción",
    placeholder="Describe tu agente",
    max_chars=250,
    value=agent_model.description
)
instructions = st.text_area(
    "Instrucciones",
    placeholder="Cómo debe comportarse el agente, indique las tareas y cómo las completa.",
    max_chars=8000,
    value=agent_model.instructions
)
col1, col2 = st.columns(2)
with col1:
    current_tone = agent_model.tone
    tone = st.selectbox(
        "Tono",
        TONES,
        index=TONES.index(current_tone) if current_tone in TONES else None,
        accept_new_options=True,
        placeholder="Seleccione un tono o ingrese uno nuevo",
    )
with col2:
    current_language = agent_model.language
    language = st.selectbox(
        "Idioma",
        options=LANGUAGES.keys(),
        format_func=lambda code: LANGUAGES.get(code, code),
        index=list(LANGUAGES.keys()).index(
            current_language) if current_language in LANGUAGES else None,
        accept_new_options=False,
        placeholder="Seleccione un idioma o ingrese uno nuevo",
        filter_mode=None,
    )

with st.container(border=True):
    st.subheader("Configuración del modelo")

    col1, col2 = st.columns(2)
    with col1:
        current_provider = agent_model.settings.provider
        provider = st.selectbox(
            "Proveedor",
            options=PROVIDERS.keys(),
            format_func=lambda code: PROVIDERS.get(code, code),
            index=list(PROVIDERS.keys()).index(
                current_provider) if current_provider in PROVIDERS else None,
            placeholder="Seleccione un proveedor",
            filter_mode=None,
        )
        temperature = st.slider(
            "Temperatura",
            0.0,
            2.0,
            value=float(agent_model.settings.temperature)
        )
        timeout = st.slider(
            "Tiempo de espera (en segundos)",
            1,
            300,
            value=int(agent_model.settings.timeout)
        )
    with col2:
        model = st.text_input(
            "Nombre del modelo",
            placeholder="Ingresa el nombre del modelo",
            max_chars=100,
            required=True,
            value=agent_model.settings.model
        )
        max_tokens = st.slider(
            "Máximo de tokens",
            50,
            10000,
            step=50,
            value=int(agent_model.settings.max_tokens)
        )
        max_retries = st.slider(
            "Reintentos",
            2,
            10,
            step=1,
            value=int(agent_model.settings.max_retries)
        )

submitted = st.button("Guardar cambios")

if submitted:
    updated_agent = Agent(
        name=name,
        description=description,
        instructions=instructions,
        tone=tone or "",
        language=language or "",
        settings=AgentSettings(
            provider=provider or "",
            model=model,
            temperature=temperature,
            timeout=timeout,
            max_tokens=max_tokens,
            max_retries=max_retries,
        ),
    )
    st.toast(f"Info: {updated_agent}", icon="😍")

    # try:
    #     AgentApiRepository(endpoint_url).save(updated_agent)
    # except httpx.HTTPError as error:
    #     st.error(f"No se pudieron guardar los cambios: {error}")
    # else:
    #     load_agent.clear()
    #     st.success("Cambios guardados.")
