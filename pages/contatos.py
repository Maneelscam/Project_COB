import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog, END, filedialog
import tkinter as tk
from core import contatos_controller as ctrl
from urllib.parse import quote
import webbrowser

# Tenta importar o pandas. Se não conseguir, a função de importação será desabilitada.
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("AVISO: 'pandas' não encontrado. A importação de planilhas estará desabilitada.")
    print("Para habilitar, instale com: pip install pandas openpyxl")


class AddEditDialog(simpledialog.Dialog):
    def __init__(self, parent, title, contact=None):
# ... (existing code ... super) ...
        self.contact = contact
        super().__init__(parent, title=title)

    def body(self, master):
# ... (existing code ... master.configure) ...
        master.configure(bg=master.master.cget("bg"))
        tk.Label(master, text="Nome:", bg=master.cget("bg"), fg="#e6eef6").grid(row=0, column=0, sticky="w", padx=6, pady=6)
# ... (existing code ... tk.Label) ...
        tk.Label(master, text="Telefone:", bg=master.cget("bg"), fg="#e6eef6").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        tk.Label(master, text="Status:", bg=master.cget("bg"), fg="#e66eef6").grid(row=2, column=0, sticky="w", padx=6, pady=6)

# ... (existing code ... self.e_nome) ...
        self.e_nome = ctk.CTkEntry(master, width=360)
        self.e_telefone = ctk.CTkEntry(master, width=360)
# ... (existing code ... self.var_status) ...
        self.var_status = ctk.CTkOptionMenu(master, values=ctrl.STATUS_OPTIONS)
        self.e_mensagem = ctk.CTkTextbox(master, height=80)

# ... (existing code ... self.e_nome.grid) ...
        self.e_nome.grid(row=0, column=1, padx=6, pady=6)
        self.e_telefone.grid(row=1, column=1, padx=6, pady=6)
# ... (existing code ... self.var_status.grid) ...
        self.var_status.grid(row=2, column=1, padx=6, pady=6)
        tk.Label(master, text="Mensagem (opcional):", bg=master.cget("bg"), fg="#e6eef6").grid(row=3, column=0, sticky="nw", padx=6, pady=(6,0))
# ... (existing code ... self.e_mensagem.grid) ...
        self.e_mensagem.grid(row=3, column=1, padx=6, pady=6)

        if self.contact:
# ... (existing code ... self.e_nome.insert) ...
            self.e_nome.insert(0, self.contact.get("nome",""))
            self.e_telefone.insert(0, self.contact.get("telefone",""))
# ... (existing code ... self.var_status.set) ...
            self.var_status.set(self.contact.get("status","Pendente"))
            self.e_mensagem.insert("1.0", self.contact.get("mensagem",""))

# ... (existing code ... return self.e_nome) ...
        return self.e_nome

    def apply(self):
# ... (existing code ... nome) ...
        nome = self.e_nome.get().strip()
        tel = self.e_telefone.get().strip()
# ... (existing code ... status) ...
        status = self.var_status.get()
        mensagem = self.e_mensagem.get("1.0", END).strip()
# ... (existing code ... if not nome) ...
        if not nome or not tel:
            messagebox.showwarning("Campos", "Nome e Telefone são obrigatórios.", parent=self)
# ... (existing code ... self.result) ...
            self.result = None
            return
# ... (existing code ... self.result) ...
        self.result = {"nome": nome, "telefone": tel, "status": status, "mensagem": mensagem}


class ContatosPage(ctk.CTkFrame):
    def __init__(self, master):
# ... (existing code ... super) ...
        super().__init__(master, corner_radius=15)
        
        # --- Estilo da Tabela ---
# ... (existing code ... BG_DARK_MAIN) ...
        BG_DARK_MAIN = "#3C3F41"
        BG_DARK_HEADER = "#31335"
# ... (existing code ... TEXT_LIGHT) ...
        TEXT_LIGHT = "#E0E0E0"
        BORDER_DARK = "#4A4A4A"
# ... (existing code ... SELECT_BLUE) ...
        SELECT_BLUE = "#0078D7"
        style = ttk.Style()
# ... (existing code ... style.theme_use) ...
        style.theme_use("clam")
        style.configure("Treeview",
# ... (existing code ... background) ...
                        background=BG_DARK_MAIN,
                        foreground=TEXT_LIGHT,
# ... (existing code ... fieldbackground) ...
                        fieldbackground=BG_DARK_MAIN,
                        bordercolor=BORDER_DARK,
# ... (existing code ... borderwidth) ...
                        borderwidth=0,
                        rowheight=28)
