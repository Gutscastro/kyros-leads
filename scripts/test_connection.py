import os
import sys
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# ── Carrega variáveis ────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

def check_env():
    print("\n📦 1. VERIFICANDO VARIÁVEIS DE AMBIENTE (.env)")
    vars_to_check = ["SUPABASE_URL", "SUPABASE_KEY", "SERPER_API_KEY", "GEMINI_API_KEY"]
    all_ok = True
    for v in vars_to_check:
        val = (os.getenv(v) or "").strip()
        if not val or val == "sua_chave_aqui":
            print(f"   ❌ {v}: AUSENTE ou com valor padrão ('sua_chave_aqui')")
            all_ok = False
        else:
            print(f"   ✅ {v}: Preenchida")
    return all_ok

def check_supabase():
    print("\n⚡ 2. TESTANDO CONEXÃO SUPABASE (Tabela leads_prospeccao)")
    url = (os.getenv("SUPABASE_URL") or "").strip()
    key = (os.getenv("SUPABASE_KEY") or "").strip()
    
    if not url or not key: return False
    
    endpoint = f"{url}/rest/v1/leads_prospeccao?select=id&limit=1"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=5)
        if response.status_code == 200:
            print("   ✅ Conexão bem-sucedida! Tabela acessível.")
            return True
        else:
            print(f"   ❌ Erro ao acessar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro de rede/DNS: {e}")
        return False

def check_serper():
    print("\n🔎 3. TESTANDO API SERPER (Google Search)")
    key = (os.getenv("SERPER_API_KEY") or "").strip()
    if not key: return False
    
    url = "https://google.serper.dev/places"
    payload = {"q": "Cafeteria em São Paulo", "num": 1}
    headers = {"X-API-KEY": key, "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print("   ✅ API Serper autorizada e funcionando.")
            return True
        else:
            print(f"   ❌ Erro Serper: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro de rede Serper: {e}")
        return False

def check_gemini():
    print("\n🧠 4. TESTANDO API GEMINI (IA Studio)")
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not key or key == "sua_chave_aqui": return False
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Teste ultra-curto apenas para validar a chave
        response = model.generate_content("Responda apenas 'OK'", 
                                         generation_config=genai.types.GenerationConfig(max_output_tokens=5))
        if "OK" in response.text:
            print("   ✅ API Gemini conectada e respondendo.")
            return True
        else:
            print("   ⚠️ Gemini respondeu, mas não o esperado.")
            return True
    except Exception as e:
        print(f"   ❌ Erro Gemini: {e}")
        return False

def main():
    print("="*60)
    print("      DIAGNÓSTICO COMPLETO - KYROS LEADS PIPELINE")
    print("="*60)
    
    env_ok = check_env()
    supa_ok = check_supabase()
    serp_ok = check_serper()
    gem_ok = check_gemini()
    
    print("\n" + "="*60)
    print("📊 RESULTADO DO TESTE DE INTEGRAÇÃO")
    print("="*60)
    if env_ok and supa_ok and serp_ok and gem_ok:
        print("🚀 TUDO PRONTO! O fluxo completo pode ser iniciado com pipeline.py")
    else:
        print("⚠️  ATENÇÃO: Corrija os erros marcados com ❌ acima antes de rodar.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
