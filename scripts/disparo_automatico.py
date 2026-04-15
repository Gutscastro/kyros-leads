"""
disparo_automatico.py 
----------------------
O "Braço Robótico" 100% Cloud do projeto Kyros Leads.
Este script envia as propostas do Supabase diretamente para o WhatsApp
através da Z-API, sem precisar rodar um servidor pesado no computador.
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
# URL oficial de envio de texto da Z-API
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"

# ── CONFIGURACOES DE FLUXO ───────────────────────────────────────────────────
TABELA = "leads_prospeccao"
# Pausa recomendada para nao ter o numero bloqueado pelo WhatsApp
# 40 segundos imitam o ritmo de um humano digitando propostas
DELAY_ENTRE_DISPAROS = 40 # Segundos


supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

# ── Funções Auxiliares ───────────────────────────────────────────────────────

def buscar_leads_prontos() -> list[dict]:
    """Busca no Supabase leads com status 'gerado' e que tenham telefone."""
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params = {
        "status": "eq.gerado",
        "select": "id,nome_empresa,telefone,texto_proposta",
        "order":  "criado_em.asc",
    }
    try:
        print("Consultando banco de dados...")
        response = requests.get(url, headers=supabase_headers, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar leads: {e}")
        return []


def tratar_telefone(telefone: str | None) -> str | None:
    """Normaliza o telefone para o formato 55DDDXXXX (padrao Z-API)."""
    if not telefone: return None
    apenas_digitos = re.sub(r"\D", "", telefone)
    if not apenas_digitos: return None
    if apenas_digitos.startswith("55") and len(apenas_digitos) >= 12:
        return apenas_digitos
    return f"55{apenas_digitos}"

def enviar_via_zapi(numero: str, mensagem: str) -> bool:
    """Envia a mensagem chamando a Cloud da Z-API."""
    payload = {
        "phone": numero,
        "message": mensagem,
    }
    
    headers = {
        "Client-Token": "Fd7b6012fae6f4372a20760d7ebb747f6S",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(ZAPI_URL, json=payload, headers=headers, timeout=20)
        # Z-API geralmente retorna 200, 201 ou 204 em caso de sucesso
        if response.status_code in (200, 201, 204):
            return True
        print(f"   Erro Z-API retornou {response.status_code}: {response.text}")
        return False
    except Exception as e:
        print(f"   Erro de rede com a Z-API: {e}")
        return False

def marcar_enviado(lead_id: str) -> bool:
    """Atualiza o status do lead no Supabase para 'enviado'."""
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params  = {"id": f"eq.{lead_id}"}
    payload = {"status": "enviado"}
    try:
        response = requests.patch(url, json=payload, headers=supabase_headers, params=params, timeout=10)
        return response.status_code in (200, 201, 204)
    except Exception: return False

# ── Loop Principal ───────────────────────────────────────────────────────────

def disparar_tudo():
    print("\n" + "="*65)
    print("DISPARO AUTOMATICO (Z-API) -- KYROS LEADS")
    print("="*65)


    leads = buscar_leads_prontos()
    if not leads:
        print("Tudo em dia! Nenhum lead com status 'gerado' encontrado.")
        return

    print("Iniciando a sequencia de disparos agora...")



    enviados = 0
    falhas   = 0

    for i, lead in enumerate(leads, start=1):
        nome    = lead["nome_empresa"]
        numero  = tratar_telefone(lead["telefone"])
        texto   = lead["texto_proposta"]
        lead_id = lead["id"]

        if not numero or not texto:
            print(f"[{i}/{len(leads)}] Pulou {nome}: Dados incompletos.")
            continue

        print(f"[{i}/{len(leads)}] Enviando para {nome} ({numero})...", end=" ", flush=True)


        sucesso = enviar_via_zapi(numero, texto)

        if sucesso:
            marcar_enviado(lead_id)
            print("OK")
            enviados += 1
            # Intervalo de seguranca para o WhatsApp
            if i < len(leads):
                print(f"Aguardando {DELAY_ENTRE_DISPAROS} segundos para o proximo...")
                time.sleep(DELAY_ENTRE_DISPAROS)
        else:
            print("ERRO")
            falhas += 1
            time.sleep(2)


    print("\n" + "="*65)
    print("RELATORIO FINAL DE DISPARO")
    print(f"   Mensagens enviadas : {enviados}")
    print(f"   Falhas no envio    : {falhas}")

    print("=" * 65)
    print("Sequencia de prospecção concluida!")

if __name__ == "__main__":
    disparar_tudo()
