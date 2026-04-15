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
# Aponta para config/.env a partir da raiz do projeto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

# .strip() remove espaços e quebras de linha invisíveis que corrompem o header Authorization
SUPABASE_URL  = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY  = (os.getenv("SUPABASE_KEY") or "").strip()
SERPER_KEY    = (os.getenv("SERPER_API_KEY") or "").strip()

# ── Validação das credenciais ────────────────────────────────────────────────
if not all([SUPABASE_URL, SUPABASE_KEY, SERPER_KEY]):
    print("❌ ERRO: Variáveis de ambiente ausentes. Verifique config/.env")
    sys.exit(1)

# ── Configurações da campanha ────────────────────────────────────────────────
CIDADES = ["Três Corações", "Varginha"]

CATEGORIAS = [
    "pet shop",
    "academia",
    "pizzaria",
    "hamburgueria",
    "loja de roupa feminina",
    "imobiliaria",
    "escola de idiomas",
    "autoescola",
    "clinica de estetica",
    "estudio de tatuagem",
    "psicologo",
    "escritorio de contabilidade",
    "loja de moveis",
    "material de construcao",
    "floricultura",
    "otica",
    "venda de carros",
    "barbearia",
    "loja de suplementos",
    "advogado",
    "oficina mecanica",
    "salao de beleza",
    "clinica odontologica",
    "farmacia"
]

SERPER_ENDPOINT  = "https://google.serper.dev/places"
SUPABASE_TABLE   = "leads_prospeccao"
DELAY_ENTRE_BUSCAS = 1.5  # segundos — evita rate limiting

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
    """
    Realiza a busca de lugares no Google via Serper.dev.
    Retorna uma lista de resultados brutos da API.
    """
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
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠️  Erro HTTP na busca '{query} em {cidade}': {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro de conexão na busca '{query} em {cidade}': {e}")
        return []


def extrair_lead(lugar: dict, categoria: str, cidade: str) -> dict | None:
    """
    Extrai e valida os dados de um lugar retornado pela Serper.
    Retorna None se o lugar possuir website (não é um lead válido).
    """
    # Filtro principal: rejeitar empresas que já têm site
    if lugar.get("website"):
        return None

    nome    = lugar.get("title", "").strip()
    telefone = lugar.get("phoneNumber", "").strip()
    nota    = lugar.get("rating")

    # Nome é obrigatório
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
    """
    Persiste o lead na tabela leads_prospeccao do Supabase.
    Retorna True se salvo com sucesso, False em caso de duplicata ou erro.
    """
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"

    try:
        response = requests.post(url, json=lead, headers=supabase_headers, timeout=10)

        # 201 = criado com sucesso
        if response.status_code == 201:
            return True

        # 409 = conflito (duplicata pela constraint UNIQUE) — esperado, silencioso
        if response.status_code == 409:
            return False

        # 401 / 403 = problema de autenticação ou RLS bloqueando
        if response.status_code in (401, 403):
            try:
                corpo = response.json()
                codigo = corpo.get("code", "?")
                mensagem = corpo.get("message", response.text)
            except Exception:
                codigo, mensagem = "?", response.text
            print(f"  🔒 Erro de permissão [{response.status_code}] código={codigo}: {mensagem}")
            print(f"     → Verifique as políticas RLS no Supabase ou a SUPABASE_KEY no .env")
            return False

        # Qualquer outro erro inesperado — loga corpo completo para debug
        print(f"  ⚠️  Supabase retornou {response.status_code}: {response.text[:200]}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro ao salvar lead '{lead.get('nome_empresa')}': {e}")
        return False


# ── Loop principal ───────────────────────────────────────────────────────────

def executar_varredura():
    """
    Itera sobre todas as combinações de cidade x categoria,
    filtra os resultados e persiste os leads válidos no Supabase.
    """
    total_encontrados  = 0
    total_salvos       = 0
    total_duplicatas   = 0
    total_com_site     = 0

    print("=" * 60)
    print("🤖 ROBÔ CAÇADOR DE LEADS — Iniciando varredura...")
    print("=" * 60)

    for cidade in CIDADES:
        print(f"\n📍 Cidade: {cidade}")
        print("-" * 40)

        for categoria in CATEGORIAS:
            print(f"  🔍 Buscando: {categoria}...", end=" ", flush=True)

            lugares = buscar_no_serper(categoria, cidade)
            encontrados_nesta_busca = len(lugares)
            total_encontrados += encontrados_nesta_busca

            salvos_nesta_busca = 0

            for lugar in lugares:
                lead = extrair_lead(lugar, categoria, cidade)

                if lead is None:
                    total_com_site += 1
                    continue

                sucesso = salvar_lead(lead)

                if sucesso:
                    total_salvos += 1
                    salvos_nesta_busca += 1
                else:
                    total_duplicatas += 1

            print(f"{encontrados_nesta_busca} resultados → {salvos_nesta_busca} novos leads salvos")
            print(f"{encontrados_nesta_busca} resultados -> {salvos_nesta_busca} novos leads salvos")

            # Pausa para nao sobrecarregar a API
            time.sleep(DELAY_ENTRE_BUSCAS)

    # -- Relatorio final ------------------------------------------------------
    print("\n" + "=" * 60)
    print("SCANNER CONCLUIDO")
    print("=" * 60)
    print(f"  Total de resultados encontrados : {total_encontrados}")
    print(f"  Filtrados (possuem website)     : {total_com_site}")
    print(f"  Leads novos salvos no Supabase  : {total_salvos}")
    print(f"  Duplicatas ignoradas            : {total_duplicatas}")
    print("=" * 60)
    print("Varredura concluida!")


if __name__ == "__main__":
    executar_varredura()
