# -*- coding: utf-8 -*-
import subprocess
import os
import base64

remote_script = """# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print("=== CONTAS WHATSAPP (whatsapp.account) ===")
    if 'whatsapp.account' in env:
        for acc in env['whatsapp.account'].search([]):
            print(f"ID: {acc.id} | Name: {acc.name} | Phone UID: {getattr(acc, 'phone_uid', 'N/A')} | Account UID: {getattr(acc, 'account_uid', 'N/A')}")
            
    print("\\n=== CANAIS AIOS (simplexo.aios.whatsapp.channel) ===")
    if 'simplexo.aios.whatsapp.channel' in env:
        for ch in env['simplexo.aios.whatsapp.channel'].search([]):
            print(f"ID: {ch.id} | Name: {ch.name} | Provider: {ch.provider} | Status: {ch.status}")
            for f in ['phone_number_id', 'waba_id', 'business_account_id']:
                if hasattr(ch, f):
                    print(f"   {f}: {getattr(ch, f)}")

    # Verificar também se a campanha 134 ainda está disparando ou se já parou/concluiu
    print("\\n=== STATUS CAMPANHA 134 ===")
    m = env['mailing.mailing'].browse(134)
    print(f"Campanha 134 - Estado: {m.state} | Total: {m.total} | Enviados: {m.sent} | Pendentes/Canceled: {m.canceled} | Falhas: {m.failed}")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} \"{remote_cmd}\""
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print('STDERR:', stderr.encode('ascii', errors='replace').decode('ascii'))
