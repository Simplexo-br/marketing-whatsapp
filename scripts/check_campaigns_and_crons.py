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
    
    # 1. Campanhas
    print("=== CAMPANHAS DE MARKETING WHATSAPP ===")
    mailings = env['mailing.mailing'].search([('mailing_type', '=', 'whatsapp')], order='id desc', limit=5)
    for m in mailings:
        subj = m.subject.encode('ascii', errors='replace').decode('ascii') if m.subject else ''
        print(f"ID: {m.id} | Titulo: {subj} | Estado: {m.state}")
        print(f"   Total traces: {m.total} | Enviados: {m.sent} | Entregues: {m.delivered} | Falhas: {m.failed} | Canceled: {m.canceled}")
        if hasattr(m, 'is_paused'):
            print(f"   Pausada: {m.is_paused}")
        if hasattr(m, 'schedule_date'):
            print(f"   Schedule Date: {m.schedule_date}")

    # 2. Status dos Crons do Marketing WhatsApp
    print("\\n=== CRONS DO MARKETING WHATSAPP ===")
    crons = env['ir.cron'].search([('name', 'ilike', 'Marketing WhatsApp')])
    for c in crons:
        print(f"ID: {c.id} | Ativo: {c.active} | Intervalo: a cada {c.interval_number} {c.interval_type}")
        print(f"   Nome: {c.name.encode('ascii', errors='replace').decode('ascii')}")
        print(f"   Proxima Execucao: {c.nextcall}")
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
