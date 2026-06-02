from services.supabase_service import supabase_service

print("1. Verificando cliente Supabase:")
print(f"   Client: {supabase_service.client}")
print(f"   URL: {supabase_service.url}")
print(f"   KEY: {supabase_service.key[:50] if supabase_service.key else 'None'}...")

print("")
print("2. Testando conexão:")
if supabase_service.client:
    print("   ✅ Cliente conectado com sucesso!")
    
    print("")
    print("3. Testando autenticacao:")
    try:
        result = supabase_service.client.table("usuarios").select("*").eq("email", "admin@lados.com").execute()
        if result.data:
            user = result.data[0]
            print(f"   ✅ Usuario encontrado: {user['nome']}")
            print(f"   Senha no banco: {user['senha']}")
            print(f"   Senha informada: admin123")
            if user['senha'] == "admin123":
                print("   ✅ Senha correta!")
            else:
                print(f"   ❌ Senha incorreta. Esperado: admin123, Encontrado: {user['senha']}")
        else:
            print("   ❌ Usuario nao encontrado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
else:
    print("   ❌ Cliente NAO conectado")
    print("   Verifique suas credenciais no arquivo .env")
