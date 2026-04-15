# 🚀 Kyros Leads Pipeline

A "Máquina de Vendas Autônoma": um sistema completo e automatizado para encontrar empresas locais, gerar propostas personalizadas com Inteligência Artificial e disparar mensagens de vendas via WhatsApp. 

Esse projeto foi criado para escalar agências e prestadores de serviços de tecnologia, focando em empresas locais sem presença digital (ex: sem website próprio).

---

## 🎯 Como Funciona o Funil (Pipeline)

O sistema possui 4 robôs autônomos que operam em sequência:

1. **🔍 Scanner (`scanner_leads.py`)** 
   Vasculha o Google Maps (via *Serper.dev*) em busca de empresas de dezenas de categorias locais. Se a empresa NÃO tem site e se encaixa no perfil, ela é salva no banco de dados como `novo`.
   
2. **🧹 Limpeza Automática**
   Dentro do orquestrador, um limpador exclui silenciosamente qualquer *"lead"* que não disponibilizou número de telefone ao público, evitando gastos desnecessários na requisição de APIs.

3. **🧠 Gerador de Propostas (`gerador_propostas.py`)**
   Nesta fase, a Inteligência Artificial (Google Gemini AI) avalia o contexto da empresa recém-descoberta e redige um "Pitch" de vendas customizado e irresistível, alterando o status do lead para `gerado`.

4. **📤 Disparo de WhatsApp (`disparo_automatico.py`)**
   Com as copys geradas, o robô consome a *Z-API* (API de WhatsApp Cloud) e envia cada mensagem diretamente para o celular ou WhatsApp Business do prospect. Ao enviar com sucesso, altera o status para `enviado`, blindando a operação contra duplicatas ou spam.

---

## 🖥️ A Central de Comando (GUI)

O projeto acompanha a **Kyros App** (`kyros_app.py`), um painel gráfico em *Dark Mode* que centraliza todo o controle da máquina dispensando o uso do terminal de comandos.

<div align="center">
  <blockquote>Execute tudo através da GUI: Scanner → IA → Zap.</blockquote>
</div>

---

## 🛠️ Tecnologias Utilizadas

*   **Python:** Linguagem *Core* do backend.
*   **CustomTkinter:** Renderização da interface visual (*GUI*).
*   **Supabase / PostgreSQL:** Armazenamento seguro de *leads* e orquestração de funil.
*   **Google Gemini (GenAI):** LLM responsável por escrever Copys Vendedoras.
*   **Serper.dev:** Ferramenta de integração e Extração do *Google Maps*.
*   **Z-API:** Plataforma *Cloud* autônoma de envios em massa via WhatsApp.

---

## ⚙️ Instalação e Execução

### 1. Requisitos
Você vai precisar de:
* Python `3.10+`
* Um servidor ativo configurado no Supabase
* Access tokens operantes nas contas: `Google AI`, `Serper` e `Z-API`.

### 2. Passo a Passo

Clone o Repositório:
```bash
git clone {sua_url_aqui}
cd prospeccao-vendas
```

Instale as Dependências:
```bash
pip install -r requirements.txt
pip install customtkinter
```

Configure as suas chaves (.env):
Na pasta `config`, duplique o exemplo ou acesse o `.env` oculto e preencha a sua *Supabase Key*, *Gemini Key*, e *Serper Key*. Mantenha este arquivo local.

Inicie a Central de Atendimento:
```bash
python kyros_app.py
```

---

## 🛡️ Segurança (Anti-Leak)

Este repositório foi construído usando boas práticas de arquitetura e utiliza regras estritas no `.gitignore` para vazar 0 (zero) dados sensíveis. O sistema não envia tokens localizados e a Z-API consome cabeçalhos dinâmicos com o protocolo de `Client-Token`.

---
*Desenvolvido por Kyros Digital Ecosystem*
