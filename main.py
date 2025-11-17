from core.theme import aplicar_tema
from components.sidebar import Sidebar
from pages.dashboard import DashboardPage
import customtkinter as ctk

class INETApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("INET - GERENCIADOR DE CONTATOS V9 (testes)")
        self.geometry("1200x700")
        self.resizable(False, False)
        aplicar_tema()

        # Sidebar (menu lateral)
        self.sidebar = Sidebar(self, command=self.navegar)
        self.sidebar.pack(side="left", fill="y")

        # Frame principal (onde as páginas aparecem)
        self.container = ctk.CTkFrame(self, corner_radius=15)
        self.container.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Página inicial
        self.pagina_atual = None
        self.navegar("dashboard")

    def navegar(self, destino: str):
        # Remove a página atual se existir
        if self.pagina_atual is not None: 
            self.pagina_atual.pack_forget()
            self.pagina_atual.destroy()

        # Cria nova página conforme o destino
        if destino == "dashboard":
            self.pagina_atual = DashboardPage(self.container)
        elif destino == "contatos":
            from pages.contatos import ContatosPage
            self.pagina_atual = ContatosPage(self.container)
        elif destino == "config":
            from pages.config_page import ConfigPage
            self.pagina_atual = ConfigPage(self.container)

        self.pagina_atual.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = INETApp()
    app.mainloop()
