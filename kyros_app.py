import os
import sys
import json
import subprocess
import threading
import requests
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "alvos.json")

NICHOS_PADRAO = [
    "academia", "advogado", "agencia de marketing", "arquitetura", "autoescola",
    "barbearia", "bistro", "cafeteria", "centro automotivo", "clinica de estetica",
    "clinica medica", "clinica odontologica", "clinica veterinaria", "construtora", "contabilidade",
    "consultorio de psicologia", "corretora de seguros", "coworking", "dedetizadora", "despachante",
    "escola de idiomas", "escola infantil", "escritorio de engenharia", "espaco de eventos", "estudio de pilates",
    "estudio de tatuagem", "farmacia", "floricultura", "funeraria", "grameira",
    "hamburgueria", "hotel", "imobiliaria", "laboratorio clinico", "lava rapido",
    "lavanderia", "loja de calcados", "loja de informatica", "loja de moveis", "loja de roupas",
    "loja de suplementos", "loja de tintas", "loja de veiculos", "marcenaria", "material de construcao",
    "moto pecas", "nutricionista", "oficina mecanica", "otica", "padaria",
    "pastelaria", "pet shop", "pizzaria", "posto de gasolina", "pousada",
    "provedor de internet", "restaurante", "restaurante japones", "salao de beleza", "sorveteria",
    "supermercado", "vidracaria"
]

class CheckboxScrollFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.checkboxes = []
        self.vars = {}

    def populate(self, list_items, pre_selected=[]):
        self.clear()
        for item in list_items:
            var = ctk.StringVar(value=item if item in pre_selected else "")
            cb = ctk.CTkCheckBox(self, text=item, variable=var, onvalue=item, offvalue="")
            cb.pack(anchor="w", pady=2, padx=5)
            self.checkboxes.append(cb)
            self.vars[item] = var

    def filter_items(self, term):
        term = term.lower()
        for cb in self.checkboxes:
            if term in cb.cget("text").lower():
                cb.pack(anchor="w", pady=2, padx=5)
            else:
                cb.pack_forget()

    def clear(self):
        for cb in self.checkboxes:
            cb.destroy()
        self.checkboxes.clear()
        self.vars.clear()

    def get_selected(self):
        return [var.get() for var in self.vars.values() if var.get() != ""]

    def select_all(self):
        for cb, var in zip(self.checkboxes, self.vars.values()):
            if cb.winfo_ismapped(): # Marca apenas as que estão visíveis na pesquisa
                cb.select()
                var.set(cb._onvalue)

    def deselect_all(self):
        for cb, var in zip(self.checkboxes, self.vars.values()):
            if cb.winfo_ismapped():
                cb.deselect()
                var.set(cb._offvalue)


class KyrosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kyros Leads — Central de Comando")
        self.geometry("1100x700")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- SIDEBAR ----------------
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="KYROS LEADS", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_aba_console = ctk.CTkButton(self.sidebar_frame, text="💻 Painel Principal", fg_color="transparent", command=self.show_console)
        self.btn_aba_console.grid(row=1, column=0, padx=20, pady=5)

        self.btn_aba_config = ctk.CTkButton(self.sidebar_frame, text="⚙️ Configurar Alvos", fg_color="transparent", command=self.show_config)
        self.btn_aba_config.grid(row=2, column=0, padx=20, pady=5)

        ctk.CTkLabel(self.sidebar_frame, text="──────────────", text_color="gray").grid(row=3, column=0, pady=5)

        self.btn_full = ctk.CTkButton(self.sidebar_frame, text="Fluxo Completo", command=lambda: self.start_script("auto_prospect.py"))
        self.btn_full.grid(row=4, column=0, padx=20, pady=10)

        self.btn_scanner = ctk.CTkButton(self.sidebar_frame, text="Buscar Leads", fg_color="transparent", border_width=1, command=lambda: self.start_script("scanner_leads.py"))
        self.btn_scanner.grid(row=5, column=0, padx=20, pady=10)

        self.btn_gemini = ctk.CTkButton(self.sidebar_frame, text="Gerar Propostas", fg_color="transparent", border_width=1, command=lambda: self.start_script("gerador_propostas.py"))
        self.btn_gemini.grid(row=6, column=0, padx=20, pady=10)

        self.btn_whatsapp = ctk.CTkButton(self.sidebar_frame, text="Disparar WhatsApp", fg_color="transparent", border_width=1, command=lambda: self.start_script("disparo_automatico.py"))
        self.btn_whatsapp.grid(row=7, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Sistema Online", text_color="green")
        self.status_label.grid(row=8, column=0, padx=20, pady=(60, 10))

        # ---------------- CONSOLE FRAME ----------------
        self.console_frame = ctk.CTkFrame(self, corner_radius=10)
        self.console_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.console_title = ctk.CTkLabel(self.console_frame, text="Monitor de Atividades", font=ctk.CTkFont(size=16, weight="bold"))
        self.console_title.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        self.textbox = ctk.CTkTextbox(self.console_frame, font=("Consolas", 12))
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # ---------------- CONFIG FRAME ----------------
        self.config_frame = ctk.CTkFrame(self, corner_radius=10)
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_columnconfigure(1, weight=1)
        self.config_frame.grid_rowconfigure(3, weight=1) # Expande as listas
        
        ctk.CTkLabel(self.config_frame, text="Mapeamento Estratégico em Massa", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # TOPO: Estado API
        top_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        top_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        
        self.estado_var = ctk.StringVar(value="Selecione o Estado IBGE")
        self.combo_estado = ctk.CTkOptionMenu(top_frame, variable=self.estado_var, command=self.carregar_cidades_thread)
        self.combo_estado.pack(side="left", padx=(0, 10))

        self.lbl_loading_cidades = ctk.CTkLabel(top_frame, text="", text_color="orange")
        self.lbl_loading_cidades.pack(side="left")

        # BARRA DE PESQUISA (Novidade)
        search_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        search_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(10,0))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=1)

        self.entry_pesquisa = ctk.CTkEntry(search_frame, placeholder_text="🔍 Escreva aqui para filtrar as cidades rapidamente...")
        self.entry_pesquisa.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_pesquisa.bind("<KeyRelease>", self.on_search_typing)

        ctk.CTkLabel(search_frame, text="🎯 Nichos do Scanner", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)

        # LISTAS DE ROLAGEM COM CHECKBOXES
        self.scroll_cidades = CheckboxScrollFrame(self.config_frame)
        self.scroll_cidades.grid(row=3, column=0, padx=10, pady=(5,10), sticky="nsew")

        self.scroll_nichos = CheckboxScrollFrame(self.config_frame)
        self.scroll_nichos.grid(row=3, column=1, padx=10, pady=(5,10), sticky="nsew")

        # BOTÕES DE SELEÇÃO EM MASSA
        btn_frame_cidad = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        btn_frame_cidad.grid(row=4, column=0, pady=5)
        ctk.CTkButton(btn_frame_cidad, text="Marcar Listados", width=100, command=self.scroll_cidades.select_all).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame_cidad, text="Desmarcar Listados", width=100, fg_color="#631414", hover_color="#8a1c1c", command=self.scroll_cidades.deselect_all).pack(side="left", padx=5)

        btn_frame_nicho = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        btn_frame_nicho.grid(row=4, column=1, pady=5)
        ctk.CTkButton(btn_frame_nicho, text="Marcar Tudo", width=100, command=self.scroll_nichos.select_all).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame_nicho, text="Desmarcar Tudo", width=100, fg_color="#631414", hover_color="#8a1c1c", command=self.scroll_nichos.deselect_all).pack(side="left", padx=5)

        # BOTÃO SALVAR
        self.btn_salvar_config = ctk.CTkButton(self.config_frame, text="✅ SALVAR TODOS OS ALVOS NO SISTEMA", font=ctk.CTkFont(weight="bold", size=14), fg_color="#0e6b26", hover_color="#148a32", height=40, command=self.salvar_alvos)
        self.btn_salvar_config.grid(row=5, column=0, columnspan=2, padx=20, pady=(15, 20), sticky="ew")

        # INIT
        self.process = None
        self.estados_api = []
        self.alvos_cidades_cadastradas = []
        self.load_alvos_salvos()
        threading.Thread(target=self.init_ibge, daemon=True).start()

    # --- NAVEGAÇÃO ---
    def show_console(self):
        self.config_frame.grid_forget()
        self.console_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.btn_aba_console.configure(fg_color=["gray75", "gray25"])
        self.btn_aba_config.configure(fg_color="transparent")

    def show_config(self):
        self.console_frame.grid_forget()
        self.config_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.btn_aba_config.configure(fg_color=["gray75", "gray25"])
        self.btn_aba_console.configure(fg_color="transparent")

    def on_search_typing(self, event):
        termo = self.entry_pesquisa.get()
        self.scroll_cidades.filter_items(termo)

    # --- JSON E LOAD INICIAL ---
    def load_alvos_salvos(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.alvos_cidades_cadastradas = data.get("cidades", [])
                self.alvos_nichos = data.get("categorias", [])
        except:
            self.alvos_cidades_cadastradas = []
            self.alvos_nichos = []
        
        nm = sorted(list(set(NICHOS_PADRAO + self.alvos_nichos)))
        self.scroll_nichos.populate(nm, pre_selected=self.alvos_nichos)
        
        if self.alvos_cidades_cadastradas:
            self.scroll_cidades.populate(self.alvos_cidades_cadastradas, pre_selected=self.alvos_cidades_cadastradas)
        else:
            self.scroll_cidades.populate(["Nenhuma cidade carregada."])

    def salvar_alvos(self):
        cids_na_tela = self.scroll_cidades.get_selected()
        nics = self.scroll_nichos.get_selected()
        
        # Merge: Mantemos as cadastradas que já existiam mas não estão visíveis na tela (caso de outro estado),
        # E adicionamos as novas. Mas para facilitar agora: O que tá selecionado daquele estado vai pro cache.
        final_cidades = list(set(self.alvos_cidades_cadastradas + cids_na_tela))
        
        # Mas e se ele desmarcou? É complexo manter merge. Vamos apenas atualizar o banco com o atual pra simplificar, ou fazer append.
        data = {
            "cidades": final_cidades[-100:], # limited pra n quebrar
            "categorias": nics
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        self.btn_salvar_config.configure(text="✅ ALVOS SALVOS COM SUCESSO!", fg_color="green")
        self.after(2000, lambda: self.btn_salvar_config.configure(text="✅ SALVAR TODOS OS ALVOS NO SISTEMA", fg_color="#0e6b26"))

    # --- API IBGE ---
    def init_ibge(self):
        try:
            self.combo_estado.configure(values=["Carregando..."])
            r = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome", timeout=10)
            self.estados_api = r.json()
            nomes_estados = [e["nome"] for e in self.estados_api]
            self.combo_estado.configure(values=nomes_estados)
            self.estado_var.set("Selecione o Estado IBGE")
        except:
            self.estado_var.set(f"Erro IBGE")

    def carregar_cidades_thread(self, estado_selecionado):
        self.lbl_loading_cidades.configure(text="⏳ Baixando dezenas de cidades, aguarde um segundo...")
        self.scroll_cidades.clear()
        self.update() # Força a tela a mostrar o Loading
        # Chama com after para permitir UI atualizar o loading text
        self.after(100, lambda: self.processar_cidades(estado_selecionado))

    def processar_cidades(self, estado_selecionado):
        uf_id = next((e["id"] for e in self.estados_api if e["nome"] == estado_selecionado), None)
        if uf_id:
            try:
                r = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios?orderBy=nome", timeout=10)
                cidades_ibge = [c["nome"] for c in r.json()]
                pre_selec = [c for c in self.alvos_cidades_cadastradas if c in cidades_ibge]
                self.scroll_cidades.populate(cidades_ibge, pre_selected=pre_selec)
            except Exception:
                pass
        self.lbl_loading_cidades.configure(text="")
        
    # --- EXECUÇÃO DE PYTHON ---
    def log(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

    def start_script(self, script_name):
        self.show_console()
        if self.process and self.process.poll() is None:
            self.log("Existe um processo em execucao. Aguarde.")
            return

        self.textbox.delete("1.0", "end")
        self.log(f"Iniciando: {script_name}...")
        self.status_label.configure(text="Executando...", text_color="orange")
        threading.Thread(target=self.run_process, args=(script_name,), daemon=True).start()

    def run_process(self, script_name):
        script_path = os.path.join("scripts", script_name)
        process = subprocess.Popen(
            [sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True, cwd=os.getcwd()
        )
        for line in process.stdout:
            self.log(line.strip())
        process.wait()
        
        if process.returncode == 0:
            self.log(f"\n{script_name} concluido com sucesso!")
            self.status_label.configure(text="Sistema Online", text_color="green")
        else:
            self.log(f"\n{script_name} parou com erro (Codigo {process.returncode})")
            self.status_label.configure(text="Erro Detectado", text_color="red")

if __name__ == "__main__":
    app = KyrosApp()
    app.mainloop()
