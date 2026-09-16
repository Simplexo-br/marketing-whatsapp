# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
import json
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo.tools import config
config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf'])
import psycopg2

conn_params = {
    'dbname': 'simplexo',
    'user': config['db_user'],
    'password': config['db_password'],
    'host': config['db_host'] or 'localhost',
    'port': config['db_port'] or 5432
}
conn = psycopg2.connect(**conn_params)
cr = conn.cursor()

print("=== COLETANDO STATUSES DE simplexo_aios_whatsapp_webhook_event ===")
cr.execute(\"\"\"
    SELECT payload_json 
    FROM simplexo_aios_whatsapp_webhook_event 
    WHERE payload_json LIKE '%"statuses"%'
    ORDER BY id ASC;
\"\"\")
rows = cr.fetchall()
print(f"Total de eventos com statuses: {len(rows)}")

delivered_ids = set()
read_ids = set()
failed_data = {}

for r in rows:
    try:
        data = json.loads(r[0])
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                for st in change.get('value', {}).get('statuses', []):
                    wamid = st.get('id')
                    status = st.get('status')
                    if not wamid:
                        continue
                    if status == 'delivered':
                        delivered_ids.add(wamid)
                    elif status == 'read':
                        read_ids.add(wamid)
                    elif status == 'failed':
                        errs = st.get('errors', [])
                        code = str(errs[0].get('code')) if errs else 'ERROR'
                        msg = errs[0].get('message', 'Erro') if errs else ''
                        failed_data[wamid] = (code, msg)
    except Exception:
        pass

print(f"WAMIDs entregues: {len(delivered_ids)}")
print(f"WAMIDs lidos: {len(read_ids)}")
print(f"WAMIDs com falha: {len(failed_data)}")

# Atualizar mailing_trace em lote para performance ultra-rapida
if read_ids:
    cr.execute(\"\"\"
        UPDATE mailing_trace
        SET whatsapp_status = 'read',
            whatsapp_read_date = COALESCE(whatsapp_read_date, NOW())
        WHERE whatsapp_message_id = ANY(%s) AND whatsapp_status != 'read';
    \"\"\", (list(read_ids),))
    print(f"Traces atualizados para READ: {cr.rowcount}")

# Para os entregues que nao foram lidos
deliv_only = delivered_ids - read_ids
if deliv_only:
    cr.execute(\"\"\"
        UPDATE mailing_trace
        SET whatsapp_status = 'delivered',
            whatsapp_delivered_date = COALESCE(whatsapp_delivered_date, NOW())
        WHERE whatsapp_message_id = ANY(%s) AND whatsapp_status NOT IN ('delivered', 'read');
    \"\"\", (list(deliv_only),))
    print(f"Traces atualizados para DELIVERED: {cr.rowcount}")

# Para falhas
for wamid, (code, msg) in failed_data.items():
    cr.execute(\"\"\"
        UPDATE mailing_trace
        SET whatsapp_status = 'failed',
            whatsapp_error_code = %s,
            whatsapp_error_message = %s
        WHERE whatsapp_message_id = %s;
    \"\"\", (code, msg, wamid))

conn.commit()

# Verificar contagem atual de traces
cr.execute(\"\"\"
    SELECT whatsapp_status, count(*)
    FROM mailing_trace
    WHERE trace_type = 'whatsapp'
    GROUP BY whatsapp_status;
\"\"\")
print("Contagem final de mailing_trace:")
for r in cr.fetchall():
    print(" ", r)

conn.close()
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo -E /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
