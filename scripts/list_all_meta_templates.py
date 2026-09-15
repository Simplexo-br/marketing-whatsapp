# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import os
import requests

token = os.environ.get('META_WHATSAPP_TOKEN', '').strip()
waba_id = "852874847875747"

url = f"https://graph.facebook.com/v20.0/{waba_id}/message_templates?limit=100"
resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
data = resp.json().get('data', [])
print(f"Total de templates na Meta: {len(data)}")
for t in data:
    print(f"Nome: {t.get('name')} | Categoria: {t.get('category')} | Status: {t.get('status')} | Idioma: {t.get('language')}")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo -E /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=60)
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print("STDERR:", stderr.encode('ascii', errors='replace').decode('ascii'))
