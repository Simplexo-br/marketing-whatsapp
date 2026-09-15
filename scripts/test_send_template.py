# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import os
import requests

token = os.environ.get('META_WHATSAPP_TOKEN', '').strip()
phone_number_id = "1037479776125011"
test_phone = "5511986834173"

payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": test_phone,
    "type": "template",
    "template": {
        "name": "simplexo_erp_vendas_pdv_v1",
        "language": {
            "code": "pt_BR"
        }
    }
}

url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

resp = requests.post(url, headers=headers, json=payload)
print("Status Code:", resp.status_code)
print("Response:", resp.text)
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
print(stdout_bytes.decode('utf-8', errors='replace'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace'))
