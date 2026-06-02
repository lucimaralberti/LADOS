import json
from pathlib import Path
from typing import List, Optional
from domain.modelos.turma import Turma
from utils.logger import get_logger

logger = get_logger(__name__)

class TurmaRepository:
    def __init__(self, caminho_arquivo: str = "data/turmas.json"):
        self.caminho = Path(caminho_arquivo)
        self.turmas: List[Turma] = []
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.turmas = [Turma.model_validate(t) for t in dados]
                logger.info(f"Carregadas {len(self.turmas)} turmas")
            except Exception as e:
                logger.error(f"Erro ao carregar turmas: {e}")
    
    def _salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.turmas], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar turmas: {e}")
    
    def buscar_por_id(self, turma_id: str) -> Optional[Turma]:
        for turma in self.turmas:
            if turma.id == turma_id:
                return turma
        return None
    
    def buscar_por_escola(self, escola_id: str) -> List[Turma]:
        return [t for t in self.turmas if t.escola_id == escola_id]
    
    def buscar_por_professor(self, professor_id: str) -> List[Turma]:
        return [t for t in self.turmas if t.professor_id == professor_id]
    
    def listar_todas(self) -> List[Turma]:
        return self.turmas.copy()
    
    def salvar(self, turma: Turma) -> bool:
        for i, existing in enumerate(self.turmas):
            if existing.id == turma.id:
                self.turmas[i] = turma
                self._salvar()
                return True
        self.turmas.append(turma)
        self._salvar()
        return True
