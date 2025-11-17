# pages/contatos.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog, END, filedialog
import tkinter as tk
from core import contatos_controller as ctrl
from urllib.parse import quote
import webbrowser

class AddEditDialog(simpledialog.Dialog):
    def __init__(self, parent, title, contact=None):
        self.contact = contact
        super().__init__(parent, title=title)

    def body(self, master):
        master.configure(bg=master.master.cget("bg"))
        tk.Label(master, text="Nome:", bg=master.cget("bg"), fg="#e6eef6").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Label(master, text="Telefone:", bg=master.cget("bg"), fg="#e6eef6").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        tk.Label(master, text="Status:", bg=master.cget("bg"), fg="#e6eef6").grid(row=2, column=0, sticky="w", padx=6, pady=6)

        self.e_nome = ctk.CTkEntry(master, width=360)
        self.e_telefone = ctk.CTkEntry(master, width=360)
        self.var_status = ctk.CTkOptionMenu(master, values=ctrl.STATUS_OPTIONS)
        self.e_mensagem = ctk.CTkTextbox(master, height=80)

        self.e_nome.grid(row=0, column=1, padx=6, pady=6)
        self.e_telefone.grid(row=1, column=1, padx=6, pady=6)
        self.var_status.grid(row=2, column=1, padx=6, pady=6)
        tk.Label(master, text="Mensagem (opcional):", bg=master.cget("bg"), fg="#e6eef6").grid(row=3, column=0, sticky="nw", padx=6, pady=(6,0))
        self.e_mensagem.grid(row=3, column=1, padx=6, pady=6)

        if self.contact:
            self.e_nome.insert(0, self.contact.get("nome",""))
            self.e_telefone.insert(0, self.contact.get("telefone",""))
            self.var_status.set(self.contact.get("status","Pendente"))
            self.e_mensagem.insert("1.0", self.contact.get("mensagem",""))

        return self.e_nome

    def apply(self):
        nome = self.e_nome.get().strip()
        tel = self.e_telefone.get().strip()
        status = self.var_status.get()
        mensagem = self.e_mensagem.get("1.0", END).strip()
        if not nome or not tel:
            messagebox.showwarning("Campos", "Nome e Telefone são obrigatórios.", parent=self)
            self.result = None
            return
        self.result = {"nome": nome, "telefone": tel, "status": status, "mensagem": mensagem}

class ContatosPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=15)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Toolbar superior
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="new", padx=12, pady=(12,6), columnspan=2)
        toolbar.grid_columnconfigure(7, weight=1)

        self.btn_add = ctk.CTkButton(toolbar, text="➕ Adicionar", command=self.action_add)
        self.btn_add.grid(row=0, column=0, padx=6, pady=6)

        self.btn_edit = ctk.CTkButton(toolbar, text="✏️ Editar", command=self.action_edit)
        self.btn_edit.grid(row=0, column=1, padx=6, pady=6)

        self.btn_del = ctk.CTkButton(toolbar, text="🗑️ Excluir", command=self.action_delete)
        self.btn_del.grid(row=0, column=2, padx=6, pady=6)

        self.btn_import = ctk.CTkButton(toolbar, text="📥 Importar", command=self.action_import)
        self.btn_import.grid(row=0, column=3, padx=6, pady=6)

        self.btn_refresh = ctk.CTkButton(toolbar, text="🔄 Atualizar", command=self.refresh_table)
        self.btn_refresh.grid(row=0, column=4, padx=6, pady=6)

        search_label = ctk.CTkLabel(toolbar, text="Buscar:")
        search_label.grid(row=0, column=5, padx=(12,6))
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Nome ou Telefone...", width=240)
        self.search_entry.grid(row=0, column=6, padx=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        # Table (Treeview)
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id","nome","telefone","status","ultimo_envio")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("status", text="Status")
        self.tree.heading("ultimo_envio", text="Último envio")
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("nome", width=360)
        self.tree.column("telefone", width=160)
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("ultimo_envio", width=160, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select())
        self.tree.bind("<Double-1>", lambda e: self.view_message())

        # Right panel: details + message + actions
        self.detail_panel = ctk.CTkFrame(self, width=320)
        self.detail_panel.grid(row=1, column=1, sticky="nse", padx=(6,12), pady=6)
        self.detail_panel.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.detail_panel, text="Detalhes", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(12,6))
        self.lbl_nome = ctk.CTkLabel(self.detail_panel, text="Nome: —")
        self.lbl_nome.grid(row=1, column=0, sticky="w", padx=12, pady=4)
        self.lbl_tel = ctk.CTkLabel(self.detail_panel, text="Telefone: —")
        self.lbl_tel.grid(row=2, column=0, sticky="w", padx=12, pady=4)
        self.lbl_status = ctk.CTkLabel(self.detail_panel, text="Status: —")
        self.lbl_status.grid(row=3, column=0, sticky="w", padx=12, pady=4)
        self.lbl_ultimo = ctk.CTkLabel(self.detail_panel, text="Último envio: —")
        self.lbl_ultimo.grid(row=4, column=0, sticky="w", padx=12, pady=4)

        ctk.CTkLabel(self.detail_panel, text="Mensagem:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, sticky="w", padx=12, pady=(12,4))
        self.msg_text = ctk.CTkTextbox(self.detail_panel, height=180)
        self.msg_text.grid(row=6, column=0, padx=12, pady=(0,12), sticky="nsew")
        self.msg_text.configure(state="disabled")

        # Actions under details
        self.btn_view_msg = ctk.CTkButton(self.detail_panel, text="Ver / Editar Mensagem", command=self.view_message)
        self.btn_view_msg.grid(row=7, column=0, padx=12, pady=6, sticky="ew")
        self.btn_send_whatsapp = ctk.CTkButton(self.detail_panel, text="Enviar via WhatsApp", command=self.send_whatsapp)
        self.btn_send_whatsapp.grid(row=8, column=0, padx=12, pady=6, sticky="ew")

        self.refresh_table()

    # ---------- Table operations ----------
    def refresh_table(self):
        contatos = ctrl.load_contacts()
        termo = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for c in contatos:
            if termo and termo not in c.get("nome","").lower() and termo not in c.get("telefone","").lower():
                continue
            self.tree.insert("", END, values=(c.get("id",""), c.get("nome",""), c.get("telefone",""), c.get("status",""), c.get("ultimo_envio","")))
        self.clear_details()

    def on_select(self):
        sel = self.tree.focus()
        if not sel:
            return
        vals = self.tree.item(sel)["values"]
        if not vals:
            return
        cid = vals[0]
        contact = ctrl.get_contact(str(cid))
        if not contact:
            return
        self.lbl_nome.configure(text=f"Nome: {contact.get('nome','—')}")
        self.lbl_tel.configure(text=f"Telefone: {contact.get('telefone','—')}")
        self.lbl_status.configure(text=f"Status: {contact.get('status','—')}")
        self.lbl_ultimo.configure(text=f"Último envio: {contact.get('ultimo_envio','—')}")
        self.msg_text.configure(state="normal")
        self.msg_text.delete("1.0", END)
        self.msg_text.insert("1.0", contact.get("mensagem",""))
        self.msg_text.configure(state="disabled")

    def clear_details(self):
        self.lbl_nome.configure(text="Nome: —")
        self.lbl_tel.configure(text="Telefone: —")
        self.lbl_status.configure(text="Status: —")
        self.lbl_ultimo.configure(text="Último envio: —")
        self.msg_text.configure(state="normal")
        self.msg_text.delete("1.0", END)
        self.msg_text.configure(state="disabled")

    # ---------- Actions ----------
    def action_add(self):
        dlg = AddEditDialog(self, "Adicionar Contato")
        data = getattr(dlg, "result", None)
        if data:
            novo = ctrl.add_contact(data["nome"], data["telefone"], mensagem=data["mensagem"], status=data["status"])
            messagebox.showinfo("Adicionado", f"Contato '{novo.get('nome')}' adicionado.")
            self.refresh_table()

    def action_edit(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleção", "Escolha um contato para editar.")
            return
        cid = self.tree.item(sel)["values"][0]
        contact = ctrl.get_contact(str(cid))
        dlg = AddEditDialog(self, "Editar Contato", contact=contact)
        data = getattr(dlg, "result", None)
        if data:
            ok = ctrl.edit_contact(cid, data["nome"], data["telefone"], data["mensagem"], data["status"])
            if ok:
                messagebox.showinfo("Editado", "Contato atualizado.")
                self.refresh_table()
            else:
                messagebox.showerror("Erro", "Falha ao editar contato.")

    def action_delete(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleção", "Escolha um contato para excluir.")
            return
        cid = self.tree.item(sel)["values"][0]
        nome = self.tree.item(sel)["values"][1]
        ans = messagebox.askyesno("Confirmar exclusão", f"Excluir '{nome}' (ID: {cid})? Esta ação não pode ser desfeita.")
        if not ans:
            return
        ok = ctrl.delete_contact(cid)
        if ok:
            messagebox.showinfo("Removido", f"Contato '{nome}' excluído.")
            self.refresh_table()
        else:
            messagebox.showerror("Erro", "Falha ao excluir contato.")

    def view_message(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione um contato para ver a mensagem.")
            return
        cid = self.tree.item(sel)["values"][0]
        contact = ctrl.get_contact(cid)
        if not contact:
            return
        dlg = simpledialog.askstring("Mensagem", f"Mensagem para {contact.get('nome')}:",
                                     initialvalue=contact.get("mensagem",""), parent=self)
        if dlg is not None:
            ctrl.edit_contact(cid, contact.get("nome",""), contact.get("telefone",""), dlg, contact.get("status","Pendente"))
            self.refresh_table()
            self.adicionar_log(f"Mensagem atualizada para {contact.get('nome')}")

    def send_whatsapp(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleção", "Escolha um contato antes de enviar.")
            return
        cid = self.tree.item(sel)["values"][0]
        contact = ctrl.get_contact(cid)
        if not contact:
            return
        mensagem = contact.get("mensagem","").strip()
        if not mensagem:
            messagebox.showwarning("Mensagem vazia", "A mensagem está vazia. Edite a mensagem antes de enviar.")
            return
        numero = contact.get("telefone","")
        mensagem_codificada = quote(mensagem)
        numero_formatado = numero.replace("+","")
        url = f"https://web.whatsapp.com/send?phone={numero_formatado}&text={mensagem_codificada}"
        try:
            webbrowser.open(url)
            ctrl.mark_sent(cid)
            messagebox.showinfo("Enviado", "WhatsApp preparado no navegador. Contato marcado como Enviado.")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o navegador: {e}")

    # ---------- IMPORTAÇÃO ----------
    def action_import(self):
        file_path = filedialog.askopenfilename(title="Selecionar arquivo", filetypes=[("CSV / XLSX", "*.csv *.xlsx")])
        if not file_path:
            return

        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Erro", "Pandas necessário para importar arquivos.")
            return

        df = pd.read_excel(file_path) if file_path.endswith(".xlsx") else pd.read_csv(file_path)
        colunas = list(df.columns)
        if not colunas:
            messagebox.showerror("Erro", "Arquivo sem colunas.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Mapear Colunas")
        dlg.grab_set()
        tk.Label(dlg, text="Selecione a coluna correspondente a cada campo:").grid(row=0, column=0, columnspan=2, padx=12, pady=12)

        campos = ["nome", "telefone", "status", "mensagem"]
        vars_col = {}
        for i, campo in enumerate(campos):
            tk.Label(dlg, text=campo.capitalize()+":").grid(row=i+1, column=0, sticky="e", padx=6, pady=6)
            var = tk.StringVar()
            var.set(colunas[0] if colunas else "")
            option = ttk.Combobox(dlg, values=colunas, textvariable=var, width=30, state="readonly")
            option.grid(row=i+1, column=1, padx=6, pady=6)
            vars_col[campo] = var

        def confirmar():
            dlg.columns_map = {campo: vars_col[campo].get() for campo in campos}
            dlg.destroy()

        tk.Button(dlg, text="Confirmar", command=confirmar).grid(row=len(campos)+1, column=0, columnspan=2, pady=12)
        self.wait_window(dlg)
        if not hasattr(dlg, "columns_map"):
            return

        columns_map = dlg.columns_map
        resultados = ctrl.import_from_file(file_path, columns_map)
        adicionados = [r["new"]["nome"] for r in resultados if not r.get("duplicate")]
        duplicados = [r["new"]["nome"] for r in resultados if r.get("duplicate")]

        msg = f"{len(adicionados)} contatos adicionados com sucesso."
        if duplicados:
            msg += f"\n{len(duplicados)} contatos já existentes (não adicionados): {', '.join(duplicados)}"
        messagebox.showinfo("Importação concluída", msg)
        self.refresh_table()

    def adicionar_log(self, texto: str):
        print("[CONTATOS]", texto)
