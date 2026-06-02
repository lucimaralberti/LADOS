# testar_salvamento_prova.py
from services.supabase_service import supabase_service
import json
from datetime import datetime

def salvar_prova_teste(exam_id, turma, ano, disciplina, questoes, gabarito):
    """Função de teste para salvar prova"""
    try:
        print(f"📤 TESTE - Tentando salvar: {exam_id}")
        
        dados = {
            "exam_id": exam_id,
            "nome": f"Prova de {disciplina} - {ano} - {turma}",
            "disciplina": disciplina,
            "ano": ano,
            "qtd_questoes": len(questoes),
            "gabarito": json.dumps(gabarito),
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase_service.client.table("provas").insert(dados).execute()
        print(f"   ✅ Sucesso! ID: {result.data[0]['exam_id']}")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

if __name__ == "__main__":
    # Teste
    salvar_prova_teste(
        exam_id="TESTE_DIRETO_001",
        turma="5º Ano A",
        ano="5º Ano",
        disciplina="Matemática",
        questoes=[1,2,3,4,5],
        gabarito={"1": "A", "2": "B", "3": "C"}
    )
