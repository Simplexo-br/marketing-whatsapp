# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import requests
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
cr.execute("SELECT id, name, waba_id, token, phone_number_id, app_id FROM whatsapp_account WHERE status = 'connected' LIMIT 1;")
row = cr.fetchone()
conn.close()

acc_id, name, waba_id, token, phone_number_id, app_id = row
token = token.strip()

url = f"https://graph.facebook.com/v21.0/{waba_id}"
params = {
    "fields": "id,name,currency,timezone_id,message_template_namespace,owner_business_info,primary_funding_id,purchase_order_number,billing_configuration"
}
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(url, headers=headers, params=params)
print("WABA Info:")
print(resp.json())

# Consultar tambem info da linha de credito / funding
url_phone = f"https://graph.facebook.com/v21.0/{phone_number_id}"
resp_phone = requests.get(url_phone, headers=headers, params={"fields": "id,display_phone_number,verified_name,code_verification_status,quality_rating,account_mode"})
print("Phone Info:")
print(resp_phone.json())
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
