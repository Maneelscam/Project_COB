import customtkinter as ctk

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=15)
        ctk.CTkLabel(
            self, text="Painel Principal", font=ctk.CTkFont("Segoe UI", 22, "bold"), anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 10))

        # Cards básicos
        container = ctk.CTkFrame(self, corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        for nome, cor in [("Pendentes", "#0A84FF"), ("Enviados", "#00A86B"), ("Falhas", "#D63C3C")]:
            card = ctk.CTkFrame(container, corner_radius=10, fg_color="#1E1E1E")
            card.pack(side="left", expand=True, fill="both", padx=10, pady=10)
            ctk.CTkLabel(card, text=nome, font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=cor).pack(pady=10)
            ctk.CTkLabel(card, text="0 registros", text_color="#B0B0B0").pack()
