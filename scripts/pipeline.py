"""
pipeline.py
-----------
Orquestrador central do projeto Kyros Leads.
"""

import subprocess
import sys
import os

def run_script(script_name):
    """Executa um script Python e aguarda sua conclusão."""
    script_path = os.path.join("scripts", script_name)
    
    print(f"\n" + "="*50)
    print(f"RUN: INICIANDO ETAPA: {script_name}")
    print("="*50 + "\n")
    
    try:
        subprocess.run([sys.executable, script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nERROR ao executar {script_name}: {e}")
        return False
    except FileNotFoundError:
        print(f"\nERROR: O arquivo {script_path} nao foi encontrado.")
        return False

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)

    print("\n" + "="*50)
    print("  SISTEMA DE PROSPECCAO KYROS LEADS - PIPELINE  ")
    print("="*50)

    if not run_script("scanner_leads.py"):
        print("\nWARN: Interrompendo pipeline devido a erro no Scanner.")
        sys.exit(1)

    if not run_script("gerador_propostas.py"):
        print("\nWARN: Interrompendo pipeline devido a erro no Gerador.")
        sys.exit(1)

    print("\n" + "="*50)
    print("SUCCESS: PIPELINE CONCLUIDO COM SUCESSO!")
    print("INFO: Abra o painel /admin para enviar as propostas.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
