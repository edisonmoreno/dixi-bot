import json
import uuid
import streamlit as st


def redirect(url: str) -> None:
    """Navega a `url` en la misma pestaña."""
    # El comentario con un id único evita que Streamlit trate el HTML como
    # idéntico al del rerun anterior y no vuelva a ejecutar el script.
    st.html(
        f"<script>/* {uuid.uuid4().hex} */"
        f"window.location.href = {json.dumps(url)};</script>",
        unsafe_allow_javascript=True,
    )


def redirect_button(label: str, url: str, *, type: str = "secondary", **kwargs) -> bool:
    """Botón nativo de Streamlit que redirige a `url` en la misma pestaña.

    `type` y el resto de kwargs (key, icon, use_container_width, disabled,
    help, width...) se pasan tal cual a st.button.
    """
    clicked = st.button(label, type=type, **kwargs)
    if clicked:
        redirect(url)
    return clicked


def redirect_logout(cookie_name: str, url: str) -> None:
    """Borra la cookie en el navegador y luego navega a `url`."""
    st.html(
        f"""<script>
        /* {uuid.uuid4().hex} */
        document.cookie = {json.dumps(cookie_name)} + "=; Max-Age=0; path=/";
        window.location.href = {json.dumps(url)};
        </script>""",
        unsafe_allow_javascript=True,
    )
