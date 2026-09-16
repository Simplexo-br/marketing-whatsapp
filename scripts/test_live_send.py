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
cr.execute("SELECT id, name, waba_id, token, phone_number_id FROM whatsapp_account WHERE status = 'connected' LIMIT 1;")
row = cr.fetchone()
conn.close()

acc_id, name, waba_id, token, phone_number_id = row
token = token.strip()

# Testar envio com o novo template aprovado simplexo_gestao_completa_v1
url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Usar um numero de teste (ex: o proprio numero da empresa ou celular)
payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "551150288495", # proprio numero da Simplexo
    "type": "template",
    "template": {
        "name": "simplexo_gestao_completa_v1",
        "language": {
            "code": "pt_BR"
        },
        "components": [
            {
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {
                            "link": "https://simplexohub.com.br/marketing_whatsapp/static/src/img/simplexo_banner_marketing.png"
                        }
                    }
                ]
            }
        ]
    }
}

resp = requests.post(url, headers=headers, json=payload, timeout=20)
print("Resposta do teste de envio Meta:")
print("Status code:", resp.status_code)
print("Corpo:", resp.json())
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
