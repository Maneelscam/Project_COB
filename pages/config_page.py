import customtkinter as ctk
from tkinter import messagebox
# Importa o CÉREBRO
from core import contatos_controller as ctrl

# Esta é a CLASSE (a TELA) que o main.py está procurando
class ConfigPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Frame Principal ---
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Título ---
        title_label = ctk.CTkLabel(main_frame, text="Modelo de Mensagem Padrão", 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # --- Instruções ---
        instructions = (
            "Escreva seu modelo de mensagem abaixo.\n"
            "Use as chaves {} para personalizar a mensagem com os dados do cliente:\n\n"
            "   • {nome}        -> Substitui pelo nome completo (ex: Maneelscam)\n"
            "   • {primeiro_nome} -> Substitui pelo primeiro nome (ex: Maneel)\n"
            "   • {telefone}    -> Substitui pelo telefone do cliente\n"
        )
        instructions_label = ctk.CTkLabel(main_frame, text=instructions, justify="left",
                                          font=ctk.CTkFont(size=13))
        instructions_label.grid(row=1, column=0, sticky="w", padx=20, pady=10)

        # --- Caixa de Texto para o Modelo ---
        self.template_textbox = ctk.CTkTextbox(main_frame, height=250, 
                                               font=ctk.CTkFont(size=14))
        self.template_textbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # --- Botão Salvar ---
        self.save_button = ctk.CTkButton(main_frame, text="Salvar Modelo", 
                                         command=self.save_template)
        self.save_button.grid(row=3, column=0, sticky="e", padx=20, pady=20)

        # Carregar o modelo salvo
        self.load_template()

    def load_template(self):
        """Pede ao CÉREBRO (controller) para carregar o modelo."""
        template = ctrl.load_message_template()
        self.template_textbox.insert("1.0", template)

    def save_template(self):
        """Pede ao CÉREBRO (controller) para salvar o modelo."""
        template_content = self.template_textbox.get("1.0", "end-1c")
        try:
            template_content.format(nome="Teste", primeiro_nome="Teste", telefone="Teste")
            
            ctrl.save_message_template(template_content) # Chama o CÉREBRO
            messagebox.showinfo("Sucesso", "Modelo de mensagem salvo com sucesso!")

        except KeyError as e:
            messagebox.showerror("Erro de Formatação", 
                                 "Ocorreu um erro com sua formatação. Verifique as chaves {}.\n" +
                                 f"Erro: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")