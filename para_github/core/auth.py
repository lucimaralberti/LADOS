def autenticar_usuario(usuario, senha):
    usuarios = {
        "admin": {"senha": "123", "nome": "Administrador", "perfil": "admin"},
        "professor1": {"senha": "prof123", "nome": "Professor", "perfil": "professor"},
        "coordenador1": {"senha": "coord123", "nome": "Coordenador", "perfil": "coordenador"}
    }
    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        return usuarios[usuario]
    return None

def get_current_user():
    import streamlit as st
    return st.session_state.get("usuario", {})
