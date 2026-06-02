import json
from pathlib import Path
from typing import List, Optional
from domain.modelos.usuario import Usuario

class UsuarioRepository:
    def __init__(self, caminho_arquivo: str = "data/usuarios.json"):
        self.caminho = Path(caminho_arquivo)
        self.usuarios: List[Usuario] = []
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.usuarios = [Usuario.model_validate(u) for u in dados]
            except Exception as e:
                print(f"Erro ao carregar usuários: {e}")
    
    def _salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump([u.model_dump() for u in self.usuarios], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar usuários: {e}")
    
    def buscar_por_id(self, usuario_id: str) -> Optional[Usuario]:
        for usuario in self.usuarios:
            if usuario.id == usuario_id:
                return usuario
        return None
    
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        for usuario in self.usuarios:
            if usuario.email == email:
                return usuario
        return None
    
    def listar_por_escola(self, escola_id: str) -> List[Usuario]:
        return [u for u in self.usuarios if u.escola_id == escola_id]
    
    def salvar(self, usuario: Usuario) -> bool:
        for i, existing in enumerate(self.usuarios):
            if existing.id == usuario.id:
                self.usuarios[i] = usuario
                self._salvar()
                return True
        self.usuarios.append(usuario)
        self._salvar()
        return True
