"""
Serviço para criar arquivos ZIP com prova + gabarito
"""

import zipfile
from pathlib import Path
from datetime import datetime
import json

def criar_zip_prova(pdf_path, gabarito_data, output_dir=None):
    """
    Cria um arquivo ZIP contendo a prova PDF e o gabarito
    
    Args:
        pdf_path: Caminho do PDF da prova
        gabarito_data: Dicionário ou caminho do PDF do gabarito
        output_dir: Diretório de saída (opcional)
    
    Returns:
        Caminho do arquivo ZIP criado
    """
    if output_dir is None:
        output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = output_dir / f"pacote_prova_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Adicionar PDF da prova
        zf.write(pdf_path, arcname="prova.pdf")
        
        # Adicionar gabarito (se for PDF)
        if isinstance(gabarito_data, str) and Path(gabarito_data).exists():
            zf.write(gabarito_data, arcname="gabarito_comentado.pdf")
        
        # Adicionar gabarito em JSON (sempre)
        if isinstance(gabarito_data, (list, dict)):
            json_path = output_dir / f"gabarito_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(gabarito_data, f, indent=2, ensure_ascii=False)
            zf.write(json_path, arcname="gabarito.json")
            json_path.unlink()  # Remove temporário
        
        # Adicionar instruções simples
        instrucoes = """INSTRUÇÕES:
1. A prova está no arquivo "prova.pdf"
2. O gabarito oficial está em "gabarito.json"
3. Se disponível, "gabarito_comentado.pdf" contém explicações detalhadas

SISTEMA LADOS - Corrigir provas:
- Acesse o sistema LADOS
- Use a câmera ou upload da prova preenchida
- O sistema corrigirá automaticamente
"""
        instrucoes_path = output_dir / f"instrucoes_{timestamp}.txt"
        instrucoes_path.write_text(instrucoes, encoding='utf-8')
        zf.write(instrucoes_path, arcname="instrucoes.txt")
        instrucoes_path.unlink()
    
    return str(zip_path)
