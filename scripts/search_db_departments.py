# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import os
import psycopg2
import configparser

cfg = configparser.ConfigParser()
cfg.read('/opt/odoo/conf/simplexo.conf')
conn = psycopg2.connect(
    dbname='simplexo',
    user=cfg.get('options', 'db_user', fallback='simplexo'),
    password=cfg.get('options', 'db_password', fallback=''),
    host=cfg.get('options', 'db_host', fallback=False) or None,
    port=cfg.get('options', 'db_port', fallback=False) or None
)
cr = conn.cursor()

# 1. Pastas em /opt/odoo/addons
print("Pastas em /opt/odoo/addons:")
try:
    print(os.listdir('/opt/odoo/addons'))
except Exception as e:
    print(e)

# 2. Pesquisar nas tabelas do banco se ha mensagens salvas com 'Ver Departamentos' ou 'Opção selecionada'
cr.execute(\"\"\"
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
      AND data_type IN ('text', 'character varying')
      AND (table_name LIKE '%whatsapp%' OR table_name LIKE '%mail%' OR table_name LIKE '%aios%' OR table_name LIKE '%chatbot%' OR table_name LIKE '%channel%');
\"\"\")
cols = cr.fetchall()
print(f"Total colunas texto relevantes: {len(cols)}")

# Buscar no mail_message as mensagens enviadas recentemente com 'Departamentos'
cr.execute(\"\"\"
    SELECT id, body, date 
    FROM mail_message 
    WHERE body ILIKE '%Departamento%' OR body ILIKE '%Opção selecionada%' OR body ILIKE '%Seja bem-vindo%'
    ORDER BY id DESC LIMIT 5;
\"\"\")
messages = cr.fetchall()
print("\\nMensagens encontradas em mail_message:")
for m in messages:
    print(m)

# Buscar no whatsapp_template ou aios_whatsapp
cr.execute(\"\"\"
    SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%bot%' OR table_name LIKE '%auto%' OR table_name LIKE '%department%');
\"\"\")
print("\\nTabelas bot/auto/department:")
for t in cr.fetchall():
    print(t)

conn.close()
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=30)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
