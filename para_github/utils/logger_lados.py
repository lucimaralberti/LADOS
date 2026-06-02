"""
Sistema de Log e Reserva - LADOS 2.0
Registra todas as ações e mantém backup de arquivos removidos
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class LadosLogger:
    """Gerenciador de log e backup"""
    
    def __init__(self, log_dir="logs", backup_dir="reserva"):
        self.log_dir = Path(log_dir)
        self.backup_dir = Path(backup_dir)
        self.removidos_dir = self.backup_dir / "arquivos_removidos"
        self.versoes_dir = self.backup_dir / "versoes_anteriores"
        
        # Criar pastas
        self.log_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.removidos_dir.mkdir(exist_ok=True)
        self.versoes_dir.mkdir(exist_ok=True)
        
        # Arquivo de log do dia
        self.log_file = self.log_dir / f"lados_{datetime.now().strftime('%Y%m%d')}.log"
    
    def log(self, acao, detalhe="", tipo="INFO"):
        """Registra ação no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{timestamp}] [{tipo}] {acao} - {detalhe}"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(linha + "\n")
        
        # Também exibir no console
        if tipo == "ERRO":
            print(f"❌ {linha}")
        elif tipo == "AVISO":
            print(f"⚠️ {linha}")
        else:
            print(f"✅ {linha}")
        
        return linha
    
    def mover_para_reserva(self, arquivo, motivo="Remoção"):
        """Move arquivo para pasta de reserva antes de deletar"""
        origem = Path(arquivo)
        if not origem.exists():
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = self.removidos_dir / f"{origem.name}.{timestamp}.backup"
        
        shutil.move(str(origem), str(destino))
        self.log(f"Arquivo movido para reserva", f"{origem.name} → {destino.name} ({motivo})")
        
        return destino
    
    def backup_versao(self, arquivo, motivo="Backup"):
        """Faz backup de uma versão estável antes de modificar"""
        origem = Path(arquivo)
        if not origem.exists():
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = self.versoes_dir / f"{origem.stem}_v{timestamp}{origem.suffix}"
        
        shutil.copy2(str(origem), str(destino))
        self.log(f"Backup criado", f"{origem.name} → {destino.name} ({motivo})")
        
        return destino
    
    def listar_acoes(self, ultimas=50):
        """Lista as últimas ações do log"""
        if not self.log_file.exists():
            print("Nenhum log encontrado")
            return []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        print(f"\n📋 ÚLTIMAS {min(ultimas, len(linhas))} AÇÕES:")
        print("=" * 80)
        for linha in linhas[-ultimas:]:
            print(linha.strip())
        
        return linhas[-ultimas:]

# Instância global para uso nos scripts
logger = LadosLogger()
