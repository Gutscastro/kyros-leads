"""
diagnostic_kyros.py
-------------------
Script para checar a saúde de todos os componentes do Kyros Leads. (SEM EMOJIS)
"""

import os
import requests
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

def check_env():
    print("--- Verificando Variaveis de Ambiente ---")
    vars = ["SUPABASE_URL", "SUPABASE_KEY", "SERPER_API_KEY", "OPENROUTER_API_KEY"]
    for v in vars:
        val = os.getenv(v)
        status = "OK" if val and len(val) > 10 else "FALTANDO/CURTO"
        print(f"{v}: {status}")

def check_supabase():
    print("\n--- Verificando Banco de Dados (Supabase) ---")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {
        "apikey": key, 
        "Authorization": f"Bearer {key}",
        "Prefer": "count=exact"
    }
    try:
        r = requests.get(f"{url}/rest/v1/leads_prospeccao?select=id&limit=1", headers=headers)
        print(f"Status Conexao: {r.status_code}")
        
        # Estatisticas
        r_novo = requests.get(f"{url}/rest/v1/leads_prospeccao?status=eq.novo&select=id", headers=headers)
        print(f"Leads 'Novo': {r_novo.headers.get('Content-Range')}")
        
        r_gerado = requests.get(f"{url}/rest/v1/leads_prospeccao?status=eq.gerado&select=id", headers=headers)
        print(f"Leads 'Gerado': {r_gerado.headers.get('Content-Range')}")
        
        r_sem_fone = requests.get(f"{url}/rest/v1/leads_prospeccao?telefone=is.null&select=id", headers=headers)
        print(f"Leads SEM TELEFONE (Lixo): {r_sem_fone.headers.get('Content-Range')}")
        
    except Exception as e:
        print(f"Erro Supabase: {e}")

def check_openrouter():
    print("\n--- Verificando IA (OpenRouter) ---")
    key = os.getenv("OPENROUTER_API_KEY")
    headers = {"Authorization": f"Bearer {key}"}
    try:
        r = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if r.status_code == 200:
            models = [m['id'] for m in r.json()['data'] if 'free' in m['id']]
            print(f"Modelos Free Disponiveis: {len(models)}")
        else:
            print(f"Erro OpenRouter: {r.status_code}")
    except Exception as e:
        print(f"Erro Conexao IA: {e}")

if __name__ == "__main__":
    check_env()
    check_supabase()
    check_openrouter()
