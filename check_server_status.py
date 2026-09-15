# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import base64

# Ensure stdout uses utf-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

with open("marketing_whatsapp/views/menus.xml", "rb") as f:
    content = f.read()

b64_file = base64.b64encode(content).decode('ascii')

remote_cmd = f'''
echo "{b64_file}" | base64 -d | sudo tee /opt/odoo/addons/marketing_whatsapp/views/menus.xml > /dev/null
sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /opt/odoo/conf/simplexo.conf -d simplexo -u marketing_whatsapp --stop-after-init --no-http
sudo systemctl restart odoo-simplexo.service
echo "DEPLOY_CORRETO_CONCLUIDO_SUCESSO"
'''

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = proc.communicate(timeout=120)
print(stdout)
if stderr:
    print("STDERR:", stderr)

