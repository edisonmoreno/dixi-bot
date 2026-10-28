import os
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import toml
import time
import requests
import json
from utils.cookies import get_user_cookie, set_user_cookie, delete_user_cookie
from services.auth_service import decode_token
from services.auth_service import exchange_code
from components.buttons import redirect_button, redirect_logout
from pages.build_menu import build_pages, page_profile, page_logout
from services.auth_service import logout

st.logo(
    image="https://a.favicon.im/reddit.com",
    link="http://localhost:8501/",
    icon_image="https://a.favicon.im/reddit.com"
)
st.set_page_config(
    page_title="Dixibot",
    page_icon=":material/robot:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
# Evitar saltos visuales en la UI
st.html("""
    <style>
    div[data-testid='element-container']:has(iframe[title='streamlit_cookies_controller.cookie_controller.cookie_controller']){
        display:none;
    }
    </style>
""")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_DIR = os.path.join(BASE_DIR, ".streamlit")
COOKIE_SESSION = "dixi_session"

headers = st.context.headers
host = headers.get("Host", "")
domain = host.split(":")[0]
secret_file = "secrets_app.toml"
site_type = "APP"

if domain.startswith("admin."):
    secret_file = "secrets_admin.toml"
    site_type = "ADMIN"

secret_path = os.path.abspath(os.path.join(SECRETS_DIR, secret_file))
try:
    config = toml.load(secret_path)["cognito"]
except FileNotFoundError:
    st.error(
        f"Error: No se encontró el archivo de configuración {secret_path}")
    st.stop()
except KeyError:
    st.error(f"Error: Falta la sección [cognito] dentro de {secret_path}")
    st.stop()
except (toml.TomlDecodeError, OSError) as e:
    st.error(f"Error de infraestructura: {e}")
    st.stop()

if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.get("logging_out"):
    logout_url = f"{config['domain']}/logout?" + urllib.parse.urlencode({
        "client_id": config["client_id"],
        "logout_uri": config["redirect_uri"],
    })
    redirect_logout(COOKIE_SESSION, logout_url)
    st.stop()

auth_code = st.query_params.get("code")

if st.session_state.user_profile is None:
    user_token = get_user_cookie(COOKIE_SESSION)

    if user_token:
        try:
            st.session_state.user_profile = decode_token(user_token)
        except ValueError:
            delete_user_cookie(COOKIE_SESSION)

    elif auth_code:
        try:
            id_token = exchange_code(auth_code, config)
            profile = decode_token(id_token)
        except Exception as e:
            st.query_params.clear()
            st.warning("El inicio de sesión expiró, intenta de nuevo.")
            st.exception(e)          # temporal, para depurar
        else:
            st.session_state.user_profile = profile
            set_user_cookie(COOKIE_SESSION, id_token)
            st.query_params.clear()

    if st.session_state.user_profile is None:
        params = urllib.parse.urlencode({
            "client_id": config["client_id"],
            "response_type": "code",
            "scope": config["scope"],
            "redirect_uri": config["redirect_uri"],
        })
        url_authentication = f"{config['domain']}/login?{params}"
        redirect_button("Iniciar sesión",
                        url_authentication,
                        type="primary",
                        icon=":material/login:")
        st.stop()


pg = st.navigation(build_pages(site_type, "OWNER"))
pg.run()
with st.sidebar:
    action_available = st.selectbox(
        "Disponibilidad",
        options=["Disponible", "Ocupado", "Ausente", "Desconectado"],
        label_visibility="visible",
        filter_mode=None
    )
    # if action_available and action_available != current:
    #     update_availability(tenant_id, user_id, new)

    action_account = st.menu_button(f":material/account_box: {st.session_state.user_profile['full_name']}",
                                    options=["PROFILE", "CONFIG", "LOGOUT"],
                                    format_func=lambda x: {
                                        "LOGOUT": ":material/logout: Cerrar sesión",
                                        "PROFILE": ":material/manage_accounts: Perfil",
                                        "CONFIG": ":material/settings: Configuración"}[x],
                                    width="stretch",
                                    key="account_menu",
                                    )
    if action_account == "PROFILE":
        st.switch_page(page_profile())
    if action_account == "LOGOUT":
        st.switch_page(page_logout())


with st.bottom:
    col1, col2 = st.columns(2)

    with col1:
        st.caption("© 2026 My Company · All rights reserved",
                   text_alignment="left")

    with col2:
        st.caption(f"{site_type} | {st.session_state.user_profile['external_id']}",
                   text_alignment="right")