# ... (existing code ... style.layout) ...
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 
        style.configure("Treeview.Heading",
# ... (existing code ... background) ...
                        background=BG_DARK_HEADER,
                        foreground=TEXT_LIGHT,
# ... (existing code ... padding) ...
                        padding=8,
                        font=('TkDefaultFont', 10, 'bold'),
# ... (existing code ... bordercolor) ...
                        bordercolor=BORDER_DARK,
                        borderwidth=1)
# ... (existing code ... style.map) ...
        style.map('Treeview',
                  background=[('selected', SELECT_BLUE)],
# ... (existing code ... foreground) ...
                  foreground=[('selected', 'white')])
        # --- Fim do Estilo ---

# ... (existing code ... Layout da Página) ...
        # --- Layout da Página ---
        self.grid_rowconfigure(2, weight=1)
# ... (existing code ... self.grid_columnconfigure) ...
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

# ... (existing code ... Toolbar superior) ...
        # Toolbar superior
        toolbar = ctk.CTkFrame(self)
# ... (existing code ... toolbar.grid) ...
        toolbar.grid(row=0, column=0, sticky="new", padx=12, pady=(12,6), columnspan=2)
        toolbar.grid_columnconfigure(7, weight=1)

# ... (existing code ... self.btn_add) ...
        self.btn_add = ctk.CTkButton(toolbar, text="➕ Adicionar", command=self.action_add)
        self.btn_add.grid(row=0, column=0, padx=6, pady=6)
# ... (existing code ... self.btn_import) ...
        self.btn_import = ctk.CTkButton(toolbar, text="📂 Importar", command=self.action_import)
        self.btn_import.grid(row=0, column=1, padx=6, pady=6)
# ... (existing code ... if not PANDAS_AVAILABLE) ...
        if not PANDAS_AVAILABLE:
            self.btn_import.configure(state="disabled")
# ... (existing code ... self.btn_edit) ...
        self.btn_edit = ctk.CTkButton(toolbar, text="✏️ Editar", command=self.action_edit)
        self.btn_edit.grid(row=0, column=2, padx=6, pady=6)
# ... (existing code ... self.btn_del) ...
        self.btn_del = ctk.CTkButton(toolbar, text="🗑️ Excluir", command=self.action_delete)
        self.btn_del.grid(row=0, column=3, padx=6, pady=6)
        
        # --- (INÍCIO DA CORREÇÃO) ---
        # O comando estava 'self.action_refresh', que não existe.
        # O comando correto é 'self.refresh_table'.
        self.btn_refresh = ctk.CTkButton(toolbar, text="🔄 Atualizar", command=self.refresh_table)
        # --- (FIM DA CORREÇÃO) ---
        
        self.btn_refresh.grid(row=0, column=4, padx=6, pady=6)
# ... (existing code ... search_label) ...
        search_label = ctk.CTkLabel(toolbar, text="Buscar:")
        search_label.grid(row=0, column=5, padx=(12,6))
# ... (existing code ... self.search_entry) ...
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Nome ou Telefone...", width=240)
        self.search_entry.grid(row=0, column=6, padx=6)
# ... (existing code ... self.search_entry.bind) ...
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        # Barra de Filtro de Status
# ... (existing code ... self.filter_frame) ...
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
# ... (existing code ... filter_values) ...
        filter_values = ["Todos"] + ctrl.STATUS_OPTIONS
        self.filter_var = ctk.StringVar(value="Todos")
# ... (existing code ... self.filter_menu) ...
        self.filter_menu = ctk.CTkSegmentedButton(
            self.filter_frame,
# ... (existing code ... values) ...
            values=filter_values,
            variable=self.filter_var,
# ... (existing code ... command) ...
            command=self.on_filter_change
        )
# ... (existing code ... self.filter_menu.pack) ...
        self.filter_menu.pack(fill="x")

        # Tabela (Treeview)
# ... (existing code ... self.table_frame) ...
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
# ... (existing code ... self.table_frame.grid_rowconfigure) ...
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
# ... (existing code ... columns) ...
        columns = ("id","nome","telefone","status","ultimo_envio")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
