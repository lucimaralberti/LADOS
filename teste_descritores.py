from services.descritores_service import descritores_service

print("=" * 50)
print("TESTE DE CONEXÃO COM DESCRITORES")
print("=" * 50)

print("\n📖 BNCC - 5º Ano, Matemática:")
descritores = descritores_service.get_descritores_bncc("5º Ano", "Matemática")
print(f"   Encontrados: {len(descritores)} descritores")
for d in descritores[:3]:
    print(f"   - {d['codigo']}: {d['descricao'][:50]}...")

print("\n📖 CNCA - 2º Ano, Português:")
descritores = descritores_service.get_descritores_cnca("2º Ano", "Português")
print(f"   Encontrados: {len(descritores)} descritores")
for d in descritores[:3]:
    print(f"   - {d['codigo']}: {d['descricao'][:50]}...")

print("\n📖 SAEB - 5º Ano, Matemática:")
descritores = descritores_service.get_descritores_saeb("5º Ano", "Matemática")
print(f"   Encontrados: {len(descritores)} descritores")
for d in descritores[:3]:
    print(f"   - {d['codigo']}: {d['descricao'][:50]}...")

print("\n✅ Teste concluído!")
