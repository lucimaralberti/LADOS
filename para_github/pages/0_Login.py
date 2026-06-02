import streamlit as st
from core.auth import autenticar_usuario\nst.set_page_config(
    page_title="LADOS - Login",
    page_icon="📘",
    layout="centered"
)\n# CSS para esconder sidebar APENAS NO LOGIN
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="stSidebarHeader"] {
    display: none;
}
#MainMenu {
    visibility: hidden;
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)\nst.markdown("""
<div style="max-width: 400px; margin: auto; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 4px 25px rgba(0,0,0,0.1); text-align: center;">
    <div style="font-size: 28px; font-weight: bold; margin-bottom: 2rem; color: #1e3c72;">📚 LADOS 2.0</div>
</div>
""", unsafe_allow_html=True)\nst.title("Login")\nwith st.form("login_form"):
    usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
    entrar = st.form_submit_button("Entrar", use_container_width=True)\nif entrar:
    if usuario and senha:
        user = autenticar_usuario(usuario, senha)
        if user:
            st.session_state["usuario"] = user
            st.session_state["autenticado"] = True
            st.switch_page("app.py")
        else:
            st.error("❌ Usuário ou senha inválidos")
    else:
        st.error("❌ Preencha usuário e senha")\nst.markdown('</div>', unsafe_allow_html=True)\n
