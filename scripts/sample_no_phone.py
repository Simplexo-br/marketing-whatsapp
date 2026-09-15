# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contact = env['mailing.contact']
    
    all_contacts = Contact.search([])
    no_phone = []
    
    for c in all_contacts:
        raw = c.mobile_whatsapp or c.mobile or getattr(c, 'phone', False)
        digits = ''.join(ch for ch in str(raw) if ch.isdigit()) if raw else ''
        if len(digits) < 8:
            no_phone.append(c)

    print(f"Sample no-phone contacts (total {len(no_phone)}):")
    for c in no_phone[:15]:
        print(f"ID {c.id}: name='{c.name}', email='{c.email}', mobile='{c.mobile}', wa='{c.mobile_whatsapp}', company='{c.company_name}', list_ids={c.list_ids.mapped('name')}")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=60)
print(stdout)
if stderr:
    print("STDERR:", stderr)
