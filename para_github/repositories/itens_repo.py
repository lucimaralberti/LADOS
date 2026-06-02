import json, random
from pathlib import Path
from typing import List, Optional, Dict
from domain.modelos.item import Item
from repositories.protocol import ItensRepositoryProtocol
from utils.logger import get_logger

logger = get_logger(__name__)

class ItensRepository(ItensRepositoryProtocol):
    def __init__(self, caminho_arquivo: str = "data/itens.json"):
        self.caminho = Path(caminho_arquivo)
        self.itens: List[Item] = []
        self._indice_id: Dict[str, Item] = {}
        self._indice_descriptor: Dict[str, List[Item]] = {}
        self._carregar()
    
    def _reconstruir_indices(self):
        self._indice_id = {item.id: item for item in self.itens}
        self._indice_descriptor = {}
        for item in self.itens:
            self._indice_descriptor.setdefault(item.descritor, []).append(item)
    
    def _carregar(self):
        if not self.caminho.exists():
            self.itens = []
            self._reconstruir_indices()
            return
        
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            # Converter cada item, tratando total_acertos como possível float
            self.itens = []
            for item_data in dados:
                # Garantir que total_acertos seja float se necessário
                if "total_acertos" in item_data and isinstance(item_data["total_acertos"], int):
                    item_data["total_acertos"] = float(item_data["total_acertos"])
                if "total_taxas_soma" not in item_data:
                    item_data["total_taxas_soma"] = item_data.get("total_acertos", 0.0)
                
                self.itens.append(Item.model_validate(item_data))
            
            self._reconstruir_indices()
            logger.info(f"📚 Carregados {len(self.itens)} itens do arquivo")
        except Exception as e:
            logger.error(f"Erro ao carregar itens: {e}")
            self.itens = []
            self._reconstruir_indices()
    
    def _salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump([item.model_dump() for item in self.itens], f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Dados salvos em {self.caminho}")
        except Exception as e:
            logger.error(f"Erro ao salvar itens: {e}")
    
    def buscar_por_id(self, item_id: str) -> Optional[Item]:
        return self._indice_id.get(item_id)
    
    def buscar_por_descriptor(self, descritor: str) -> List[Item]:
        return self._indice_descriptor.get(descritor, [])
    
    def listar_todos(self) -> List[Item]:
        return self.itens.copy()
    
    def atualizar_item(self, item: Item) -> bool:
        for i, existing in enumerate(self.itens):
            if existing.id == item.id:
                self.itens[i] = item
                self._reconstruir_indices()
                self._salvar()
                return True
        return False
    
    def registrar_aplicacao_discreta(self, item_id: str, acertou: bool) -> None:
        """Registra aplicação discreta (para compatibilidade)"""
        item = self.buscar_por_id(item_id)
        if item:
            item.registrar_aplicacao_discreta(acertou)
            if item.total_aplicacoes >= 10:
                item.recalcular_dificuldade()
            self.atualizar_item(item)
    
    def registrar_aplicacao_continua(self, item_id: str, taxa_acerto: float) -> None:
        """Registra aplicação contínua (NOVO)"""
        item = self.buscar_por_id(item_id)
        if item:
            item.registrar_aplicacao_continua(taxa_acerto)
            if item.total_aplicacoes >= 10:
                item.recalcular_dificuldade()
            self.atualizar_item(item)
