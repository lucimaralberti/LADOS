import json
from pathlib import Path
from typing import List, Optional
from domain.modelos.escola import Escola

class EscolaRepository:
    def __init__(self, caminho_arquivo: str = "data/escolas.json"):
        self.caminho = Path(caminho_arquivo)
        self.escolas: List[Escola] = []
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.escolas = [Escola.model_validate(e) for e in dados]
            except Exception as e:
                print(f"Erro ao carregar escolas: {e}")
    
    def _salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump([e.model_dump() for e in self.escolas], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar escolas: {e}")
    
    def buscar_por_id(self, escola_id: str) -> Optional[Escola]:
        for escola in self.escolas:
            if escola.id == escola_id:
                return escola
        return None
    
    def buscar_por_codigo_inep(self, codigo_inep: str) -> Optional[Escola]:
        for escola in self.escolas:
            if escola.codigo_inep == codigo_inep:
                return escola
        return None
    
    def listar_todas(self) -> List[Escola]:
        return self.escolas.copy()
    
    def salvar(self, escola: Escola) -> bool:
        for i, existing in enumerate(self.escolas):
            if existing.id == escola.id:
                self.escolas[i] = escola
                self._salvar()
                return True
        self.escolas.append(escola)
        self._salvar()
        return True
