# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import requests
import psycopg2

import configparser

cfg = configparser.ConfigParser()
cfg.read('/opt/odoo/conf/simplexo.conf')
db_user = cfg.get('options', 'db_user', fallback='simplexo')
db_password = cfg.get('options', 'db_password', fallback='')
db_host = cfg.get('options', 'db_host', fallback=False)
db_port = cfg.get('options', 'db_port', fallback=False)

conn_args = {'dbname': 'simplexo', 'user': db_user}
if db_password: conn_args['password'] = db_password
if db_host: conn_args['host'] = db_host
if db_port: conn_args['port'] = db_port

conn = psycopg2.connect(**conn_args)
cr = conn.cursor()
cr.execute("SELECT id, name, waba_id, token, phone_number_id, app_id FROM whatsapp_account WHERE status = 'connected' LIMIT 1;")
row = cr.fetchone()
conn.close()

if not row:
    print("Nenhuma conta encontrada.")
    exit(0)

acc_id, name, waba_id, token, phone_number_id, app_id = row
print(f"Conta: {name}, WABA: {waba_id}, AppID: {app_id}")

url = f"https://graph.facebook.com/v21.0/{waba_id}/message_templates"
headers = {
    "Authorization": f"Bearer {token.strip()}",
    "Content-Type": "application/json"
}
resp = requests.get(url, headers=headers, params={"limit": 5}, timeout=15)
print("GET message_templates status:", resp.status_code)
data = resp.json()
print("Templates existentes:")
for t in data.get('data', []):
    print(" -", t.get('name'), f"[{t.get('category')}]", t.get('status'))
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
