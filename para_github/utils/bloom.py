from enum import Enum

class NivelBloom(str, Enum):
    """Níveis da Taxonomia de Bloom Revisada"""
    LEMBRAR = "Lembrar"
    COMPREENDER = "Compreender"
    APLICAR = "Aplicar"
    ANALISAR = "Analisar"
    AVALIAR = "Avaliar"
    CRIAR = "Criar"
    
    @classmethod
    def listar(cls):
        return [n.value for n in cls]
    
    def peso_por_ano(self, ano: str) -> float:
        """Retorna o peso esperado deste nível para o ano escolar"""
        from pathlib import Path
        import json
        
        pesos_file = Path("data/pesos_bloom.json")
        if pesos_file.exists():
            try:
                with open(pesos_file, "r", encoding="utf-8") as f:
                    pesos = json.load(f)
                ano_data = pesos.get(ano, {})
                return ano_data.get(self.value, 0.05)
            except:
                pass
        # Fallback
        pesos_padrao = {
            NivelBloom.LEMBRAR: 0.30,
            NivelBloom.COMPREENDER: 0.25,
            NivelBloom.APLICAR: 0.20,
            NivelBloom.ANALISAR: 0.12,
            NivelBloom.AVALIAR: 0.07,
            NivelBloom.CRIAR: 0.06
        }
        return pesos_padrao.get(self, 0.05)
