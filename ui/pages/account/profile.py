import streamlit as st

st.title("Perfil")
st.write("Perfil y cerrar sesión")

st.write(f"**Correo:** {st.session_state.user_profile['email']}")
st.write(f"**Nombre:** {st.session_state.user_profile['full_name']}")
