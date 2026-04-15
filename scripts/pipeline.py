"""
pipeline.py
-----------
Orquestrador central do projeto Kyros Leads.
Este script automatiza o fluxo completo:
1. Chama o Scanner (Busca de leads sem site no Google Maps)
2. Chama o Gerador (Criação de propostas personalizadas com Gemini AI)
"""

import subprocess
import sys
import os

def run_script(script_name):
    """Executa um script Python e aguarda sua conclusão."""
    script_path = os.path.join("scripts", script_name)
    
    print(f"\n" + "="*50)
    print(f"🚀 INICIANDO ETAPA: {script_name}")
    print("="*50 + "\n")
    
    try:
        # Executa o processo e redireciona a saída para o terminal atual
        result = subprocess.run([sys.executable, script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO ao executar {script_name}: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ ERRO: O arquivo {script_path} não foi encontrado.")
        return False

def main():
    # Garante que estamos na raiz do projeto
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    print("\n" + "╔" + "═"*48 + "╗")
    print("║  SISTEMA DE PROSPECÇÃO KYROS LEADS - PIPELINE  ║")
    print("╚" + "═"*48 + "╝")

    # Passo 1: Scanner (Serper.dev)
    if not run_script("scanner_leads.py"):
        print("\n⚠️ Interrompendo pipeline devido a erro no Scanner.")
        sys.exit(1)

    # Passo 2: Gerador (Gemini AI)
    if not run_script("gerador_propostas.py"):
        print("\n⚠️ Interrompendo pipeline devido a erro no Gerador.")
        sys.exit(1)

    print("\n" + "="*50)
    print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
    print("🖥️  Abra o painel /admin para enviar as propostas.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
