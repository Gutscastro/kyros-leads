"""
disparo_automatico.py 
----------------------
O "Braço Robótico" 100% Cloud do projeto Kyros Leads.
"""

import os
import sys
import re
import time
import requests
from dotenv import load_dotenv

# ── Carrega variáveis ────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ── CONFIGURACOES DA Z-API ───────────────────────────────────────────────────
ZAPI_INSTANCE_ID = "3F1B1724F42872095AF7BA4D31290A14"
ZAPI_TOKEN       = "79C5D45D6EE38E945B4F4BB6"
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
DELAY_ENTRE_DISPAROS = 40 

supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

def buscar_leads_prontos() -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
    params = {
        "status": "eq.gerado",
        "select": "id,nome_empresa,telefone,texto_proposta",
        "order":  "criado_em.asc",
    }
    try:
        print("INFO: Consultando banco de dados...")
        response = requests.get(url, headers=supabase_headers, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"ERROR: Erro ao buscar leads: {e}")
        return []

def tratar_telefone(telefone: str | None) -> str | None:
    if not telefone: return None
    apenas_digitos = re.sub(r"\D", "", telefone)
    if not apenas_digitos: return None
    if apenas_digitos.startswith("55") and len(apenas_digitos) >= 12:
        return apenas_digitos
    return f"55{apenas_digitos}"

def enviar_via_zapi(numero: str, mensagem: str) -> bool:
    payload = {"phone": numero, "message": mensagem}
    headers = {
        "Client-Token": "Fd7b6012fae6f4372a20760d7ebb747f6S",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(ZAPI_URL, json=payload, headers=headers, timeout=20)
        return response.status_code in (200, 201, 204)
    except Exception as e:
        print(f"  WARN: Erro de rede com a Z-API: {e}")
        return False

def marcar_enviado(lead_id: str) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/leads_prospeccao"
    params  = {"id": f"eq.{lead_id}"}
    payload = {"status": "enviado"}
    try:
        response = requests.patch(url, json=payload, headers=supabase_headers, params=params, timeout=10)
        return response.status_code in (200, 201, 204)
    except Exception: return False

def disparar_tudo():
    print("\n" + "="*65)
    print("DISPARO AUTOMATICO (Z-API) -- KYROS LEADS")
    print("="*65)

    leads = buscar_leads_prontos()
    if not leads:
        print("INFO: Tudo em dia! Nenhum lead pronto encontrado.")
        return

    print(f"INFO: Iniciando sequencia de {len(leads)} disparos...")

    enviados = 0
    falhas   = 0

    for i, lead in enumerate(leads, start=1):
        nome    = lead["nome_empresa"]
        numero  = tratar_telefone(lead["telefone"])
        texto   = lead["texto_proposta"]
        lead_id = lead["id"]

        if not numero or not texto:
            print(f"[{i}/{len(leads)}] SKIP: {nome} (Dados incompletos)")
            continue

        print(f"[{i}/{len(leads)}] SEND: {nome} ({numero})...", end=" ", flush=True)

        if enviar_via_zapi(numero, texto):
            marcar_enviado(lead_id)
            print("OK")
            enviados += 1
            if i < len(leads):
                print(f"WAIT: Aguardando {DELAY_ENTRE_DISPAROS}s...")
                time.sleep(DELAY_ENTRE_DISPAROS)
        else:
            print("FAIL")
            falhas += 1
            time.sleep(2)

    print("\n" + "="*65)
    print("RELATORIO FINAL")
    print(f"   Enviados : {enviados}")
    print(f"   Falhas   : {falhas}")
    print("=" * 65)

if __name__ == "__main__":
    disparar_tudo()
