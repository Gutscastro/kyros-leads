import os
import sys
import subprocess
import threading
import customtkinter as ctk

# Configurações de Design
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class KyrosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kyros Leads — Central de Comando")
        self.geometry("900x600")

        # Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Menu Lateral)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="KYROS LEADS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_full = ctk.CTkButton(self.sidebar_frame, text="Fluxo Completo", command=lambda: self.start_script("auto_prospect.py"))
        self.btn_full.grid(row=1, column=0, padx=20, pady=10)

        self.btn_scanner = ctk.CTkButton(self.sidebar_frame, text="Buscar Leads", fg_color="transparent", border_width=1, command=lambda: self.start_script("scanner_leads.py"))
        self.btn_scanner.grid(row=2, column=0, padx=20, pady=10)

        self.btn_gemini = ctk.CTkButton(self.sidebar_frame, text="Gerar Propostas", fg_color="transparent", border_width=1, command=lambda: self.start_script("gerador_propostas.py"))
        self.btn_gemini.grid(row=3, column=0, padx=20, pady=10)

        self.btn_whatsapp = ctk.CTkButton(self.sidebar_frame, text="Disparar WhatsApp", fg_color="transparent", border_width=1, command=lambda: self.start_script("disparo_automatico.py"))

        self.btn_whatsapp.grid(row=4, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Sistema Online", text_color="green")
        self.status_label.grid(row=5, column=0, padx=20, pady=(100, 10))

        # Main Area (Console de Saída)
        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.console_title = ctk.CTkLabel(self.main_container, text="Monitor de Atividades", font=ctk.CTkFont(size=14, weight="bold"))
        self.console_title.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        self.textbox = ctk.CTkTextbox(self.main_container, font=("Consolas", 12))
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Iniciar processo em Thread para nao travar a UI
        self.process = None

    def log(self, text):
        """Adiciona texto ao console visual."""
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

    def start_script(self, script_name):
        if self.process and self.process.poll() is None:
            self.log("⚠️ Já existe um processo em execução. Aguarde.")
            return

        self.textbox.delete("1.0", "end")
        self.log(f"Iniciando: {script_name}...")

        self.status_label.configure(text="Executando...", text_color="orange")
        
        # Roda o script em uma thread separada
        threading.Thread(target=self.run_process, args=(script_name,), daemon=True).start()

    def run_process(self, script_name):
        script_path = os.path.join("scripts", script_name)
        
        # Executa o processo e captura a saida em tempo real
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
            self.log(f"\n✅ {script_name} concluído com sucesso!")
            self.status_label.configure(text="Sistema Online", text_color="green")
        else:
            self.log(f"\n❌ {script_name} parou com erro (Código {process.returncode})")
            self.status_label.configure(text="Erro Detectado", text_color="red")

if __name__ == "__main__":
    app = KyrosApp()
    app.mainloop()
