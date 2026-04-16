# 🎓 Guia de Estudos: Kyros Leads para Iniciantes

Parabéns por estar arriscando! Programação é como aprender um novo idioma: no começo parece difícil, mas depois vira automático. Aqui está um resumo do que você tem em mãos:

## 1. O que é o quê neste projeto?
*   **Python (`.py`):** É a linguagem que você usou para criar a "cara" do programa (a janela com botões). É excelente para automação rápida.
*   **TypeScript/Node.js (`/automacao`):** É como se fosse o "motor" mais forte escondido no porão. Ele cuida dos dados pesados.
*   **JSON (`.json`):** São arquivos de texto que guardam dados de um jeito que o computador entende fácil. É como uma lista de compras organizada.

## 2. Conceitos que você vai ver no código (e o que significam):

### A. Variáveis (As caixas)
Pense em uma variável como uma caixa com uma etiqueta.
```python
nome_da_cidade = "São Paulo"
```
Aqui, criamos uma caixa chamada `nome_da_cidade` e guardamos o texto `"São Paulo"` dentro dela.

### B. Funções (As receitas)
Uma função é um conjunto de instruções que você dá para o computador fazer só quando você chamar.
```python
def salvar_dados():
    # ... comandos para salvar ...
```
É como uma receita de bolo: ela está escrita no livro, mas o bolo só começa a ser feito quando você decide "rodar" a receita.

### C. Listas (Os arrays)
```python
nichos = ["academia", "padaria", "otica"]
```
É uma sequência de itens guardados em uma única variável.

## 3. Como "brincar" sem medo:

### Dica 1: O "Comentário" é seu melhor amigo
Tudo que começa com `#` no Python o computador ignora. Use isso para escrever notas para você mesmo:
```python
# Esse botão faz os leads aparecerem na tela
self.btn_scanner = ctk.CTkButton(...) 
```

### Dica 2: Cuidado com a Identação (Os espaços)
No Python, os espaços no começo da linha importam MUITO. Se um comando está "dentro" de outro, ele precisa estar um pouco mais para a direita (4 espaços).

## 4. Como a IA (Gemini) trabalha aqui?
Você vai notar que o projeto usa o **Google Gemini**:
*   **Conexão:** Ele usa uma "Chave de API" (como uma senha) para falar com os servidores do Google.
*   **Metodologia:** O sistema envia os dados da empresa (nome, cidade, nota) e pede para a IA criar uma mensagem "mineira" e profissional.
*   **Trabalho:** A IA lê quem são os novos leads, inventa a melhor proposta de venda e salva no banco de dados para ser enviada depois.

## 5. Próxima missão para você:
Tente abrir o arquivo `kyros_app.py` e procure por `self.title`. Tente mudar o texto que está entre aspas e rode o programa para ver o título da janela mudar!

---
**Lembre-se:** Errar faz parte. Se o código der erro (o famoso "crash"), o computador vai te dar uma mensagem dizendo em qual linha o erro está. Leia com calma! 🚀
