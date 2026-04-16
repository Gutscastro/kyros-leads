"""
gerador_propostas.py
--------------------
ESTEIRA INFINITA: Processa todos os leads pendentes automaticamente em lotes.
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
IA_MODEL       = (os.getenv("IA_MODEL") or "google/gemma-3-4b-it:free").strip()

supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

def chamar_ia_com_retry(prompt: str, max_tentativas=2) -> str | None:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "json", # Simplificado
        "HTTP-Referer": "https://kyros-leads.app",
        "X-Title": "KyrosBot"
    }
    payload = {
        "model": IA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    for tentativa in range(max_tentativas):
        try:
            # Headers corrigidos para Content-Type padrao
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            
            if response.status_code == 429:
                # Espera progressiva
                waittime = 30 + (tentativa * 20)
                print(f" (Limite! Pausando {waittime}s...)", end="", flush=True)
                time.sleep(waittime)
                continue
            else:
                print(f" (Erro {response.status_code})", end="")
        except Exception as e:
            print(f" (Erro rede: {e})", end="")
    return None

def executar_gerador():
    print(f"ESTEIRA INFINITA KYROS -- IA: {IA_MODEL}")
    print("Iniciando processamento automatico de toda a base pendente.")
    print("-" * 60)

    total_geral = 0

    while True:
        # Busca o próximo lote de 10 leads
        url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
        params = {"status": "eq.novo", "select": "id,nome_empresa,categoria,cidade,nota_google", "limit": 10}
        
        try:
            res = requests.get(url, headers=supabase_headers, params=params)
            leads = res.json()
        except:
            print("\nERROR: Falha ao conectar ao banco. Tentando em 10s...")
            time.sleep(10)
            continue

        if not leads:
            print("\n✅ TUDO CONCLUIDO! Nenhum lead pendente encontrado.")
            break

        print(f"\n--- Processando Lote de {len(leads)} leads ---")
        
        for lead in leads:
            nome = lead.get('nome_empresa')
            print(f" -> {nome}...", end=" ", flush=True)
            
            prompt = f"Crie uma abordagem curta de 3 linhas para a empresa {nome} ({lead.get('categoria')}) em {lead.get('cidade')}. Assine Equipe Kyros."
            
            proposta = chamar_ia_com_retry(prompt)
            
            if proposta:
                p_url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao?id=eq.{lead['id']}"
                requests.patch(p_url, json={"texto_proposta": proposta, "status": "gerado"}, headers=supabase_headers)
                print("OK")
                total_geral += 1
            else:
                print("FALHA")
            
            time.sleep(4) # Pausa entre leads do mesmo lote

        print(f"Lote finalizado. Total acumulado: {total_geral}")
        print("Aguardando 8s para o proximo lote...")
        time.sleep(8) 

    print(f"\n" + "="*60)
    print(f"PROCESSO FINALIZADO. {total_geral} propostas criadas no total.")
    print("="*60)

if __name__ == "__main__":
    executar_gerador()
