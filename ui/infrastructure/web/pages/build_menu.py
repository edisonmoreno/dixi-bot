import streamlit as st
from infrastructure.auth_service import logout

PAGE_PREFIX = "infrastructure/web/pages"


def build_pages(site_type: str, role: str):
    pages = {}

    if site_type == "ADMIN":
        pages["Plataforma"] = [
            st.Page(f"{PAGE_PREFIX}/platform/tenants.py", title="Clientes",
                    icon=":material/store:"),
            st.Page(f"{PAGE_PREFIX}/platform/tenants_form.py", title="Formulario de cliente",
                    url_path="cliente-formulario", visibility="hidden"),
            st.Page(f"{PAGE_PREFIX}/platform/usage.py", title="Uso y consumo",
                    icon=":material/monitoring:"),
            st.Page(f"{PAGE_PREFIX}/platform/ingestion.py", title="Ingesta",
                    icon=":material/error:"),
        ]
    else:
        if role in ("OWNER", "ADMIN"):
            pages["Chatbot"] = [
                st.Page(f"{PAGE_PREFIX}/tenant/dashboard.py", title="Dashboard",
                        icon=":material/dashboard:"),
                st.Page(f"{PAGE_PREFIX}/tenant/conversations.py", title="Conversaciones",
                        icon=":material/chat:"),
                st.Page(f"{PAGE_PREFIX}/tenant/documents.py", title="Documentos",
                        icon=":material/menu_book:"),
            ]
            pages["Configuración"] = [
                st.Page(f"{PAGE_PREFIX}/tenant/company.py", title="Empresa",
                        icon=":material/store:"),
                st.Page(f"{PAGE_PREFIX}/tenant/agent.py", title="Agente",
                        icon=":material/smart_toy:"),
                st.Page(f"{PAGE_PREFIX}/tenant/channels.py", title="Canales",
                        icon=":material/forum:"),
                st.Page(f"{PAGE_PREFIX}/tenant/team.py", title="Equipo",
                        icon=":material/group:"),
            ]
        elif role == "AGENT":
            pages["Atención"] = [
                st.Page(f"{PAGE_PREFIX}/agent/conversations.py", title="Mis conversaciones",
                        icon=":material/chat:"),
            ]

    pages["Cuenta"] = [
        st.Page(f"{PAGE_PREFIX}/account/profile.py", title="Perfil",
                icon=":material/manage_accounts:", visibility="hidden"),
        st.Page(logout, title="Cerrar sesión",
                icon=":material/logout:", url_path="logout",  visibility="hidden"),
    ]
    return pages


def page_profile():
    return st.Page(f"{PAGE_PREFIX}/account/profile.py", title="Perfil",
                   icon=":material/manage_accounts:", url_path="profile")


def page_logout():
    return st.Page(logout, title="Cerrar sesión",
                   icon=":material/logout:", url_path="logout")
