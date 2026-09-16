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

cr.execute(\"\"\"
    SELECT count(*) 
    FROM simplexo_aios_whatsapp_webhook_event 
    WHERE payload_json LIKE '%"statuses"%';
\"\"\")
print("Eventos com statuses:", cr.fetchone()[0])

cr.execute(\"\"\"
    SELECT payload_json 
    FROM simplexo_aios_whatsapp_webhook_event 
    WHERE payload_json LIKE '%"statuses"%' 
    ORDER BY id DESC 
    LIMIT 3;
\"\"\")
for r in cr.fetchall():
    try:
        p = json.loads(r[0])
        print("STATUS SAMPLE:")
        for entry in p.get('entry', []):
            for change in entry.get('changes', []):
                for st in change.get('value', {}).get('statuses', []):
                    print(" ", st.get('id'), st.get('status'), st.get('recipient_id'))
    except Exception as e:
        print("Err:", e)

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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=30)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
