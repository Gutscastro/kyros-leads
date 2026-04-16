# 🗺️ Guia Mestre: Entendendo o Universo Kyros Leads

Este guia foi feito para você, que está começando, entender cada canto deste projeto. O Kyros Leads não é apenas um arquivo, é um **ecossistema** com várias partes que conversam entre si.

---

## 🏗️ As 3 Grandes Partes (Arquitetura)

O seu projeto é dividido em três "mundos":

1.  **O Mundo Desktop (`kyros_app.py`):** É a janela que você abre no Windows. Ela serve como um controle remoto para disparar todas as outras funções.
2.  **O Mundo da Automação (`/automacao`):** É o coração técnico. Ele usa tecnologias modernas (Node.js e TypeScript) para gerenciar o banco de dados e garantir que as informações sejam salvas com segurança.
3.  **O Mundo Web (`/admin`):** É uma interface que você abre no navegador. Ela serve para você visualizar os resultados de forma bonita e profissional, usando as mesmas tecnologias que grandes sites usam (React/Vite).

---

## 📂 Explorando as Pastas

### 1. `/scripts` (As Mãos que Trabalham)
Aqui ficam os "operários". Cada arquivo faz um trabalho específico:
*   `scanner_leads.py`: O "detetive". Ele varre a internet em busca de empresas (leads) que se encaixam no que você quer.
*   `gerador_propostas.py`: O "escritor". Ele usa Inteligência Artificial para criar textos de vendas personalizados para cada empresa encontrada.
*   `disparo_automatico.py`: O "mensageiro". Ele pega as propostas e envia automaticamente pelo WhatsApp.
*   `auto_prospect.py`: O "gerente". Se você rodar este, ele faz todo o fluxo acima sozinho, um atrás do outro.

### 2. `/automacao` (O Motor e o Cérebro)
*   `src/cache`: Guarda informações temporárias para o sistema ser mais rápido.
*   `prisma/`: É o mapa do seu Banco de Dados. Diz para o computador como as tabelas de clientes devem ser organizadas.

### 3. `/admin` (O Painel de Visualização)
*   Se você quiser ver seus gráficos e listas de leads em uma página da web, é este código que faz isso acontecer.

### 4. `/config` (As Regras)
*   Aqui ficam arquivos como `alvos.json`. É aqui que o sistema lê quais cidades e nichos (ex: "odontologia") ele deve procurar.

---

## ⚙️ Como as peças se encaixam? (Fluxo de Trabalho)

1.  Você abre o `kyros_app.py`.
2.  Você escolhe as **Cidades** e os **Nichos** (isso salva no `/config`).
3.  Você clica em "Buscar Leads". O aplicativo chama o script da pasta `/scripts`.
4.  O script busca os dados e pede para o "Motor" da pasta `/automacao` salvar tudo no banco de dados.
5.  Depois, a IA gera as propostas e o robô envia pelo WhatsApp.
6.  No final, você abre o site na pasta `/admin` para ver o relatório de sucesso.

---

## 🧠 O Cérebro: Como a Inteligência Artificial Trabalha

A IA não é mágica, ela é um processo lógico que segue uma estratégia de vendas. Veja como ela funciona dentro do Kyros:

### 1. Conexão Direta
O sistema utiliza o **Google Gemini AI (versão 2.0 Flash)**. A conexão é feita via API através da biblioteca oficial do Google, usando a chave secreta que você configurou no seu `.env`. 

### 2. Metodologia de Escrita (Prompt Engineering)
Em vez de enviar apenas um "Olá, quer um site?", a IA recebe instruções complexas baseadas nos dados do lead:
*   **Dados Reais:** Ela lê o nome da empresa, a categoria e a nota que eles têm no Google Maps.
*   **Personalização Regional:** O robô é instruído a falar como um consultor de tecnologia local, usando um tom profissional e "mineiro" (educado porém direto).
*   **Estratégia de Dor e Prazer:** A metodologia foca no fato de que a empresa já é boa (tem nota alta), mas está "invisível" ou perdendo espaço por não ter um site oficial.

### 3. O Ciclo de Trabalho
O script `gerador_propostas.py` segue estes passos:
1.  **Busca:** Pergunta ao Supabase: "Quem são os novos leads que ainda não têm proposta?".
2.  **Criação:** Monta um pedido (prompt) único para cada empresa.
3.  **Processamento:** Envia para o Google Gemini e recebe de volta um texto de WhatsApp pronto para envio.
4.  **Resiliência:** O sistema espera cerca de 15 segundos entre um lead e outro para respeitar os limites de uso gratuito do Google e evitar travamentos.
5.  **Entrega:** Salva o texto no banco de dados e marca o lead como `gerado`.

---

## 💡 Dicas para o seu Aprendizado

*   **Quer mudar a lógica de busca?** Olhe a pasta `/scripts`.
*   **Quer mudar a aparência da janela principal?** Abra o `kyros_app.py`.
*   **Quer mudar as tabelas do banco de dados?** Vá na pasta `/automacao`.
*   **Quer mudar o site?** Vá na pasta `/admin`.

---

### 🛡️ Regra de Ouro: O Arquivo `.env`
Você verá vários arquivos chamados `.env`. Eles guardam suas senhas e chaves secretas (como a chave do Gemini ou do banco de dados). **Nunca apague esses arquivos e nunca mostre o conteúdo deles para ninguém!**

---
Este é o seu mapa. Explore com curiosidade, mude pequenos textos e veja o que acontece. A melhor forma de aprender é tentando! 🚀