# ... (existing code ... self.tree.heading) ...
        self.tree.heading("nome", text="Nome")
        self.tree.heading("telefone", text="Telefone")
# ... (existing code ... self.tree.heading) ...
        self.tree.heading("status", text="Status")
        self.tree.heading("ultimo_envio", text="Último envio")
# ... (existing code ... self.tree.column) ...
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("nome", width=250, minwidth=200)
# ... (existing code ... self.tree.column) ...
        self.tree.column("telefone", width=140, minwidth=120)
        self.tree.column("status", width=100, minwidth=90, anchor="center")
# ... (existing code ... self.tree.column) ...
        self.tree.column("ultimo_envio", width=150, minwidth=140, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
# ... (existing code ... vsb) ...
        vsb = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
# ... (existing code ... vsb.grid) ...
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select())
# ... (existing code ... self.tree.bind) ...
        self.tree.bind("<Double-1>", lambda e: self.view_message())

        # Painel da Direita: Detalhes
# ... (existing code ... self.detail_panel) ...
        self.detail_panel = ctk.CTkFrame(self, width=320)
        self.detail_panel.grid(row=2, column=1, sticky="nse", padx=(6,12), pady=6)
# ... (existing code ... self.detail_panel.grid_rowconfigure) ...
        self.detail_panel.grid_rowconfigure(6, weight=1)
        ctk.CTkLabel(self.detail_panel, text="Detalhes", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(12,6))
# ... (existing code ... self.lbl_nome) ...
        self.lbl_nome = ctk.CTkLabel(self.detail_panel, text="Nome: —")
        self.lbl_nome.grid(row=1, column=0, sticky="w", padx=12, pady=4)
# ... (existing code ... self.lbl_tel) ...
        self.lbl_tel = ctk.CTkLabel(self.detail_panel, text="Telefone: —")
        self.lbl_tel.grid(row=2, column=0, sticky="w", padx=12, pady=4)
# ... (existing code ... self.lbl_status) ...
        self.lbl_status = ctk.CTkLabel(self.detail_panel, text="Status: —")
        self.lbl_status.grid(row=3, column=0, sticky="w", padx=12, pady=4)
# ... (existing code ... self.lbl_ultimo) ...
        self.lbl_ultimo = ctk.CTkLabel(self.detail_panel, text="Último envio: —")
        self.lbl_ultimo.grid(row=4, column=0, sticky="w", padx=12, pady=4)
