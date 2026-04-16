"""
gerador_propostas.py
--------------------
VERSAO ESTAVEL: Com logs detalhados e sem travar a interface da central.
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

SUPABASE_URL   = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY   = (os.getenv("SUPABASE_KEY") or "").strip()
OPENROUTER_KEY = (os.getenv("OPENROUTER_API_KEY") or "").strip()

MODELOS = [
    "openrouter/free",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "google/gemma-3-4b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "nvidia/llama-3.1-nemotron-70b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]

supabase_headers = {
    "apikey": SUPABASE_KEY, 
    "Authorization": f"Bearer {SUPABASE_KEY}", 
    "Content-Type": "application/json"
}

def chamar_ia_robusta(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    for modelo in MODELOS:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kyros-leads.app",
            "X-Title": "KyrosV16"
        }
        payload = {"model": modelo, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        
        try:
            print(f"   Tentando IA: {modelo.split('/')[1] if '/' in modelo else modelo}...")
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'].strip()
            
            if res.status_code == 429:
                print("   Aguardando lugar na fila...")
                time.sleep(5)
        except:
            continue
    return None

def executar():
    print("--- MONITOR DE PROPOSTAS KYROS ---")
    print("Modo de Feedback Constante Ativado. O status das IAs sera listado.")
    print("-" * 50)

    while True:
        url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
        # Limita lote para evitar timeout do banco
        params = {"status": "eq.novo", "select": "id,nome_empresa,categoria,cidade,nota_google", "limit": 5}
        
        try:
            res = requests.get(url, headers=supabase_headers, params=params, timeout=15)
            leads = res.json()
        except:
            print("Erro ao ler banco. Tentando de novo em 10s...")
            time.sleep(10)
            continue

        if not leads:
            print("\nNenhum lead novo. Vigiando base...")
            time.sleep(30)
            continue

        print(f"\nLOTE: {len(leads)} leads para processar.")

        for lead in leads:
            nome = lead.get('nome_empresa', 'Empresa')
            print(f"- Processando: {nome}")
            
            nota = lead.get('nota_google') or 'excelente'
            prompt = (
                f"Escreva uma mensagem de WhatsApp para {nome} em {lead.get('cidade')}. "
                f"Comece com Ola, tudo bem? Note que eles tem nota {nota} no Google mas nao tem site. "
                f"Pergunte se pode explicar como isso ajudaria. Seja humano e breve. APENAS a mensagem final."
            )
            
            proposta = chamar_ia_robusta(prompt)
            
            if proposta:
                proposta = proposta.replace('"', '').strip()
                update_url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao?id=eq.{lead['id']}"
                up_res = requests.patch(update_url, json={"texto_proposta": proposta, "status": "gerado"}, headers=supabase_headers)
                
                if up_res.status_code in (200, 204):
                    print(f"   SUCESSO: Proposta salva.")
                else:
                    print(f"   ERRO DB ao salvar.")
            else:
                print(f"   FALHA: IA ocupada para este cliente agora.")
            
            time.sleep(4)

        print("\n--- Lote finalizado. Buscando novos... ---")
        time.sleep(5)

if __name__ == "__main__":
    executar()
