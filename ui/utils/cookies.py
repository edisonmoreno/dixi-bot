import streamlit as st
from streamlit_cookies_controller import CookieController


def _get_controller():
    """
    Inicializa el controlador de cookies y lo almacena en caché 
    para mitigar parpadeos e inicializaciones repetidas.
    """
    return CookieController()


def set_user_cookie(key: str, value: str):
    """Guarda una cookie en el navegador del cliente."""
    controller = _get_controller()
    controller.set(key, value)


def get_user_cookie(key: str):
    """Obtiene el valor de una cookie específica."""
    controller = _get_controller()
    return controller.get(key)


def delete_user_cookie(key: str):
    """Elimina la cookie del navegador."""
    controller = _get_controller()
    if controller.get(key) is not None:
        controller.remove(key)
