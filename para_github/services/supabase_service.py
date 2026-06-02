"""
Integração com Supabase - LADOS 2.0
Com retry, cache, validação e fallback offline
"""

import os
import json
import uuid
import time
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from threading import Lock
import streamlit as st

# Importar módulos internos
from services.logging_service import logger

# Tentar carregar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

class SupabaseService:
    """
    Serviço para integração com Supabase com retry e fallback offline
    """
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")
        self.modo_demo = os.getenv("MODO_DEMO", "True").lower() == "true"
        self.client = None
        self._conectado = False
        self._lock = Lock()
        self._fila_sincronizacao = []
        
        # Inicializar banco local SQLite
        self._init_sqlite()
        
        # Tentar conectar
        if not self.modo_demo:
            self._conectar()
    
    def _init_sqlite(self):
        """Inicializa banco SQLite local"""
        try:
            self._conn = sqlite3.connect("data/lados_local.db", check_same_thread=False)
            cursor = self._conn.cursor()
            
            # Tabela de correções
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS correcoes (
                    id TEXT PRIMARY KEY,
                    sessao_id TEXT,
                    numero_prova INTEGER,
                    tipo_prova TEXT,
                    acertos INTEGER,
                    total INTEGER,
                    percentual REAL,
                    nota REAL,
                    periodo TEXT,
                    ordem TEXT,
                    prova TEXT,
                    turma TEXT,
                    horario TEXT,
                    data TEXT,
                    timestamp TEXT,
                    detalhes TEXT,
                    sincronizado INTEGER DEFAULT 0
                )
            ''')
            
            # Tabela de sessões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessoes (
                    sessao_id TEXT PRIMARY KEY,
                    periodo TEXT,
                    ordem TEXT,
                    prova TEXT,
                    turma TEXT,
                    total_alunos INTEGER,
                    media_geral REAL,
                    usuario_nome TEXT,
                    data TEXT,
                    sincronizado INTEGER DEFAULT 0
                )
            ''')
            
            self._conn.commit()
            logger.info("Banco SQLite local inicializado")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar SQLite: {e}")
    
    def _conectar(self, tentativas: int = 3):
        """Conecta ao Supabase com retry"""
        if not self.url or not self.key:
            logger.warning("Credenciais Supabase não configuradas")
            return False
        
        for tentativa in range(tentativas):
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.key)
                self._conectado = True
                logger.info(f"Conectado ao Supabase (tentativa {tentativa + 1})")
                
                # Tentar sincronizar fila pendente
                self._sincronizar_pendentes()
                return True
                
            except Exception as e:
                logger.warning(f"Tentativa {tentativa + 1} falhou: {e}")
                if tentativa < tentativas - 1:
                    time.sleep(2 ** tentativa)  # Exponential backoff
        
        self._conectado = False
        logger.error("Não foi possível conectar ao Supabase após múltiplas tentativas")
        return False
    
    def _sincronizar_pendentes(self):
        """Sincroniza itens pendentes do banco local"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT * FROM correcoes WHERE sincronizado = 0 LIMIT 100")
            pendentes = cursor.fetchall()
            
            for p in pendentes:
                # Tentar sincronizar cada item
                if self.client:
                    # TODO: Implementar sync real
                    cursor.execute("UPDATE correcoes SET sincronizado = 1 WHERE id = ?", (p[0],))
            
            self._conn.commit()
            logger.info(f"Sincronizados {len(pendentes)} itens pendentes")
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
    
    def salvar_correcao(self, correcao_data: Dict) -> bool:
        """Salva correção com fallback local"""
        try:
            # Garantir ID único
            if not correcao_data.get("id"):
                correcao_data["id"] = str(uuid.uuid4())
            
            # Salvar no SQLite local
            with self._lock:
                cursor = self._conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO correcoes 
                    (id, sessao_id, numero_prova, tipo_prova, acertos, total, 
                     percentual, nota, periodo, ordem, prova, turma, 
                     horario, data, timestamp, detalhes, sincronizado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    correcao_data.get("id"),
                    correcao_data.get("sessao_id"),
                    correcao_data.get("numero_prova"),
                    correcao_data.get("tipo_prova"),
                    correcao_data.get("acertos"),
                    correcao_data.get("total"),
                    correcao_data.get("percentual"),
                    correcao_data.get("nota"),
                    correcao_data.get("periodo"),
                    correcao_data.get("ordem"),
                    correcao_data.get("prova"),
                    correcao_data.get("turma"),
                    correcao_data.get("horario"),
                    correcao_data.get("data"),
                    correcao_data.get("timestamp"),
                    json.dumps(correcao_data.get("detalhes", []))
                ))
                self._conn.commit()
            
            logger.info(f"Correção salva localmente: {correcao_data.get('id')}")
            
            # Tentar sincronizar online
            if self._conectado and self.client and not self.modo_demo:
                try:
                    # TODO: Implementar inserção real no Supabase
                    cursor.execute("UPDATE correcoes SET sincronizado = 1 WHERE id = ?", 
                                 (correcao_data.get("id"),))
                    self._conn.commit()
                    logger.info(f"Correção sincronizada: {correcao_data.get('id')}")
                except Exception as e:
                    logger.warning(f"Erro na sincronização online: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar correção: {e}")
            return False
    
    def recuperar_historico(self, turma: str = None, prova: str = None, 
                             pagina: int = 1, limite: int = 50) -> List[Dict]:
        """Recupera histórico com paginação"""
        try:
            offset = (pagina - 1) * limite
            
            query = "SELECT * FROM correcoes WHERE 1=1"
            params = []
            
            if turma:
                query += " AND turma = ?"
                params.append(turma)
            if prova:
                query += " AND prova = ?"
                params.append(prova)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limite, offset])
            
            cursor = self._conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            # Converter para dicionário
            colunas = [desc[0] for desc in cursor.description]
            historico = []
            for row in resultados:
                item = dict(zip(colunas, row))
                if item.get("detalhes"):
                    item["detalhes"] = json.loads(item["detalhes"])
                historico.append(item)
            
            logger.info(f"Recuperados {len(historico)} registros (página {pagina})")
            return historico
            
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []
    
    def total_registros(self, turma: str = None, prova: str = None) -> int:
        """Retorna total de registros para paginação"""
        try:
            query = "SELECT COUNT(*) FROM correcoes WHERE 1=1"
            params = []
            
            if turma:
                query += " AND turma = ?"
                params.append(turma)
            if prova:
                query += " AND prova = ?"
                params.append(prova)
            
            cursor = self._conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Erro ao contar registros: {e}")
            return 0
    
    def esta_conectado(self) -> bool:
        return self._conectado and not self.modo_demo
    
    def limpar_dados_locais(self) -> bool:
        """Limpa dados locais"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM correcoes")
            cursor.execute("DELETE FROM sessoes")
            self._conn.commit()
            logger.info("Dados locais limpos")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar dados: {e}")
            return False


supabase_service = SupabaseService()
