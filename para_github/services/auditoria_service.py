from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
import hashlib

class AuditoriaService:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def registrar_acao(self, usuario_id: str, acao: str, detalhes: Optional[Dict] = None):
        """Registra uma ação do usuário no log de auditoria"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "usuario_id": usuario_id,
            "acao": acao,
            "detalhes": detalhes or {},
            "hash": ""
        }
        
        # Gerar hash para integridade
        conteudo = f"{log_entry['timestamp']}{usuario_id}{acao}"
        log_entry["hash"] = hashlib.sha256(conteudo.encode()).hexdigest()[:16]
        
        filename = self.log_dir / f"auditoria_{datetime.now().strftime('%Y%m%d')}.json"
        
        logs = []
        if filename.exists():
            with open(filename, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def registrar_exportacao(self, usuario_id: str, relatorio_tipo: str, arquivo: str):
        """Registra exportação de relatório (especial para segurança)"""
        self.registrar_acao(usuario_id, "exportacao", {
            "tipo_relatorio": relatorio_tipo,
            "arquivo": arquivo
        })
    
    def obter_logs_por_usuario(self, usuario_id: str) -> List[Dict]:
        """Obtém logs de um usuário específico"""
        logs = []
        for log_file in self.log_dir.glob("auditoria_*.json"):
            with open(log_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                logs.extend([l for l in dados if l["usuario_id"] == usuario_id])
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)
