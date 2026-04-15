"""
gerador_propostas.py
--------------------
Cérebro do robô de prospecção: lê leads com status 'novo' no Supabase,
gera uma mensagem personalizada de abordagem via Gemini (Google AI Studio)
e atualiza o registro com a proposta e o novo status 'gerado'.
"""

import os
import sys
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# ── Carrega variáveis de ambiente ────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_KEY   = os.getenv("GEMINI_API_KEY")

# ── Validação ────────────────────────────────────────────────────────────────
credenciais_faltando = [
    nome for nome, val in [
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY),
        ("GEMINI_API_KEY", GEMINI_KEY),
    ] if not val or val == "sua_chave_aqui"
]

if credenciais_faltando:
    print(f"❌ ERRO: Variáveis ausentes ou não preenchidas no config/.env:")
    for c in credenciais_faltando:
        print(f"   → {c}")
    sys.exit(1)

# Configuracao do Gemini - Usando o caminho completo do modelo 2.0
genai.configure(api_key=GEMINI_KEY)
modelo = genai.GenerativeModel("models/gemini-2.0-flash")

# ── Headers do Supabase ───────────────────────────────────────────────────────
TABELA = "leads_prospeccao"

supabase_headers = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

DELAY_ENTRE_LEADS = 2  # segundos — respeita o rate limit do Gemini (free tier)


# ── Funções auxiliares ────────────────────────────────────────────────────────

def buscar_leads_novos() -> list[dict]:
    """
    Busca no Supabase todos os leads com status = 'novo'.
    Retorna uma lista de dicionários com os dados do lead.
    """
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params = {
        "status": "eq.novo",
        "select": "id,nome_empresa,categoria,cidade,nota_google",
    }

    try:
        response = requests.get(url, headers=supabase_headers, params=params, timeout=10)
        response.raise_for_status()
        leads = response.json()
        print(f"📋 {len(leads)} lead(s) com status 'novo' encontrado(s).\n")
        return leads
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar leads no Supabase: {e}")
        sys.exit(1)


def montar_prompt(lead: dict) -> str:
    """
    Monta o prompt personalizado para o Gemini com base nos dados do lead.
    """
    nome     = lead.get("nome_empresa", "a empresa")
    categoria = lead.get("categoria", "estabelecimento")
    cidade   = lead.get("cidade", "sua cidade")
    nota     = lead.get("nota_google")

    nota_texto = f"nota {nota} no Google" if nota else "boa avaliação no Google"

    return (
        f"Aja como um consultor de tecnologia de Três Corações, Minas Gerais. "
        f"Escreva uma mensagem de abordagem para o WhatsApp do dono da {nome}, "
        f"que é uma {categoria} em {cidade}. "
        f"Foque no fato de que eles têm {nota_texto}, mas não têm site, "
        f"e estão perdendo clientes para a concorrência que já está no digital. "
        f"A mensagem deve ser curta (máximo 5 linhas), profissional e mineira "
        f"(educada mas direta ao ponto, sem rodeios). "
        f"Não use asteriscos nem emojis excessivos. Assine como 'Equipe Kyros Digital'."
    )


def gerar_proposta_com_gemini(prompt: str) -> str | None:
    """
    Envia o prompt ao Gemini e retorna o texto gerado.
    Retorna None em caso de falha.
    """
    try:
        resposta = modelo.generate_content(prompt)
        return resposta.text.strip()
    except Exception as e:
        print(f"  ⚠️  Erro ao chamar o Gemini: {e}")
        return None


def atualizar_lead_no_supabase(lead_id: str, texto_proposta: str) -> bool:
    """
    Atualiza o lead no Supabase com a proposta gerada e status 'gerado'.
    Retorna True se bem-sucedido.
    """
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}"
    params = {"id": f"eq.{lead_id}"}
    payload = {
        "texto_proposta": texto_proposta,
        "status":         "gerado",
    }

    try:
        response = requests.patch(
            url, json=payload, headers=supabase_headers, params=params, timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro ao atualizar lead {lead_id}: {e}")
        return False


# ── Loop principal ────────────────────────────────────────────────────────────

def executar_gerador():
    """
    Orquestra a leitura dos leads, geração das propostas e atualização no banco.
    """
    print("CADERNO DE PROPOSTAS -- Iniciando com Gemini AI...")
    print("="*60)

    print()

    leads = buscar_leads_novos()

    if not leads:

        return

    total_gerados  = 0
    total_erros    = 0

    for lead in leads:
        nome     = lead.get("nome_empresa", "Empresa desconhecida")
        lead_id  = lead.get("id")

    print("Processando: ", nome)


        # Gera o prompt e chama o Gemini
        prompt   = montar_prompt(lead)
        proposta = None
        
        while proposta is None:
            try:
                proposta = gerar_proposta_com_gemini(prompt)
                if not proposta:
                    print(f"  ❌ Falha generica ao gerar proposta para: {nome}")
                    total_erros += 1
                    break
            except Exception as e:
                # Se for erro de quota (429)
                print(f"Limites atingidos. Aguardando 15 segundos...")

                    time.sleep(15)
                    continue # Tenta gerar o mesmo lead de novo
                else:
                    print(f"  ❌ Erro ao processar: {e}")
                    total_erros += 1
                    break

        if proposta:
            # Persiste a proposta e atualiza o status
            sucesso = atualizar_lead_no_supabase(lead_id, proposta)

            if sucesso:
                print(f"  ✅ [PROPOSTA OK] Gerada para: {nome}")
                total_gerados += 1
            else:
                print(f"  ❌ Falha ao salvar proposta de: {nome}")
                total_erros += 1

        # Pausa fixa de 15 segundos entre chamadas para garantir paz total na quota do Gemini
        time.sleep(15)




    # ── Relatório final ───────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"  ✅ Propostas geradas com sucesso : {total_gerados}")
    print(f"  ❌ Erros                         : {total_erros}")
    print("=" * 60)
    print("✅ Processo concluído!")


if __name__ == "__main__":
    executar_gerador()
