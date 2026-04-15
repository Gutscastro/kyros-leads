import os
import sys
import json
import subprocess
import threading
import requests
import customtkinter as ctk

# Configurações de Design
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "alvos.json")

class KyrosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kyros Leads — Central de Comando")
        self.geometry("1000x650")

        # Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Menu Lateral)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="KYROS LEADS", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botões de Abas
        self.btn_aba_console = ctk.CTkButton(self.sidebar_frame, text="💻 Painel Principal", fg_color="transparent", command=self.show_console)
        self.btn_aba_console.grid(row=1, column=0, padx=20, pady=5)

        self.btn_aba_config = ctk.CTkButton(self.sidebar_frame, text="⚙️ Configurar Alvos", fg_color="transparent", command=self.show_config)
        self.btn_aba_config.grid(row=2, column=0, padx=20, pady=5)

        ctk.CTkLabel(self.sidebar_frame, text="──────────────", text_color="gray").grid(row=3, column=0, pady=5)

        # Botões de Ação
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

        # ---------------- CONSOLE FRAME (Aba 1) ----------------
        self.console_frame = ctk.CTkFrame(self, corner_radius=10)
        self.console_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.console_title = ctk.CTkLabel(self.console_frame, text="Monitor de Atividades", font=ctk.CTkFont(size=16, weight="bold"))
        self.console_title.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        self.textbox = ctk.CTkTextbox(self.console_frame, font=("Consolas", 12))
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # ---------------- CONFIG FRAME (Aba 2 - IBGE) ----------------
        self.config_frame = ctk.CTkFrame(self, corner_radius=10)
        # Nao exibe no inicio...
        self.config_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(self.config_frame, text="Mapeamento Estratégico (IBGE API)", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 20))

        # --- Linha Cidades ---
        self.estado_var = ctk.StringVar(value="Selecione o Estado")
        self.cidade_var = ctk.StringVar(value="Aguardando...")

        self.combo_estado = ctk.CTkOptionMenu(self.config_frame, variable=self.estado_var, command=self.carregar_cidades)
        self.combo_estado.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.combo_cidade = ctk.CTkOptionMenu(self.config_frame, variable=self.cidade_var)
        self.combo_cidade.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        self.btn_add_cidade = ctk.CTkButton(self.config_frame, text="+ Adicionar Cidade à Rota", command=self.add_cidade)
        self.btn_add_cidade.grid(row=2, column=0, columnspan=2, pady=10)

        # --- Linha Nichos ---
        self.entry_nicho = ctk.CTkEntry(self.config_frame, placeholder_text="Digite um novo Nicho (Ex: Construtora)")
        self.entry_nicho.grid(row=3, column=0, columnspan=2, padx=20, pady=(30,10), sticky="ew")

        self.btn_add_nicho = ctk.CTkButton(self.config_frame, text="+ Adicionar Nicho", command=self.add_nicho)
        self.btn_add_nicho.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Mostrador Atual ---
        self.lbl_atuais = ctk.CTkLabel(self.config_frame, text="Alvos Atuais:", font=ctk.CTkFont(weight="bold"))
        self.lbl_atuais.grid(row=5, column=0, columnspan=2, pady=(20,5))
        
        self.txt_atuais = ctk.CTkTextbox(self.config_frame, height=150)
        self.txt_atuais.grid(row=6, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        # Iniciar processo em Thread para nao travar a UI
        self.process = None
        
        # Load inicial da API IBGE e Arquivo
        self.estados_api = []
        threading.Thread(target=self.init_ibge, daemon=True).start()
        self.atualizar_visor_json()

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

    # --- INTEGRAÇÃO IBGE ---
    def init_ibge(self):
        try:
            self.combo_estado.configure(values=["Carregando Estados..."])
            r = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome", timeout=10)
            self.estados_api = r.json()
            nomes_estados = [e["nome"] for e in self.estados_api]
            self.combo_estado.configure(values=nomes_estados)
            self.estado_var.set("Selecione o Estado")
        except Exception as e:
            self.estado_var.set(f"Erro IBGE")

    def carregar_cidades(self, estado_selecionado):
        self.cidade_var.set("Carregando...")
        self.combo_cidade.configure(values=["Buscando..."])
        
        def fetch():
            uf_id = next((e["id"] for e in self.estados_api if e["nome"] == estado_selecionado), None)
            if uf_id:
                try:
                    r = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios?orderBy=nome", timeout=10)
                    cidades = [c["nome"] for c in r.json()]
                    self.combo_cidade.configure(values=cidades)
                    if cidades:
                        self.cidade_var.set(cidades[0])
                except:
                    self.cidade_var.set("Erro API")
        threading.Thread(target=fetch, daemon=True).start()

    # --- GERENCIAMENTO JSON ---
    def load_json(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"cidades": [], "categorias": []}

    def save_json(self, data):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.atualizar_visor_json()

    def add_cidade(self):
        cid = self.cidade_var.get()
        if cid and cid not in ["Aguardando...", "Carregando...", "Erro API"]:
            data = self.load_json()
            if cid not in data["cidades"]:
                data["cidades"].append(cid)
                self.save_json(data)

    def add_nicho(self):
        nic = self.entry_nicho.get().strip().lower()
        if nic:
            data = self.load_json()
            if nic not in data["categorias"]:
                data["categorias"].append(nic)
                self.save_json(data)
                self.entry_nicho.delete(0, 'end')

    def atualizar_visor_json(self):
        self.txt_atuais.delete("1.0", "end")
        data = self.load_json()
        texto = f"[ CIDADES MAPEADAS ]\n{', '.join(data.get('cidades', []))}\n\n"
        texto += f"[ NICHOS VIGIADOS ]\n{', '.join(data.get('categorias', []))}"
        self.txt_atuais.insert("end", texto)

    # --- EXECUÇÃO SYSTEM ---
    def log(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

    def start_script(self, script_name):
        self.show_console() # Abre pro console rodar
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
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd()
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
