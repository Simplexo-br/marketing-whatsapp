# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import os
import requests
import odoo
from odoo import api, SUPERUSER_ID

token = os.environ.get('META_WHATSAPP_TOKEN', '').strip()
tpl_id = "1070897355793002"

url = f"https://graph.facebook.com/v20.0/{tpl_id}"
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(url, headers=headers)
print("Template Status:", resp.json().get('status'))

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    MailingList = env['mailing.list']
    all_lists = MailingList.search([])
    valid_lists = [l for l in all_lists if l.contact_count > 0]
    valid_lists.sort(key=lambda x: x.contact_count, reverse=True)
    print(f"Total de listas com contatos válidos: {len(valid_lists)}")
    for l in valid_lists:
        print(f"  ID: {l.id} | Nome: {l.name} | Contatos: {l.contact_count}")
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
