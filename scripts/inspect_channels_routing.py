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

cr.execute(\"\"\"
    SELECT id, name, phone_e164, status, 
           enable_welcome_routing, welcome_header, welcome_button_text, welcome_message_body,
           dept_1_id, dept_2_id, dept_3_id, dept_4_id
    FROM simplexo_aios_whatsapp_channel;
\"\"\")
channels = cr.fetchall()
print(f"Total Canais AIOS: {len(channels)}")
cols = ['id', 'name', 'phone_e164', 'status', 'enable_welcome_routing', 'welcome_header', 'welcome_button_text', 'welcome_message_body', 'dept_1_id', 'dept_2_id', 'dept_3_id', 'dept_4_id']
for ch in channels:
    print("--- CANAL ---")
    for k, v in zip(cols, ch):
        print(f"  {k}: {v}")

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
