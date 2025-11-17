# core/contatos_controller.py
import csv
import os
import datetime
from typing import List, Dict

# Se quiser ler XLSX
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

CSV_FILE = "contatos.csv"
CSV_HEADERS = ["id", "nome", "telefone", "status", "mensagem", "ultimo_envio"]

STATUS_OPTIONS = ["Pendente", "Enviado", "Falha"]

def _ensure_csv_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()

def load_contacts() -> List[Dict]:
    _ensure_csv_exists()
    contatos = []
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contatos.append(row)
    except Exception:
        return []
    return contatos

def save_contacts(contatos: List[Dict]) -> bool:
    try:
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(contatos)
        return True
    except Exception:
        return False

def _next_id(contatos: List[Dict]) -> int:
    ids = [int(c["id"]) for c in contatos if c.get("id") and str(c["id"]).isdigit()]
    return (max(ids) + 1) if ids else 1

def add_contact(nome: str, telefone: str, mensagem: str = "", status: str = "Pendente") -> Dict:
    contatos = load_contacts()
    new_id = _next_id(contatos)
    novo = {
        "id": str(new_id),
        "nome": nome,
        "telefone": telefone,
        "status": status if status in STATUS_OPTIONS else "Pendente",
        "mensagem": mensagem,
        "ultimo_envio": ""
    }
    contatos.append(novo)
    save_contacts(contatos)
    return novo

def edit_contact(contact_id: str, nome: str, telefone: str, mensagem: str, status: str) -> bool:
    contatos = load_contacts()
    updated = False
    for c in contatos:
        if c.get("id") == str(contact_id):
            c["nome"] = nome
            c["telefone"] = telefone
            c["mensagem"] = mensagem
            c["status"] = status if status in STATUS_OPTIONS else c["status"]
            updated = True
            break
    if updated:
        save_contacts(contatos)
    return updated

def delete_contact(contact_id: str) -> bool:
    contatos = load_contacts()
    novo = [c for c in contatos if c.get("id") != str(contact_id)]
    if len(novo) == len(contatos):
        return False
    save_contacts(novo)
    return True

def get_contact(contact_id: str) -> Dict:
    contatos = load_contacts()
    for c in contatos:
        if c.get("id") == str(contact_id):
            return c
    return {}

def mark_sent(contact_id: str) -> bool:
    contatos = load_contacts()
    updated = False
    for c in contatos:
        if c.get("id") == str(contact_id):
            c["status"] = "Enviado"
            c["ultimo_envio"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            updated = True
            break
    if updated:
        save_contacts(contatos)
    return updated

# ---------- NOVAS FUNÇÕES DE IMPORTAÇÃO ----------
def import_from_file(file_path: str, columns_map: Dict[str,str]) -> List[Dict]:
    """
    Importa contatos de CSV ou XLSX.
    columns_map: {"nome": "Nome da coluna", "telefone": "Telefone", ...}
    """
    contatos = load_contacts()
    novos_contatos = []

    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path, encoding="utf-8") if PANDAS_AVAILABLE else None
        if df is None:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                df = pd.DataFrame(reader)
    elif file_path.lower().endswith(".xlsx"):
        if not PANDAS_AVAILABLE:
            raise Exception("Pandas não disponível para XLSX")
        df = pd.read_excel(file_path)
    else:
        raise Exception("Formato não suportado")

    for _, row in df.iterrows():
        nome = str(row.get(columns_map.get("nome",""), "")).strip()
        telefone = str(row.get(columns_map.get("telefone",""), "")).strip()
        status = str(row.get(columns_map.get("status",""), "Pendente")).strip()
        mensagem = str(row.get(columns_map.get("mensagem",""), "")).strip()
        if not nome or not telefone:
            continue

        # Checar duplicados
        exist = next((c for c in contatos if c["telefone"] == telefone), None)
        if exist:
            novos_contatos.append({"duplicate": True, "existing": exist,
                                   "new": {"nome": nome, "telefone": telefone,
                                           "status": status, "mensagem": mensagem}})
        else:
            novo = add_contact(nome, telefone, mensagem, status)
            novos_contatos.append({"duplicate": False, "new": novo})
    return novos_contatos
