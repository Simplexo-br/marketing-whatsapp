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
    
    Cron = env['ir.cron']
    crons = Cron.search(['|', '|', '|',
        ('name', 'ilike', 'whatsapp'),
        ('name', 'ilike', 'marketing'),
        ('name', 'ilike', 'mail'),
        ('model_name', 'ilike', 'mailing')
    ])
    
    print("=== CRONS ENCONTRADOS (MARKETING / WHATSAPP / MAILING) ===")
    for c in crons:
        print(f"ID: {c.id} | Name: {c.name}")
        print(f"   Model: {c.model_name} | Method: {c.code}")
        print(f"   Active: {c.active} | Interval: every {c.interval_number} {c.interval_type}")
        print(f"   Next Call: {c.nextcall} | Number of Calls: {c.numbercall}")
        print("-" * 50)
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
print(stdout)
if stderr:
    print('STDERR:', stderr)
