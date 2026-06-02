from enum import Enum

class PerfilUsuario(str, Enum):
    PROFESSOR = "professor"
    COORDENADOR = "coordenador"
    GESTOR = "gestor"
    ADMIN = "admin"

class Permissoes:
    """Centraliza as regras de permissão do sistema baseadas em perfis"""
    
    @staticmethod
    def pode_gerenciar_turmas(perfil: PerfilUsuario) -> bool:
        return perfil in [PerfilUsuario.PROFESSOR, PerfilUsuario.COORDENADOR, PerfilUsuario.ADMIN]
    
    @staticmethod
    def pode_gerar_prova(perfil: PerfilUsuario) -> bool:
        return perfil in [PerfilUsuario.PROFESSOR, PerfilUsuario.ADMIN]
    
    @staticmethod
    def pode_corrigir_prova(perfil: PerfilUsuario) -> bool:
        return perfil in [PerfilUsuario.PROFESSOR, PerfilUsuario.COORDENADOR, PerfilUsuario.ADMIN]
    
    @staticmethod
    def pode_ver_relatorios_turma(perfil: PerfilUsuario) -> bool:
        return perfil in [PerfilUsuario.PROFESSOR, PerfilUsuario.COORDENADOR, PerfilUsuario.GESTOR, PerfilUsuario.ADMIN]
    
    @staticmethod
    def pode_ver_relatorios_escola(perfil: PerfilUsuario) -> bool:
        return perfil in [PerfilUsuario.COORDENADOR, PerfilUsuario.GESTOR, PerfilUsuario.ADMIN]
    
    @staticmethod
    def pode_gerar_simulado(perfil: PerfilUsuario) -> bool:
        return perfil in [PerfilUsuario.COORDENADOR, PerfilUsuario.ADMIN]
    
    @staticmethod
    def pode_gerenciar_usuarios(perfil: PerfilUsuario) -> bool:
        return perfil == PerfilUsuario.ADMIN
    
    @staticmethod
    def pode_gerenciar_escolas(perfil: PerfilUsuario) -> bool:
        return perfil == PerfilUsuario.ADMIN
