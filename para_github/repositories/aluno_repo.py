import json
from pathlib import Path
from typing import List, Optional
from domain.modelos.aluno import Aluno

class AlunoRepository:
    def __init__(self, caminho_arquivo: str = "data/alunos.json"):
        self.caminho = Path(caminho_arquivo)
        self.alunos: List[Aluno] = []
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.alunos = [Aluno.model_validate(a) for a in dados]
            except Exception as e:
                print(f"Erro ao carregar alunos: {e}")
    
    def _salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump([a.model_dump() for a in self.alunos], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar alunos: {e}")
    
    def buscar_por_id(self, aluno_id: str) -> Optional[Aluno]:
        for aluno in self.alunos:
            if aluno.id == aluno_id:
                return aluno
        return None
    
    def buscar_por_turma(self, turma_id: str) -> List[Aluno]:
        return [a for a in self.alunos if a.turma_id == turma_id]
    
    def buscar_por_escola(self, escola_id: str) -> List[Aluno]:
        return [a for a in self.alunos if a.escola_id == escola_id]
    
    def salvar(self, aluno: Aluno) -> bool:
        for i, existing in enumerate(self.alunos):
            if existing.id == aluno.id:
                self.alunos[i] = aluno
                self._salvar()
                return True
        self.alunos.append(aluno)
        self._salvar()
        return True
