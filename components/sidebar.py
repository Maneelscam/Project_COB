import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master, width=220, corner_radius=0)
        self.command = command

        self.logo_label = ctk.CTkLabel(
            self, text="INET", font=ctk.CTkFont("Segoe UI", 26, "bold"), text_color="#00A8E8"
        )
        self.logo_label.pack(pady=(30, 10))

        ctk.CTkLabel(
            self,
            text="Gerenciador de Contatos\nV9 (testes)",
            font=ctk.CTkFont("Segoe UI", 13),
            text_color="#B0B0B0",
        ).pack(pady=(0, 30))

        # Botões do menu
        self.btn_dashboard = ctk.CTkButton(
            self, text="📊 Dashboard", fg_color="#0A84FF", hover_color="#006DD6",
            command=lambda: self.command("dashboard") if self.command else None
        )
        self.btn_dashboard.pack(pady=10, fill="x", padx=20)

        self.btn_contatos = ctk.CTkButton(
            self, text="👥 Contatos", fg_color="#1E1E1E", hover_color="#333333",
            command=lambda: self.command("contatos") if self.command else None
        )
        self.btn_contatos.pack(pady=10, fill="x", padx=20)

        self.btn_config = ctk.CTkButton(
            self, text="⚙️ Configurações", fg_color="#1E1E1E", hover_color="#333333",
            command=lambda: self.command("config") if self.command else None
        )
        self.btn_config.pack(pady=10, fill="x", padx=20)
