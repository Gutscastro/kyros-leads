import os
import sys
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# ── Carrega variáveis ────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

def check_env():
    print("\n[STEP 1] VERIFICANDO VARIAVEIS DE AMBIENTE (.env)")
    vars_to_check = ["SUPABASE_URL", "SUPABASE_KEY", "SERPER_API_KEY", "OPENROUTER_API_KEY"]
    all_ok = True
    for v in vars_to_check:
        val = (os.getenv(v) or "").strip()
        if not val or val == "sua_chave_aqui":
            print(f"   X {v}: AUSENTE ou com valor padrao")
            all_ok = False
        else:
            print(f"   OK: {v}")
    return all_ok

def check_supabase():
    print("\n[STEP 2] TESTANDO CONEXAO SUPABASE")
    url = (os.getenv("SUPABASE_URL") or "").strip()
    key = (os.getenv("SUPABASE_KEY") or "").strip()
    if not url or not key: return False
    endpoint = f"{url}/rest/v1/leads_prospeccao?select=id&limit=1"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    try:
        response = requests.get(endpoint, headers=headers, timeout=5)
        if response.status_code == 200:
            print("   OK: Conexao bem-sucedida!")
            return True
        else:
            print(f"   X Erro ao acessar: {response.status_code}")
            return False
    except Exception as e:
        print(f"   X Erro de rede: {e}")
        return False

def check_openrouter():
    print("\n[STEP 3] TESTANDO API OPENROUTER")
    key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    if not key or "sk-or" not in key:
        print("   X Chave OpenRouter nao configurada corretamente.")
        return False
    # Teste de saldo / modelos
    url = "https://openrouter.ai/api/v1/auth/key"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print("   OK: Chave OpenRouter validada!")
            return True
        else:
            print(f"   X Chave invalida ou sem acesso: {response.status_code}")
            return False
    except Exception as e:
        print(f"   X Erro OpenRouter: {e}")
        return False

def main():
    print("="*60)
    print("      DIAGNOSTICO COMPLETO - KYROS LEADS PIPELINE")
    print("="*60)
    
    e_ok = check_env()
    s_ok = check_supabase()
    o_ok = check_openrouter()
    
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    if e_ok and s_ok and o_ok:
        print("TUDO PRONTO! O sistema pode ser operado normalmente.")
    else:
        print("ATENCAO: Corrija os erros marcados acima.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
