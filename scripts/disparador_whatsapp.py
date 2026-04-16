"""
disparador_whatsapp.py
----------------------
Disparador semi-automático de propostas via WhatsApp.
"""

import os
import sys
import re
import time
import webbrowser
from urllib.parse import quote
import requests
from dotenv import load_dotenv

# ── Carrega variáveis de ambiente ─────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ── Validação ─────────────────────────────────────────────────────────────────
if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL ou SUPABASE_KEY ausentes no config/.env")
    sys.exit(1)

# ── Configurações ─────────────────────────────────────────────────────────────
TABELA = "leads_prospeccao"
supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

def buscar_leads_gerados() -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params = {
        "status": "eq.gerado",
        "select": "id,nome_empresa,telefone,texto_proposta,cidade",
        "order":  "criado_em.asc",
    }
    try:
        response = requests.get(url, headers=supabase_headers, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"ERROR: Erro ao buscar leads no Supabase: {e}")
        sys.exit(1)

def tratar_telefone(telefone: str | None) -> str | None:
    if not telefone: return None
    apenas_digitos = re.sub(r"\D", "", telefone)
    if not apenas_digitos: return None
    if apenas_digitos.startswith("55") and len(apenas_digitos) >= 12:
        return apenas_digitos
    return f"55{apenas_digitos}"

def montar_link_whatsapp(telefone: str, texto: str) -> str:
    texto_codificado = quote(texto, safe="")
    return f"https://api.whatsapp.com/send?phone={telefone}&text={texto_codificado}"

def marcar_como_enviado(lead_id: str) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params  = {"id": f"eq.{lead_id}"}
    payload = {"status": "enviado"}
    try:
        response = requests.patch(url, json=payload, headers=supabase_headers, params=params, timeout=10)
        return response.status_code in (200, 201, 204)
    except Exception as e:
        print(f"  WARN: Erro ao atualizar status: {e}")
        return False

def confirmar(pergunta: str) -> bool:
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in ("s", "sim"): return True
        if resposta in ("n", "nao", "não"): return False
        print(" -> Digite 's' para sim ou 'n' para nao.")

def executar_disparador():
    print("=" * 65)
    print("DISPARADOR WHATSAPP -- Modo manual com confirmacao")
    print("=" * 65)

    leads = buscar_leads_gerados()
    if not leads:
        print("INFO: Tudo em dia! Nenhum lead 'gerado' encontrado.")
        return

    total = len(leads)
    print(f"INFO: {total} lead(s) prontos para disparo.\n")

    enviados, pulados, sem_fone = 0, 0, 0

    for i, lead in enumerate(leads, start=1):
        nome, cidade, fone_raw = lead.get("nome_empresa"), lead.get("cidade"), lead.get("telefone")
        proposta, lead_id = lead.get("texto_proposta", ""), lead.get("id")

        print(f"--- Lead {i}/{total} " + "-"*20)
        print(f"  EMPRESA: {nome}")
        print(f"  CIDADE : {cidade}")
        print(f"  FONE   : {fone_raw or 'Nao informado'}")

        if not proposta:
            print("  WARN: Sem proposta. Pulando.")
            pulados += 1
            continue

        telefone = tratar_telefone(fone_raw)
        if not telefone:
            print("  WARN: Telefone invalido.")
            sem_fone += 1
            if not confirmar("  Continuar para o proximo? (s/n): "): break
            continue

        link = montar_link_whatsapp(telefone, proposta)
        print(f"  LINK: {link}")
        print(f"  MSN : {proposta[:80]}...")

        if confirmar("  Deseja abrir o WhatsApp agora? (s/n): "):
            webbrowser.open(link)
            time.sleep(1)
            if marcar_como_enviado(lead_id):
                print("  OK: Enviado!")
                enviados += 1
            else:
                print("  WARN: Aberto, mas falha no banco.")
        else:
            print("  SKIP: Pulado.")
            pulados += 1

        if i < total and not confirmar("  Proximo lead? (s/n): "): break

    print("\n" + "=" * 65)
    print("RELATORIO")
    print(f"  Enviados  : {enviados}")
    print(f"  Pulados   : {pulados}")
    print(f"  Sem Fone  : {sem_fone}")
    print("=" * 65)

if __name__ == "__main__":
    executar_disparador()
