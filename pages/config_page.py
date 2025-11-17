import customtkinter as ctk
from core.config import APP_NAME, VERSION, DEVELOPER

class ConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=15)
        ctk.CTkLabel(self, text="Configurações", font=ctk.CTkFont("Segoe UI", 22, "bold")).pack(pady=20)

        info = f"{APP_NAME}\nVersão: {VERSION}\nDesenvolvido por {DEVELOPER}"
        ctk.CTkLabel(self, text=info, text_color="#B0B0B0", justify="left").pack(pady=20)
