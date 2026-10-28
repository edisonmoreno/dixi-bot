from copy import deepcopy

import streamlit as st


DEFAULT_SETTINGS = {
    "agent_name": "Asistente",
    "system_prompt": "Eres un asistente útil.",
    "chat": {
        "provider": "openai",
        "model": "gemini-3.5-flash-lite",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key": "",
        "temperature": 0.7,
        "timeout": 20,
        "max_retries": 5,
    },
    "embedding": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "base_url": "https://otra.com",
        "api_key": "",
        "dimensions": 1536,
        "similarity_threshold": 0.7,
        "language": "es",
    },
    "business_hours": {},
    "extra_config": {},
}

DEMO_TENANTS = [
    {
        "code": "acme",
        "name": "Acme Corporation",
        "status": "ACTIVE",
        "plan": "PRO",
        "created_at": "2026-03-12",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Asistente Acme",
            "system_prompt": (
                "Responde consultas sobre productos y pedidos de Acme."
            ),
        },
    },
    {
        "code": "tienda-norte",
        "name": "Tienda Norte",
        "status": "ACTIVE",
        "plan": "FREE",
        "created_at": "2026-05-04",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Nora",
            "system_prompt": "Ayuda a los clientes con sus compras y envíos.",
        },
    },
    {
        "code": "contoso",
        "name": "Contoso Servicios",
        "status": "SUSPENDED",
        "plan": "BASIC",
        "created_at": "2026-01-21",
        "settings": deepcopy(DEFAULT_SETTINGS),
    },
    {
        "code": "demo",
        "name": "Cuenta de demostración",
        "status": "INACTIVE",
        "plan": "FREE",
        "created_at": "2025-11-18",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Demo Bot",
            "system_prompt": (
                "Presenta las funciones principales del servicio."
            ),
        },
    },
    {
        "code": "nube-sur",
        "name": "Nube Sur",
        "status": "ACTIVE",
        "plan": "BASIC",
        "created_at": "2026-06-08",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Suri",
            "system_prompt": "Resuelve dudas sobre servicios en la nube.",
        },
    },
    {
        "code": "lumen",
        "name": "Lumen Studio",
        "status": "ACTIVE",
        "plan": "PRO",
        "created_at": "2026-07-14",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Lumen",
            "system_prompt": "Ayuda con consultas de diseño y proyectos.",
        },
    },
    {
        "code": "verde-vivo",
        "name": "Verde Vivo",
        "status": "SUSPENDED",
        "plan": "FREE",
        "created_at": "2026-08-02",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Vera",
            "system_prompt": "Ofrece información sobre productos sostenibles.",
        },
    },
    {
        "code": "atlas",
        "name": "Atlas Logística",
        "status": "ACTIVE",
        "plan": "ENTERPRISE",
        "created_at": "2026-08-19",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Atlas",
            "system_prompt": "Responde preguntas sobre envíos y seguimiento.",
        },
    },
    {
        "code": "pixel-shop",
        "name": "Pixel Shop",
        "status": "INACTIVE",
        "plan": "BASIC",
        "created_at": "2026-09-11",
        "settings": {
            **deepcopy(DEFAULT_SETTINGS),
            "agent_name": "Pixel",
            "system_prompt": "Asesora a clientes sobre productos electrónicos.",
        },
    },
]


def get_demo_tenants():
    if "tenants_demo" not in st.session_state:
        st.session_state.tenants_demo = deepcopy(DEMO_TENANTS)
    return st.session_state.tenants_demo
