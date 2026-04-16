"""
gerador_propostas.py
--------------------
MODO TRATOR V2: Destravado e com monitoramento de busca.
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
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-4b-it:free",
    "openrouter/free"
]

supabase_headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

def chamar_ia_persistente(prompt: str) -> str | None:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://kyros-leads.app", "X-Title": "KyrosFinal"}
    
    while True:
        for modelo in MODELOS:
            payload = {
                "model": modelo, 
                "messages": [{"role": "system", "content": "Consultor amigavel. Apenas a mensagem final de 3 linhas."}, {"role": "user", "content": prompt}]
            }
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    if 'choices' in data:
                        return data['choices'][0]['message']['content'].strip()
                if res.status_code == 429:
                    print(".", end="", flush=True)
                    time.sleep(4)
                    continue
            except:
                time.sleep(3)
                continue
        print(" (Fila cheia, aguardando 20s...)", end="", flush=True)
        time.sleep(20)

def executar():
    print("ESTEIRA KYROS -- MODO TRATOR ATIVADO")
    print("-" * 60)

    while True:
        print("\n[BUSCA] Consultando novos leads...", end=" ", flush=True)
        
        url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
        # Lote de 5 para ser instantaneo
        params = {"status": "eq.novo", "select": "id,nome_empresa,categoria,cidade,nota_google", "limit": 5}
        
        try:
            res = requests.get(url, headers=supabase_headers, params=params, timeout=15)
            if res.status_code != 200:
                print(f"Erro DB {res.status_code}. Tentando em 10s...")
                time.sleep(10)
                continue
            leads = res.json()
        except Exception as e:
            print(f"Erro conexao: {e}. Tentando em 10s...")
            time.sleep(10)
            continue

        if not leads: 
            print("Nenhum lead pendente. ✅")
            break

        print(f"OK ({len(leads)} encontrados)")

        for lead in leads:
            print(f" -> {lead['nome_empresa']}...", end=" ", flush=True)
            prompt = f"Ola, tudo bem? Notei que a {lead['nome_empresa']} em {lead['cidade']} tem otima nota no Google mas nao tem site. Posso explicar como isso ajuda? Seja humano e breve."
            
            proposta = chamar_ia_persistente(prompt)
            if proposta:
                proposta = proposta.replace('"', '').strip()
                requests.patch(f"{url}?id=eq.{lead['id']}", json={"texto_proposta": proposta, "status": "gerado"}, headers=supabase_headers)
                print("OK")
                time.sleep(4)
            else:
                print("ERRO")
        
        time.sleep(5)

if __name__ == "__main__":
    executar()
