"""
scanner_leads.py
----------------
Robô Caçador de Leads — prospecção automática via Google Maps (Serper.dev).
Busca comércios e serviços locais em Três Corações e Varginha que NÃO possuem
website, indicando maior chance de converter uma venda de presença digital.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# ── Carrega variáveis de ambiente ────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

SUPABASE_URL  = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY  = (os.getenv("SUPABASE_KEY") or "").strip()
SERPER_KEY    = (os.getenv("SERPER_API_KEY") or "").strip()

# ── Validação das credenciais ────────────────────────────────────────────────
if not all([SUPABASE_URL, SUPABASE_KEY, SERPER_KEY]):
    print("ERROR: Variaveis de ambiente ausentes. Verifique config/.env")
    sys.exit(1)

# ── Configurações da campanha ────────────────────────────────────────────────
import json
ALVOS_PATH = os.path.join(ROOT_DIR, "config", "alvos.json")
try:
    with open(ALVOS_PATH, "r", encoding="utf-8") as f:
        _alvos = json.load(f)
        CIDADES = _alvos.get("cidades", [])
        CATEGORIAS = _alvos.get("categorias", [])
except Exception as e:
    print(f"Erro ao ler config/alvos.json: {e}")
    CIDADES = []
    CATEGORIAS = []

SERPER_ENDPOINT  = "https://google.serper.dev/places"
SUPABASE_TABLE   = "leads_prospeccao"
DELAY_ENTRE_BUSCAS = 1.5  # segundos

# ── Headers reutilizáveis ────────────────────────────────────────────────────
serper_headers = {
    "X-API-KEY":    SERPER_KEY,
    "Content-Type": "application/json",
}

supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


# ── Funções auxiliares ───────────────────────────────────────────────────────

def buscar_no_serper(query: str, cidade: str) -> list[dict]:
    payload = {
        "q": f"{query} em {cidade}",
        "gl": "br",
        "hl": "pt",
        "num": 10,
    }
    try:
        response = requests.post(SERPER_ENDPOINT, json=payload, headers=serper_headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("places", [])
    except Exception as e:
        print(f"  WARN: Erro na busca '{query} em {cidade}': {e}")
        return []

def extrair_lead(lugar: dict, categoria: str, cidade: str) -> dict | None:
    if lugar.get("website"):
        return None
    nome    = lugar.get("title", "").strip()
    telefone = lugar.get("phoneNumber", "").strip()
    nota    = lugar.get("rating")
    if not nome:
        return None
    return {
        "nome_empresa":   nome,
        "telefone":       telefone or None,
        "categoria":      categoria,
        "cidade":         cidade,
        "nota_google":    float(nota) if nota else None,
    }

def salvar_lead(lead: dict) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    try:
        response = requests.post(url, json=lead, headers=supabase_headers, timeout=10)
        if response.status_code == 201:
            return True
        if response.status_code == 409:
            return False
        if response.status_code in (401, 403):
            print(f"  LOCK: Erro de permissao [{response.status_code}] no Supabase.")
            return False
        return False
    except Exception as e:
        print(f"  WARN: Erro ao salvar lead '{lead.get('nome_empresa')}': {e}")
        return False

# ── Loop principal ───────────────────────────────────────────────────────────

def executar_varredura():
    total_encontrados  = 0
    total_salvos       = 0
    total_duplicatas   = 0
    total_com_site     = 0

    print("=" * 60)
    print("ROBO CACADOR DE LEADS -- Iniciando varredura...")
    print("=" * 60)

    for cidade in CIDADES:
        print(f"\nLOC: Cidade: {cidade}")
        print("-" * 40)

        for categoria in CATEGORIAS:
            print(f"  SCAN: Buscando {categoria}...", end=" ", flush=True)

            lugares = buscar_no_serper(categoria, city=cidade) if 'city' in buscar_no_serper.__code__.co_varnames else buscar_no_serper(categoria, cidade)
            encontrados_nesta_busca = len(lugares)
            total_encontrados += encontrados_nesta_busca

            salvos_nesta_busca = 0
            for lugar in lugares:
                lead = extrair_lead(lugar, categoria, cidade)
                if lead is None:
                    total_com_site += 1
                    continue
                if salvar_lead(lead):
                    total_salvos += 1
                    salvos_nesta_busca += 1
                else:
                    total_duplicatas += 1

            print(f"DONE: {encontrados_nesta_busca} resultados -> {salvos_nesta_busca} salvos")
            time.sleep(DELAY_ENTRE_BUSCAS)

    print("\n" + "=" * 60)
    print("SCANNER CONCLUIDO")
    print("=" * 60)
    print(f"  Resultados Totais : {total_encontrados}")
    print(f"  Com Website       : {total_com_site}")
    print(f"  Leads Novos       : {total_salvos}")
    print(f"  Duplicatas        : {total_duplicatas}")
    print("=" * 60)

if __name__ == "__main__":
    executar_varredura()
