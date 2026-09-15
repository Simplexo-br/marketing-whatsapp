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
    c9567 = Contact.browse(9567)
    print("c9567 write_date:", c9567.write_date, "write_uid:", c9567.write_uid.name)
    
    # Check if mailing.trace has contact_id
    Trace = env['mailing.trace']
    print("Trace fields with 'contact':", [f for f in Trace._fields if 'contact' in f])

    # Check if there are other contacts with empty mobile that have wa_status_delivered
    empty_deliv = Contact.search([
        ('mobile_whatsapp', '=', False),
        ('mobile', '=', False),
        ('wa_status_delivered', '=', True)
    ])
    print(f"Total contacts with empty mobile but wa_status_delivered=True: {len(empty_deliv)}")
    for c in empty_deliv[:5]:
        print(f"  ID: {c.id}, Name: {c.name}, email: {c.email}, create_date: {c.create_date}, write_date: {c.write_date}")
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
