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
