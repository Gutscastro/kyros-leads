"""
disparador_whatsapp.py
----------------------
Disparador semi-automático de propostas via WhatsApp.
Busca leads com status 'gerado' no Supabase, monta o link do WhatsApp Web
e abre no navegador sob confirmação do usuário — mantendo controle total
sobre o que é enviado e quando.
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
    print("❌ ERRO: SUPABASE_URL ou SUPABASE_KEY ausentes no config/.env")
    sys.exit(1)

# ── Configurações ─────────────────────────────────────────────────────────────
TABELA = "leads_prospeccao"

supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}


# ── Funções auxiliares ────────────────────────────────────────────────────────

def buscar_leads_gerados() -> list[dict]:
    """
    Busca no Supabase todos os leads com status = 'gerado'.
    Retorna lista de dicts com id, nome_empresa, telefone e texto_proposta.
    """
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params = {
        "status": "eq.gerado",
        "select": "id,nome_empresa,telefone,texto_proposta,cidade",
        "order":  "criado_em.asc",
    }

    try:
        response = requests.get(url, headers=supabase_headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar leads no Supabase: {e}")
        sys.exit(1)


def tratar_telefone(telefone: str | None) -> str | None:
    """
    Normaliza o número de telefone para o formato internacional brasileiro.
    Remove espaços, parênteses, hífens e traços.
    Garante o prefixo +55 (Brasil) se não estiver presente.

    Exemplos:
      '(35) 99999-1234'  → '5535999991234'
      '35999991234'      → '5535999991234'
      '5535999991234'    → '5535999991234'
      None               → None
    """
    if not telefone:
        return None

    # Remove tudo que não for dígito
    apenas_digitos = re.sub(r"\D", "", telefone)

    if not apenas_digitos:
        return None

    # Já tem o código do país (55) → mantém
    if apenas_digitos.startswith("55") and len(apenas_digitos) >= 12:
        return apenas_digitos

    # Adiciona o código do Brasil
    return f"55{apenas_digitos}"


def montar_link_whatsapp(telefone: str, texto: str) -> str:
    """
    Monta o link da API do WhatsApp com número e texto codificado (URL-safe).
    Usa api.whatsapp.com para funcionar em qualquer navegador (Web ou app).
    """
    texto_codificado = quote(texto, safe="")
    return f"https://api.whatsapp.com/send?phone={telefone}&text={texto_codificado}"


def marcar_como_enviado(lead_id: str) -> bool:
    """
    Atualiza o status do lead para 'enviado' no Supabase.
    Retorna True se bem-sucedido.
    """
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params  = {"id": f"eq.{lead_id}"}
    payload = {"status": "enviado"}

    try:
        response = requests.patch(
            url, json=payload, headers=supabase_headers, params=params, timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro ao atualizar status: {e}")
        return False


def confirmar(pergunta: str) -> bool:
    """
    Exibe uma pergunta e aguarda resposta 's' ou 'n' do usuário.
    Retorna True para 's', False para 'n'.
    """
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "não", "nao"):
            return False
        print("  ↳ Digite 's' para sim ou 'n' para não.")


# ── Loop principal ────────────────────────────────────────────────────────────

def executar_disparador():
    """
    Itera sobre os leads 'gerado', exibe o link do WhatsApp,
    abre no navegador sob confirmação e atualiza o status para 'enviado'.
    """
    print("=" * 65)
    print("📲 DISPARADOR WHATSAPP — Modo manual com confirmação")
    print("=" * 65)
    print()

    leads = buscar_leads_gerados()

    if not leads:
        print("✅ Nenhum lead com status 'gerado' para disparar. Tudo em dia!")
        return

    total = len(leads)
    print(f"📋 {total} lead(s) prontos para disparo.\n")

    enviados  = 0
    pulados   = 0
    sem_fone  = 0

    for i, lead in enumerate(leads, start=1):
        nome     = lead.get("nome_empresa", "Empresa desconhecida")
        cidade   = lead.get("cidade", "")
        telefone_raw = lead.get("telefone")
        proposta = lead.get("texto_proposta", "")
        lead_id  = lead.get("id")

        print(f"─── Lead {i}/{total} {'─' * 40}")
        print(f"  🏢 Empresa : {nome}")
        print(f"  📍 Cidade  : {cidade}")
        print(f"  📞 Fone    : {telefone_raw or '❌ Não informado'}")
        print()

        # Valida se há proposta gerada
        if not proposta:
            print("  ⚠️  Sem proposta gerada. Pulando este lead.\n")
            pulados += 1
            continue

        # Trata o número de telefone
        telefone = tratar_telefone(telefone_raw)

        if not telefone:
            print("  ⚠️  Número de telefone inválido ou ausente.")
            print("  💬 Proposta gerada (para copiar manualmente):")
            print(f"\n{proposta}\n")
            sem_fone += 1

            # Permite pular ou encerrar sem telefone
            if not confirmar("  Continuar para o próximo lead? (s/n): "):
                print("\n🛑 Disparador encerrado pelo usuário.")
                break
            print()
            continue

        # Monta e exibe o link
        link = montar_link_whatsapp(telefone, proposta)
        print(f"  🔗 Link WhatsApp:")
        print(f"  {link}")
        print()
        print(f"  💬 Prévia da proposta:")
        print(f"  {proposta[:180]}{'...' if len(proposta) > 180 else ''}")
        print()

        # Confirma antes de abrir
        abrir = confirmar("  Deseja abrir o próximo lead no WhatsApp? (s/n): ")

        if abrir:
            print("  🌐 Abrindo no navegador...", end=" ", flush=True)
            webbrowser.open(link)
            time.sleep(1)  # pequena pausa para o browser carregar

            # Atualiza status no Supabase
            if marcar_como_enviado(lead_id):
                print("✅ Status atualizado para 'enviado'.")
                enviados += 1
            else:
                print("⚠️  Link aberto, mas falha ao atualizar o status.")
        else:
            print("  ⏭️  Lead pulado.\n")
            pulados += 1
            continue

        print()

        # Pergunta se continua para o próximo (se não for o último)
        if i < total:
            if not confirmar("  Continuar para o próximo lead? (s/n): "):
                print("\n🛑 Disparador encerrado pelo usuário.")
                break
        print()

    # ── Relatório final ───────────────────────────────────────────────────────
    print("=" * 65)
    print("📊 RELATÓRIO DO DISPARO")
    print("=" * 65)
    print(f"  📲 Links abertos / enviados  : {enviados}")
    print(f"  ⏭️  Leads pulados             : {pulados}")
    print(f"  📵 Sem telefone              : {sem_fone}")
    print("=" * 65)
    print("✅ Sessão de disparo encluída!")


if __name__ == "__main__":
    executar_disparador()