# ... (existing code ... ctk.CTkLabel) ...
        ctk.CTkLabel(self.detail_panel, text="Mensagem:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, sticky="w", padx=12, pady=(12,4))
        self.msg_text = ctk.CTkTextbox(self.detail_panel, height=180)
# ... (existing code ... self.msg_text.grid) ...
        self.msg_text.grid(row=6, column=0, padx=12, pady=(0,12), sticky="nsew")
        self.msg_text.configure(state="disabled")
# ... (existing code ... self.btn_view_msg) ...
        self.btn_view_msg = ctk.CTkButton(self.detail_panel, text="Ver / Editar Mensagem", command=self.view_message)
        self.btn_view_msg.grid(row=7, column=0, padx=12, pady=6, sticky="ew")
# ... (existing code ... self.btn_send_whatsapp) ...
        self.btn_send_whatsapp = ctk.CTkButton(self.detail_panel, text="Enviar via WhatsApp", command=self.send_whatsapp)
        self.btn_send_whatsapp.grid(row=8, column=0, padx=12, pady=6, sticky="ew")

# ... (existing code ... self.refresh_table) ...
        self.refresh_table()

    # ---------- Operações da Tabela ----------
# ... (existing code ... def refresh_table) ...
    def refresh_table(self):
        """Carrega contatos do controller e atualiza a treeview, filtrando pela busca."""
# ... (existing code ... selected_id) ...
        selected_id = None
        if self.tree.focus():
# ... (existing code ... vals) ...
            vals = self.tree.item(self.tree.focus())["values"]
            if vals:
# ... (existing code ... selected_id) ...
                selected_id = str(vals[0])
        
        contatos = ctrl.load_contacts()
# ... (existing code ... termo) ...
        termo = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""
        filtro_status = self.filter_var.get() if hasattr(self, "filter_var") else "Todos"

# ... (existing code ... self.tree.delete) ...
        self.tree.delete(*self.tree.get_children())
        
        item_a_selecionar = None
# ... (existing code ... for c) ...
        for c in contatos:
            if filtro_status != "Todos":
# ... (existing code ... if c.get) ...
                if c.get("status", "Pendente") != filtro_status:
                    continue
# ... (existing code ... if termo) ...
            if termo:
                if termo not in c.get("nome","" ).lower() and termo not in c.get("telefone","" ).lower():
# ... (existing code ... continue) ...
                    continue
            
            contact_id_str = str(c.get("id",""))
# ... (existing code ... item_id) ...
            item_id = self.tree.insert("", END, values=(
                contact_id_str, 
# ... (existing code ... c.get) ...
                c.get("nome","" ), 
                c.get("telefone","" ), 
# ... (existing code ... c.get) ...
                c.get("status","" ), 
                c.get("ultimo_envio","" )
# ... (existing code ... )) ...
            ))
            if contact_id_str == selected_id:
# ... (existing code ... item_a_selecionar) ...
                item_a_selecionar = item_id
        
        if item_a_selecionar:
# ... (existing code ... self.tree.selection_set) ...
            self.tree.selection_set(item_a_selecionar)
            self.tree.focus(item_a_selecionar)
# ... (existing code ... self.on_select) ...
            self.on_select()
        else:
# ... (existing code ... self.clear_details) ...
            self.clear_details()

    # --- (ESTA É A FUNÇÃO QUE ESTÁ CAUSANDO O BUG) ---
# ... (existing code ... def on_select) ...
    def on_select(self):
        sel = self.tree.focus()
# ... (existing code ... if not sel) ...
        if not sel: return
        vals = self.tree.item(sel)["values"]
# ... (existing code ... if not vals) ...
        if not vals: return
        
        cid = str(vals[0])
        
# ... (existing code ... INÍCIO DA CORREÇÃO) ...
        # --- (INÍCIO DA CORREÇÃO) ---
        # 1. Pede ao "Cérebro" (controller) para buscar o contato
        contact = ctrl.get_contact(cid) 
# ... (existing code ... if not contact) ...
        if not contact:
            self.clear_details()
# ... (existing code ... return) ...
            return
        
        # 2. Atualiza os detalhes (Nome, Telefone, etc.)
# ... (existing code ... self.lbl_nome.configure) ...
        self.lbl_nome.configure(text=f"Nome: {contact.get('nome','—')}")
        self.lbl_tel.configure(text=f"Telefone: {contact.get('telefone','—')}")
# ... (existing code ... self.lbl_status.configure) ...
        self.lbl_status.configure(text=f"Status: {contact.get('status','—')}")
        self.lbl_ultimo.configure(text=f"Último envio: {contact.get('ultimo_envio','—')}")
        
# ... (existing code ... Pede ao) ...
        # 3. Pede ao "Cérebro" (controller) a MENSAGEM CORRETA.
        #    O Cérebro vai verificar se é "nan" e gerar uma nova se for.
# ... (existing code ... message_to_display) ...
        message_to_display = ctrl.get_message_for_contact(cid)
        
        # 4. Atualiza a caixa de texto com a mensagem que o Cérebro retornou
# ... (existing code ... self.msg_text.configure) ...
        self.msg_text.configure(state="normal")
        self.msg_text.delete("1.0", END)
# ... (existing code ... self.msg_text.insert) ...
        self.msg_text.insert("1.0", message_to_display)
        self.msg_text.configure(state="disabled")
# ... (existing code ... FIM DA CORREÇÃO) ...
        # --- (FIM DA CORREÇÃO) ---

    def clear_details(self):
# ... (existing code ... self.lbl_nome.configure) ...
        self.lbl_nome.configure(text="Nome: —")
        self.lbl_tel.configure(text="Telefone: —")
# ... (existing code ... self.lbl_status.configure) ...
        self.lbl_status.configure(text="Status: —")
        self.lbl_ultimo.configure(text="Último envio: —")
# ... (existing code ... self.msg_text.configure) ...
        self.msg_text.configure(state="normal")
        self.msg_text.delete("1.0", END)
# ... (existing code ... self.msg_text.configure) ...
        self.msg_text.configure(state="disabled")

    # ---------- Ações (CRUD) ----------
# ... (existing code ... def action_add) ...
    def action_add(self):
        dlg = AddEditDialog(self, "Adicionar Contato")
# ... (existing code ... data) ...
        data = getattr(dlg, "result", None)
        if data:
# ... (existing code ... novo) ...
            novo = ctrl.add_contact(data["nome"], data["telefone"], mensagem=data["mensagem"], status=data["status"])
            messagebox.showinfo("Adicionado", f"Contato '{novo.get('nome')}' adicionado.")
# ... (existing code ... self.refresh_table) ...
            self.refresh_table()

    def action_edit(self):
# ... (existing code ... sel) ...
        sel = self.tree.focus()
        if not sel:
# ... (existing code ... messagebox.showwarning) ...
            messagebox.showwarning("Seleção", "Escolha um contato para editar.")
            return
# ... (existing code ... cid) ...
        cid = self.tree.item(sel)["values"][0]
        contact = ctrl.get_contact(str(cid))
# ... (existing code ... dlg) ...
        dlg = AddEditDialog(self, "Editar Contato", contact=contact)
        data = getattr(dlg, "result", None)
# ... (existing code ... if data) ...
        if data:
            ok = ctrl.edit_contact(cid, data["nome"], data["telefone"], data["mensagem"], data["status"])
# ... (existing code ... if ok) ...
            if ok:
                messagebox.showinfo("Editado", "Contato atualizado.")
# ... (existing code ... self.refresh_table) ...
                self.refresh_table()
            else:
# ... (existing code ... messagebox.showerror) ...
                messagebox.showerror("Erro", "Falha ao editar contato.")

    def action_delete(self):
# ... (existing code ... sel) ...
        sel = self.tree.focus()
        if not sel:
# ... (existing code ... messagebox.showwarning) ...
            messagebox.showwarning("Seleção", "Escolha um contato para excluir.")
            return
# ... (existing code ... cid) ...
        cid = self.tree.item(sel)["values"][0]
        nome = self.tree.item(sel)["values"][1]
# ... (existing code ... ans) ...
        ans = messagebox.askyesno("Confirmar exclusão", f"Excluir '{nome}' (ID: {cid})? Esta ação não pode ser desfeita.")
        if not ans:
# ... (existing code ... return) ...
            return
        ok = ctrl.delete_contact(cid)
# ... (existing code ... if ok) ...
        if ok:
            messagebox.showinfo("Removido", f"Contato '{nome}' excluído.")
# ... (existing code ... self.refresh_table) ...
            self.refresh_table()
        else:
# ... (existing code ... messagebox.showerror) ...
            messagebox.showerror("Erro", "Falha ao excluir contato.")

    # --- Ações de Filtro e Importação ---
# ... (existing code ... def on_filter_change) ...
    def on_filter_change(self, value):
        self.refresh_table()

# ... (existing code ... def action_import) ...
    def action_import(self):
        if not PANDAS_AVAILABLE:
# ... (existing code ... messagebox.showerror) ...
            messagebox.showerror("Recurso Faltando", 
                                 "A biblioteca 'pandas' é necessária para importar planilhas.\n"
# ... (existing code ... No seu terminal) ...
                                 "No seu terminal, execute: pip install pandas openpyxl",
                                 parent=self)
# ... (existing code ... return) ...
            return

        filepath = filedialog.askopenfilename(
# ... (existing code ... title) ...
            title="Selecionar planilha para importar",
            filetypes=[("Planilhas Excel", "*.xlsx"), ("Planilhas CSV", "*.csv"), ("Todos os Arquivos", "*.*")],
# ... (existing code ... parent) ...
            parent=self
        )
# ... (existing code ... if not filepath) ...
        if not filepath: return
        try:
# ... (existing code ... if filepath.endswith) ...
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
# ... (existing code ... else) ...
            else:
                df = pd.read_excel(filepath)

# ... (existing code ... if 'Nome') ...
            if 'Nome' not in df.columns or 'Telefone' not in df.columns:
                messagebox.showerror("Colunas Faltando", 
# ... (existing code ... A planilha) ...
                                     "A planilha DEVE conter colunas chamadas 'Nome' e 'Telefone'.\n"
                                     "Uma coluna 'Mensagem' é opcional.",
# ... (existing code ... parent) ...
                                     parent=self)
                return

# ... (existing code ... importados) ...
            importados = 0
            for index, row in df.iterrows():
# ... (existing code ... try) ...
                try:
                    nome = str(row['Nome']).strip()
# ... (existing code ... tel) ...
                    tel = str(row['Telefone']).strip().replace('.0', '')
                    msg = str(row.get('Mensagem', '')).strip()
# ... (existing code ... if nome) ...
                    if nome and tel:
                        # Se a planilha tiver uma mensagem, usa ela. Senão, fica em branco (para ser gerada).
# ... (existing code ... ctrl.add_contact) ...
                        ctrl.add_contact(nome, tel, mensagem=msg, status="Pendente")
                        importados += 1
# ... (existing code ... except Exception) ...
                except Exception as e:
                    print(f"Erro ao importar linha {index}: {e}")
            
# ... (existing code ... messagebox.showinfo) ...
            messagebox.showinfo("Importação Concluída", 
                                f"{importados} de {len(df)} contatos foram importados com status 'Pendente'.",
# ... (existing code ... parent) ...
                                parent=self)
            self.refresh_table()
# ... (existing code ... except Exception) ...
        except Exception as e:
            messagebox.showerror("Erro ao Ler Arquivo", f"Não foi possível ler a planilha.\nErro: {e}", parent=self)

# ... (existing code ... def view_message) ...
    # --- Ações de Mensagem ---
    def view_message(self):
# ... (existing code ... sel) ...
        sel = self.tree.focus()
        if not sel:
# ... (existing code ... messagebox.showwarning) ...
            messagebox.showwarning("Seleção", "Selecione um contato para ver a mensagem.")
            return
# ... (existing code ... cid) ...
        cid = self.tree.item(sel)["values"][0]
        contact = ctrl.get_contact(cid)
# ... (existing code ... if not contact) ...
        if not contact: return
        
        # Pega a mensagem atual (que pode ter sido recém-gerada)
# ... (existing code ... current_message) ...
        current_message = self.msg_text.get("1.0", "end-1c")

        dlg = simpledialog.askstring("Mensagem", f"Mensagem para {contact.get('nome')}:",
# ... (existing code ... initialvalue) ...
                                      initialvalue=current_message, parent=self)
        if dlg is not None:
# ... (existing code ... Salva a mensagem) ...
            # Salva a mensagem (potencialmente) editada
            ctrl.edit_contact(cid, contact.get("nome",""), contact.get("telefone",""), dlg, contact.get("status","Pendente"))
# ... (existing code ... self.refresh_table) ...
            self.refresh_table()
            self.adicionar_log(f"Mensagem atualizada para {contact.get('nome')}")

# ... (existing code ... def send_whatsapp) ...
    def send_whatsapp(self):
        sel = self.tree.focus()
# ... (existing code ... if not sel) ...
        if not sel:
            messagebox.showwarning("Seleção", "Escolha um contato antes de enviar.")
# ... (existing code ... return) ...
            return
        cid = self.tree.item(sel)["values"][0]
# ... (existing code ... contact) ...
        contact = ctrl.get_contact(cid)
        if not contact: return

# ... (existing code ... Pega a mensagem) ...
        # Pega a mensagem que está no painel de detalhes
        mensagem = self.msg_text.get("1.0", "end-1c").strip()
# ... (existing code ... if not mensagem) ...
        if not mensagem:
            messagebox.showwarning("Mensagem vazia", "A mensagem está vazia. Edite a mensagem antes de enviar.")
# ... (existing code ... return) ...
            return
            
        numero = contact.get("telefone","" )
# ... (existing code ... mensagem_codificada) ...
        mensagem_codificada = quote(mensagem)
        numero_formatado = numero.replace("+","" )
# ... (existing code ... url) ...
        url = f"https://web.whatsapp.com/send?phone={numero_formatado}&text={mensagem_codificada}"
        
# ... (existing code ... try) ...
        try:
            webbrowser.open(url)
# ... (existing code ... ctrl.mark_sent) ...
            ctrl.mark_sent(cid)
            messagebox.showinfo("Enviado", "WhatsApp preparado no navegador. Contato marcado como Enviado.")
# ... (existing code ... self.refresh_table) ...
            self.refresh_table()
        except Exception as e:
# ... (existing code ... messagebox.showerror) ...
            messagebox.showerror("Erro", f"Não foi possível abrir o navegador: {e}")

    def adicionar_log(self, texto: str):
# ... (existing code ... print) ...
        print("[CONTATOS]", texto)