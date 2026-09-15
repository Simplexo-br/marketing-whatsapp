# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import os
import requests
import odoo
from odoo import api, SUPERUSER_ID

token = os.environ.get('META_WHATSAPP_TOKEN', '').strip()
print(f"Token no ambiente: {token[:15]}...{token[-10:] if token else 'VAZIO'}")

# Testar chamada direta na Meta Graph API com os dados do Canal ID 3
phone_number_id = "1037479776125011"
waba_id = "852874847875747"

headers = {"Authorization": f"Bearer {token}"}
url_phone = f"https://graph.facebook.com/v20.0/{phone_number_id}?fields=verified_name,display_phone_number,quality_rating,messaging_limit_tier"
resp = requests.get(url_phone, headers=headers)
print("Meta Phone Info Status:", resp.status_code, resp.text)

url_templates = f"https://graph.facebook.com/v20.0/{waba_id}/message_templates?limit=10"
resp_tpl = requests.get(url_templates, headers=headers)
print("Meta Templates Status:", resp_tpl.status_code)
if resp_tpl.status_code == 200:
    tpl_data = resp_tpl.json().get('data', [])
    print(f"Total de templates retornados da Meta: {len(tpl_data)}")
    for t in tpl_data[:5]:
        print(f"  Template: {t.get('name')} | Categoria: {t.get('category')} | Status: {t.get('status')} | Lingua: {t.get('language')}")
else:
    print("Meta Templates Erro:", resp_tpl.text)
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
