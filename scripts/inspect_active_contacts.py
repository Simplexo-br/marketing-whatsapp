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
    active_contacts = Contact.search([('wa_status', '!=', 'not_sent')])
    print(f"Total de contatos com status WhatsApp ativo: {len(active_contacts)}")
    for c in active_contacts[:10]:
        print(f"ID: {c.id} | Nome: {c.name} | Phone: {c.mobile_whatsapp} | Status: {c.wa_status} | Write Date: {c.write_date} | Listas: {c.list_ids.mapped('name')}")
    
    # Checar se ha mailing.trace vinculado a esses contatos
    Trace = env['mailing.trace']
    traces = Trace.search([('contact_id', 'in', active_contacts.ids)])
    print(f"Total de mailing.trace desses contatos: {len(traces)}")
    for tr in traces[:10]:
        print(f"Trace ID: {tr.id} | Mass Mailing: {tr.mass_mailing_id.name if tr.mass_mailing_id else None} | Type: {tr.trace_type} | Sent: {tr.sent_datetime} | Trace status: {tr.trace_status}")
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
