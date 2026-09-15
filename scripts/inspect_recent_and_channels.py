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
    
    # 1. Inspecionar os 15 mailings mais recentes
    Mailing = env['mailing.mailing']
    recent = Mailing.search([], order='id desc', limit=15)
    print("Ultimos 15 mailings criados:")
    for m in recent:
        print(f"ID: {m.id} | Titulo: {m.subject} | Tipo: {m.mailing_type} | Estado: {m.state} | Criado: {m.create_date} | Total: {m.total}")
        if hasattr(m, 'whatsapp_account_id'):
            print(f"   whatsapp_account_id: {m.whatsapp_account_id.id if m.whatsapp_account_id else None}")
            print(f"   whatsapp_template_id: {m.whatsapp_template_id.id if m.whatsapp_template_id else None}")

    # 2. Inspecionar os canais do simplexo.aios.whatsapp.channel
    Channel = env['simplexo.aios.whatsapp.channel']
    for c in Channel.search([]):
        print(f"Canal ID {c.id}: {c.name} | Provider: {getattr(c, 'provider', None)} | Type: {getattr(c, 'channel_type', None)}")
        fields_to_check = ['phone_number', 'phone_number_id', 'waba_id', 'token', 'access_token', 'status', 'active']
        for f in fields_to_check:
            if hasattr(c, f):
                val = getattr(c, f)
                if f in ['token', 'access_token'] and val:
                    val = val[:15] + '...' + val[-10:]
                print(f"   {f}: {val}")
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
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print("STDERR:", stderr.encode('ascii', errors='replace').decode('ascii'))
