from core.auth import autenticar_usuario

user = autenticar_usuario("admin@lados.com", "admin123")
if user:
    print(f"Perfil: '{user.get('perfil')}'")
    print(f"Tipo: {type(user.get('perfil'))}")
else:
    print("Login falhou")
