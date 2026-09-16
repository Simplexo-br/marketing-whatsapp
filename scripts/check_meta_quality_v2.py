# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import requests
import json
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
cr.execute("SELECT id, name, waba_id, token, phone_number_id, status FROM whatsapp_account;")
rows = cr.fetchall()
conn.close()

for r in rows:
    acc_id, name, waba_id, token, phone_number_id, status = r
    token = token.strip() if token else ""
    print(f"=== WHATSAPP ACCOUNT ID: {acc_id} | Name: {name} | Status: {status} ===")
    print(f"WABA ID: {waba_id} | Phone Number ID: {phone_number_id}")
    if not token or not phone_number_id:
        continue
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Telefone
    url_phone = f"https://graph.facebook.com/v21.0/{phone_number_id}?fields=display_phone_number,verified_name,quality_rating,messaging_limit_tier,status,code_verification_status,throughput"
    resp = requests.get(url_phone, headers=headers)
    print("Telefone info:", resp.status_code, json.dumps(resp.json(), indent=2))
    
    # 2. WABA
    url_waba = f"https://graph.facebook.com/v21.0/{waba_id}?fields=name,account_review_status,message_template_namespace"
    resp_w = requests.get(url_waba, headers=headers)
    print("WABA info:", resp_w.status_code, json.dumps(resp_w.json(), indent=2))
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=15)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
