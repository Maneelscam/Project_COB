import json  # Usado para salvar o modelo de mensagem
import os
import sqlite3
import uuid
from datetime import datetime
import math
import textwrap  # <-- ADICIONADO para formatar a mensagem

# --- Constantes ---
DB_FILE = 'banco.db'
CONFIG_FILE = 'config.json'
FIELDNAMES = ['id', 'nome', 'telefone', 'status', 'mensagem', 'ultimo_envio']
STATUS_OPTIONS = ["Pendente", "Enviado", "Falha", "Respondido"]

# --- (MENSAGEM ATUALIZADA E FORMATADA) ---
# Este é o novo modelo padrão que você pediu, agora formatado
DEFAULT_TEMPLATE = textwrap.dedent("""\
    Olá, Boa tarde {primeiro_nome}.

    Sou o Emanoel do setor de negociações da INET...💙
    
    Estamos com uma proposta incrível hoje para você:
    50% de desconto nos débitos pendentes para você voltar a 
    desfrutar da melhor internet da cidade !!
    
    Tem interesse ?
    """)

# --- (NOVA FUNÇÃO) ---
# Funções de Configuração (Modelo de Mensagem)
# A TELA 'CONFIGURAÇÕES' PRECISA DISTO

def load_message_template():
# ... (existing code ... load_message_template) ...
    """Lê o modelo de mensagem do config.json. Cria o arquivo se não existir."""
    if not os.path.exists(CONFIG_FILE):
# ... (existing code ... save_message_template) ...
        save_message_template(DEFAULT_TEMPLATE)
        return DEFAULT_TEMPLATE
    
# ... (existing code ... try) ...
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
# ... (existing code ... config) ...
            config = json.load(f)
            return config.get("message_template", DEFAULT_TEMPLATE)
# ... (existing code ... except) ...
    except (json.JSONDecodeError, IOError):
        save_message_template(DEFAULT_TEMPLATE)
# ... (existing code ... return DEFAULT_TEMPLATE) ...
        return DEFAULT_TEMPLATE

# --- (NOVA FUNÇÃO) ---
def save_message_template(template_content):
# ... (existing code ... save_message_template) ...
    """Salva o modelo de mensagem no config.json."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
# ... (existing code ... json.dump) ...
        json.dump({"message_template": template_content}, f, indent=4)

# --- Funções auxiliares de Banco de Dados (SQLite) ---

def _get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria a tabela de contatos caso ainda não exista."""
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contatos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                status TEXT NOT NULL,
                mensagem TEXT,
                ultimo_envio TEXT
            )
            """
        )
        conn.commit()


def load_contacts(page=1, page_size=50, search_query=None, status_filter=None):
# ... (existing code ... load_contacts) ...
    """Carrega contatos do banco SQLite com paginação e filtros."""
    init_db()
    page = max(1, int(page) if page else 1)
    page_size = max(1, int(page_size) if page_size else 50)
    offset = (page - 1) * page_size

    conditions = []
    params = []

    if search_query:
        pattern = f"%{search_query.strip().lower()}%"
        conditions.append("(LOWER(nome) LIKE ? OR LOWER(telefone) LIKE ?)")
        params.extend([pattern, pattern])

    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT id, nome, telefone, status, mensagem, ultimo_envio
        FROM contatos
        {where_clause}
        ORDER BY rowid
        LIMIT ? OFFSET ?
    """
    params.extend([page_size, offset])

    with _get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_total_pages(page_size=50, search_query=None, status_filter=None):
    """Retorna o total de páginas disponíveis para os filtros informados."""
    init_db()
    page_size = max(1, int(page_size) if page_size else 50)

    conditions = []
    params = []

    if search_query:
        pattern = f"%{search_query.strip().lower()}%"
        conditions.append("(LOWER(nome) LIKE ? OR LOWER(telefone) LIKE ?)")
        params.extend([pattern, pattern])

    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"SELECT COUNT(*) as total FROM contatos {where_clause}"

    with _get_connection() as conn:
        row = conn.execute(query, params).fetchone()
        total = row["total"] if row else 0

    total_pages = math.ceil(total / page_size) if total else 1
    return max(1, total_pages)

def get_contact(contact_id):
# ... (existing code ... get_contact) ...
    """Busca um contato específico pelo seu ID."""
    init_db()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT id, nome, telefone, status, mensagem, ultimo_envio FROM contatos WHERE id = ?",
            (contact_id,),
        ).fetchone()
        return dict(row) if row else None

def add_contact(nome, telefone, mensagem="", status="Pendente", ultimo_envio="", custom_id=None):
# ... (existing code ... add_contact) ...
    """Adiciona um novo contato ao banco SQLite. Se custom_id for fornecido e já existir, atualiza a mensagem concatenando."""
    init_db()
    contact_id = custom_id if custom_id else str(uuid.uuid4())[:8]
    
    with _get_connection() as conn:
        # Verifica se o ID já existe
        existing = conn.execute(
            "SELECT id, nome, telefone, status, mensagem, ultimo_envio FROM contatos WHERE id = ?",
            (contact_id,)
        ).fetchone()
        
        if existing:
            # Se existe, concatena a mensagem nova com a existente
            existing_dict = dict(existing)
            mensagem_existente = existing_dict.get('mensagem', '') or ''
            mensagem_nova = mensagem or ''
            
            if mensagem_existente and mensagem_nova:
                mensagem_final = f"{mensagem_existente} | {mensagem_nova}"
            elif mensagem_nova:
                mensagem_final = mensagem_nova
            else:
                mensagem_final = mensagem_existente
            
            # Atualiza o contato existente
            conn.execute(
                """
                UPDATE contatos
                SET nome = ?, telefone = ?, mensagem = ?, status = ?
                WHERE id = ?
                """,
                (nome, telefone, mensagem_final, status, contact_id)
            )
            conn.commit()
            return {
                'id': contact_id,
                'nome': nome,
                'telefone': telefone,
                'status': status,
                'mensagem': mensagem_final,
                'ultimo_envio': existing_dict.get('ultimo_envio', '')
            }
        else:
            # Se não existe, insere novo
            new_contact = {
                'id': contact_id,
                'nome': nome,
                'telefone': telefone,
                'status': status,
                'mensagem': mensagem,
                'ultimo_envio': ultimo_envio
            }
            conn.execute(
                """
                INSERT INTO contatos (id, nome, telefone, status, mensagem, ultimo_envio)
                VALUES (:id, :nome, :telefone, :status, :mensagem, :ultimo_envio)
                """,
                new_contact,
            )
            conn.commit()
            return new_contact

