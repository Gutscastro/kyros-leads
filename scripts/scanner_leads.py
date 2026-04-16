"""
scanner_leads.py
----------------
Robô Caçador de Leads - Versão com Filtro de Telefone Obrigatório.
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip()
SERPER_KEY   = (os.getenv("SERPER_API_KEY") or "").strip()

ALVOS_PATH = os.path.join(ROOT_DIR, "config", "alvos.json")
with open(ALVOS_PATH, "r", encoding="utf-8") as f:
    ALVOS = json.load(f)
    CIDADES = ALVOS.get("cidades", [])
    CATEGORIAS = ALVOS.get("categorias", [])

supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

def buscar_serper(query, cidade):
    url = "https://google.serper.dev/places"
    payload = {"q": f"{query} em {cidade}", "gl": "br", "hl": "pt", "num": 10}
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        return res.json().get("places", [])
    except: return []

def salvar_lead(lugar, categoria, cidade):
    # FILTRO: Se nao tem telefone ou ja tem site, descarta
    telefone = lugar.get("phoneNumber")
    possue_site = lugar.get("website")
    
    if possue_site or not telefone:
        return False

    lead = {
        "nome_empresa": lugar.get("title", "Empresa"),
        "telefone":     telefone,
        "categoria":    categoria,
        "cidade":       cidade,
        "nota_google":  lugar.get("rating"),
        "status":       "novo"
    }

    url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
    try:
        res = requests.post(url, json=lead, headers=supabase_headers, timeout=10)
        return res.status_code == 201
    except: return False

def executar():
    print("ROBO CACADOR -- FILTRO DE TELEFONE ATIVADO")
    for cidade in CIDADES:
        print(f"\nCidade: {cidade}")
        for cat in CATEGORIAS:
            print(f" -> Buscando {cat}...", end=" ", flush=True)
            lugares = buscar_serper(cat, cidade)
            salvos = 0
            for lug in lugares:
                if salvar_lead(lug, cat, cidade): salvos += 1
            print(f"OK ({salvos} qualificados)")
            time.sleep(2)

if __name__ == "__main__":
    executar()
