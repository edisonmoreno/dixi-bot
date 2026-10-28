import streamlit as st
from services.auth_service import logout


def build_pages(site_type: str, role: str):
    pages = {}

    if site_type == "ADMIN":
        pages["Plataforma"] = [
            st.Page("pages/platform/tenants.py", title="Clientes",
                    icon=":material/apartment:"),
            st.Page("pages/platform/tenants_form.py", title="Formulario de cliente",
                    url_path="cliente-formulario", visibility="hidden"),
            st.Page("pages/platform/usage.py", title="Uso y consumo",
                    icon=":material/monitoring:"),
            st.Page("pages/platform/ingestion.py", title="Ingesta",
                    icon=":material/error:"),
        ]
    else:
        if role in ("OWNER", "ADMIN"):
            pages["Chatbot"] = [
                st.Page("pages/tenant/dashboard.py", title="Dashboard",
                        icon=":material/dashboard:"),
                st.Page("pages/tenant/conversations.py", title="Conversaciones",
                        icon=":material/chat:"),
                st.Page("pages/tenant/documents.py", title="Documentos",
                        icon=":material/menu_book:"),
            ]
            pages["Configuración"] = [
                st.Page("pages/tenant/channels.py", title="Canales",
                        icon=":material/forum:"),
                st.Page("pages/tenant/agent.py", title="Agente",
                        icon=":material/smart_toy:"),
                st.Page("pages/tenant/team.py", title="Equipo",
                        icon=":material/group:"),
            ]
        elif role == "AGENT":
            pages["Atención"] = [
                st.Page("pages/agent/conversations.py", title="Mis conversaciones",
                        icon=":material/chat:"),
            ]

    pages["Cuenta"] = [
        st.Page("pages/account/profile.py", title="Perfil",
                icon=":material/manage_accounts:", visibility="hidden"),
        st.Page(logout, title="Cerrar sesión",
                icon=":material/logout:", url_path="logout",  visibility="hidden"),
    ]
    return pages


def page_profile():
    return st.Page("pages/account/profile.py", title="Perfil",
                   icon=":material/manage_accounts:", url_path="profile")


def page_logout():
    return st.Page(logout, title="Cerrar sesión",
                   icon=":material/logout:", url_path="logout")