def edit_contact(contact_id, nome, telefone, mensagem, status):
# ... (existing code ... edit_contact) ...
    """Atualiza um contato existente."""
    init_db()
    with _get_connection() as conn:
        cur = conn.execute(
            """
            UPDATE contatos
            SET nome = ?, telefone = ?, mensagem = ?, status = ?
            WHERE id = ?
            """,
            (nome, telefone, mensagem, status, contact_id),
        )
        conn.commit()
        return cur.rowcount > 0

def delete_contact(contact_id):
# ... (existing code ... delete_contact) ...
    """Exclui um contato pelo ID."""
    init_db()
    with _get_connection() as conn:
        cur = conn.execute("DELETE FROM contatos WHERE id = ?", (contact_id,))
        conn.commit()
        return cur.rowcount > 0


# Garante que o banco exista logo ao importar o módulo
init_db()

def mark_sent(contact_id):
# ... (existing code ... mark_sent) ...
    """Marca um contato como 'Enviado' e atualiza a data/hora."""
    contact = get_contact(contact_id)
# ... (existing code ... if contact) ...
    if contact:
        contact['status'] = "Enviado"
# ... (existing code ... contact) ...
        contact['ultimo_envio'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        # Re-usamos edit_contact para salvar
# ... (existing code ... edit_contact) ...
        edit_contact(
            contact_id, 
# ... (existing code ... contact) ...
            contact['nome'], 
            contact['telefone'], 
# ... (existing code ... contact) ...
            contact['mensagem'], 
            contact['status']
# ... (existing code ... ) ...
        )
        return True
# ... (existing code ... return False) ...
    return False


# --- (FUNÇÃO ATUALIZADA - CORRIGE O "nan" E O "sumiço" DA TELA) ---
# A TELA 'CONTATOS' PRECISA DISTO

def get_message_for_contact(contact_id):
# ... (existing code ... get_message_for_contact) ...
    """
    Pega a mensagem de um contato. 
    Se a mensagem estiver vazia, gera uma nova usando o modelo,
# ... (existing code ... salva no contato) ...
    salva no contato e a retorna.
    """
# ... (existing code ... contact) ...
    contact = get_contact(contact_id)
    if not contact:
# ... (existing code ... return) ...
        return "" # Contato não encontrado

    # 1. Verifica se o contato já tem uma mensagem
# ... (existing code ... contact_message_raw) ...
    contact_message_raw = contact.get('mensagem')

    # --- (INÍCIO DA CORREÇÃO "nan") ---
# ... (existing code ... is_empty) ...
    is_empty = False
    if contact_message_raw is None:
# ... (existing code ... is_empty) ...
        is_empty = True
    else:
# ... (existing code ... contact_message_str) ...
        contact_message_str = str(contact_message_raw).strip()
        if not contact_message_str or contact_message_str.lower() == 'nan':
# ... (existing code ... is_empty) ...
            is_empty = True

    if not is_empty:
# ... (existing code ... return str) ...
        return str(contact_message_raw) # Retorna a mensagem original
    # --- (FIM DA CORREÇÃO "nan") ---


# ... (existing code ... Se não tem) ...
    # 2. Se não tem (ou é "nan"), gera uma nova
    template = load_message_template()
    
# ... (existing code ... nome_completo) ...
    nome_completo = contact.get('nome', '')
    primeiro_nome = nome_completo.split(' ')[0]
# ... (existing code ... telefone) ...
    telefone = contact.get('telefone', '')
    
    try:
# ... (existing code ... personalized_message) ...
        personalized_message = template.format(
            nome=nome_completo,
# ... (existing code ... primeiro_nome) ...
            primeiro_nome=primeiro_nome,
            telefone=telefone
# ... (existing code ... ) ...
        )
    except KeyError as e:
# ... (existing code ... print) ...
        print(f"Erro no modelo: variável {e} não encontrada. Usando modelo padrão.")
        personalized_message = DEFAULT_TEMPLATE.format(
# ... (existing code ... nome) ...
            nome=nome_completo,
            primeiro_nome=primeiro_nome,
# ... (existing code ... telefone) ...
            telefone=telefone
        )

# ... (existing code ... Salva a nova) ...
    # 3. Salva a nova mensagem gerada de volta no contato
    edit_contact(
# ... (existing code ... contact_id) ...
        contact_id,
        contact['nome'],
# ... (existing code ... contact) ...
        contact['telefone'],
        personalized_message, # Salva a nova mensagem
# ... (existing code ... contact) ...
        contact['status']
    )

# ... (existing code ... Retorna a nova) ...
    # 4. Retorna a nova mensagem
    return personalized_message