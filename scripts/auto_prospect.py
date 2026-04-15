"""
auto_prospect.py
----------------
Orquestrador Supremo do Projeto Kyros Leads.
Este script executa o fluxo completo em 4 etapas com seguranca anti-duplicata:
1. Scanner (Busca novos leads)
2. Limpeza (Exclui leads invalidos ou sem telefone)
3. Gerador (Cria propostas para novos leads)
4. Disparador (Envia via Z-API apenas para os nao enviados)
"""

import subprocess
import sys
import os
import time
import requests
from dotenv import load_dotenv

# Carrega ambiente para a etapa de limpeza manual rápida
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def limpar_leads_sem_telefone():
    """Conecta no Supabase e deleta registros que nao possuem numero de telefone."""
    print("\n" + "="*60)
    print("ETAPA: LIMPEZA DE LEADS (ANTI-LIXO)")
    print("Removendo leads sem telefone do banco de dados...")

    print("="*60 + "\n")
    
    url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
    }
    # Filtro PostgREST: telefone is null (is.null)
    params = {"telefone": "is.null"}
    
    try:
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code in (200, 204):
            print("   Limpeza concluida! Leads sem telefone foram removidos.")
            return True
        else:
            print(f"   Erro na limpeza: {response.text}")
            return False
    except Exception as e:
        print(f"   Erro ao conectar no Supabase limpeza: {e}")
        return False

def run_step(script_name, description):
    """Executa um script Python da pasta scripts e aguarda a conclusao."""
    script_path = os.path.join("scripts", script_name)
    
    print("\n" + "="*60)
    print(f"📦 ETAPA: {description.upper()}")
    print(f"🚀 Iniciando {script_name}...")
    print("="*60 + "\n")
    
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO na etapa {description}: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ ERRO: O arquivo {script_path} nao foi encontrado.")
        return False

def main():
    # Garante que estamos na raiz do projeto (prospeccao-vendas)
    os.chdir(ROOT_DIR)

    print("\n" + "============================================================")
    print("   SISTEMA DE PROSPECCAO AUTOMATICA KYROS -- MODO SUPREMO   ")
    print("============================================================")

    print("Este script ira Cacar, Limpar, Gerar e Enviar leads sozinho.")
    print("Certifique-se de que o CELULAR esta conectado no Z-API.")

    
    print("Iniciando o processo completo agora...")


    # --- ETAPA 1: SCANNER (GOOGLE MAPS) ---
    if not run_step("scanner_leads.py", "Busca de Novos Leads"):
        print("\n⚠️  Falha no Scanner. Prosseguindo...")

    # --- ETAPA 2: LIMPEZA (SUPABASE DELETE) ---
    # Adicionada para nao gastar Gemini/Z-API com quem nao tem fone
    limpar_leads_sem_telefone()

    # --- ETAPA 3: GERADOR (IA GEMINI) ---
    if not run_step("gerador_propostas.py", "Geração de Propostas (IA Gemini)"):
        print("\n⚠️  Falha no Gerador. Prosseguindo...")

    # --- ETAPA 4: DISPARADOR (Z-API) ---
    if not run_step("disparo_automatico.py", "Disparo de WhatsApp (Z-API Cloud)"):
        print("\n❌ Falha critica no Disparador Automático.")
        sys.exit(1)

    print("\n" + "="*60)
    print("🏆 PROSPECÇÃO AUTOMATIZADA CONCLUÍDA COM SUCESSO!")
    print("📊 Verifique seu Painel Administrativo para acompanhar os retornos.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
