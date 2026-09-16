# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
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

# 1. Departamentos cadastrados
print("=== TABELA: simplexo_aios_whatsapp_department ===")
cr.execute(\"\"\"
    SELECT id, name, code, sequence, active 
    FROM simplexo_aios_whatsapp_department 
    ORDER BY sequence, id;
\"\"\")
for r in cr.fetchall():
    print(r)

# 2. Automation Flows
print("\\n=== TABELA: simplexo_aios_whatsapp_automation_flow ===")
cr.execute(\"\"\"
    SELECT id, name, trigger_type, active 
    FROM simplexo_aios_whatsapp_automation_flow;
\"\"\")
for r in cr.fetchall():
    print(r)

# 3. Automation Nodes
print("\\n=== TABELA: simplexo_aios_whatsapp_automation_node ===")
cr.execute(\"\"\"
    SELECT id, flow_id, name, node_type, sequence 
    FROM simplexo_aios_whatsapp_automation_node 
    ORDER BY sequence, id;
\"\"\")
for r in cr.fetchall():
    print(r)

# 4. WhatsApp Channels / Configs
print("\\n=== TABELA: simplexo_aios_whatsapp_channel ===")
cr.execute(\"\"\"
    SELECT column_name FROM information_schema.columns WHERE table_name = 'simplexo_aios_whatsapp_channel';
\"\"\")
cols = [c[0] for c in cr.fetchall()]
print("Colunas do canal:", cols)
cr.execute(\"\"\"
    SELECT id, name, phone_number, is_active FROM simplexo_aios_whatsapp_channel;
\"\"\")
for r in cr.fetchall():
    print(r)

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
