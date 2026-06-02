import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import hashlib

class ExportadorCSV:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def exportar_relatorio(self, dados: List[Dict], nome_base: str, usuario_exportador: str) -> str:
        """Exporta um relatório em CSV com identificador de segurança"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        identificador = hashlib.sha256(f"{usuario_exportador}{timestamp}{nome_base}".encode()).hexdigest()[:16]
        
        filename = self.output_dir / f"{nome_base}_{timestamp}_{identificador}.csv"
        
        if dados:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=dados[0].keys())
                writer.writeheader()
                writer.writerows(dados)
        
        return str(filename)
    
    def exportar_resultados_turma(self, resultados: Dict, turma_id: str, usuario_exportador: str) -> str:
        """Exporta resultados de uma turma formatados"""
        dados_formatados = []
        for resultado in resultados.get("itens", []):
            dados_formatados.append({
                "aluno_id": resultado.get("aluno_id", ""),
                "descritor": resultado.get("descritor", ""),
                "acertou": resultado.get("acertou", False),
                "percentual": resultado.get("percentual", 0)
            })
        return self.exportar_relatorio(dados_formatados, f"turma_{turma_id}", usuario_exportador)
