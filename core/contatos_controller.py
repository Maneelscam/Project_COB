import csv
import json # Usado para salvar o modelo de mensagem
import os
import uuid
from datetime import datetime
import textwrap # <-- ADICIONADO para formatar a mensagem

# --- Constantes ---
DB_FILE = 'contatos.csv'
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

# --- Funções de Banco de Dados (CSV) ---

def _check_db_file():
# ... (existing code ... _check_db_file) ...
    """Verifica se o arquivo CSV existe e tem os cabeçalhos corretos."""
    if not os.path.exists(DB_FILE):
# ... (existing code ... open) ...
        with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
# ... (existing code ... writer.writeheader) ...
            writer.writeheader()

def load_contacts():
# ... (existing code ... load_contacts) ...
    """Carrega todos os contatos do arquivo CSV."""
    _check_db_file()
# ... (existing code ... contacts) ...
    contacts = []
    with open(DB_FILE, 'r', newline='', encoding='utf-8') as f:
# ... (existing code ... reader) ...
        reader = csv.DictReader(f)
        for row in reader:
# ... (existing code ... contacts.append) ...
            contacts.append(row)
    return contacts

def get_contact(contact_id):
# ... (existing code ... get_contact) ...
    """Busca um contato específico pelo seu ID."""
    contacts = load_contacts()
# ... (existing code ... for contact) ...
    for contact in contacts:
        if contact['id'] == contact_id:
# ... (existing code ... return contact) ...
            return contact
    return None

def add_contact(nome, telefone, mensagem="", status="Pendente", ultimo_envio=""):
# ... (existing code ... add_contact) ...
    """Adiciona um novo contato ao CSV."""
    _check_db_file()
# ... (existing code ... new_contact) ...
    new_contact = {
        'id': str(uuid.uuid4())[:8], # ID curto
# ... (existing code ... 'nome') ...
        'nome': nome,
        'telefone': telefone,
# ... (existing code ... 'status') ...
        'status': status,
        'mensagem': mensagem,
# ... (existing code ... 'ultimo_envio') ...
        'ultimo_envio': ultimo_envio
    }
    
# ... (existing code ... open) ...
    with open(DB_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
# ... (existing code ... writer.writerow) ...
        writer.writerow(new_contact)
    return new_contact

def _save_all_contacts(contacts):
# ... (existing code ... _save_all_contacts) ...
    """Salva a lista inteira de contatos de volta ao CSV (usado por edit/delete)."""
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
# ... (existing code ... writer) ...
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
# ... (existing code ... writer.writerows) ...
        writer.writerows(contacts)

def edit_contact(contact_id, nome, telefone, mensagem, status):
# ... (existing code ... edit_contact) ...
    """Atualiza um contato existente."""
    contacts = load_contacts()
# ... (existing code ... updated) ...
    updated = False
    for contact in contacts:
# ... (existing code ... if contact) ...
        if contact['id'] == contact_id:
            contact['nome'] = nome
# ... (existing code ... contact) ...
            contact['telefone'] = telefone
            contact['mensagem'] = mensagem
# ... (existing code ... contact) ...
            contact['status'] = status
            updated = True
# ... (existing code ... break) ...
            break
    if updated:
# ... (existing code ... _save_all_contacts) ...
        _save_all_contacts(contacts)
    return updated

def delete_contact(contact_id):
# ... (existing code ... delete_contact) ...
    """Exclui um contato pelo ID."""
    contacts = load_contacts()
# ... (existing code ... contacts_to_keep) ...
    contacts_to_keep = [c for c in contacts if c['id'] != contact_id]
    
# ... (existing code ... if len) ...
    if len(contacts) > len(contacts_to_keep):
        _save_all_contacts(contacts_to_keep)
# ... (existing code ... return True) ...
        return True
    return False

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