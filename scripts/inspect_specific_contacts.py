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
    Trace = env['mailing.trace']
    
    for cid in [7438, 9567, 38871, 34247]:
        c = Contact.browse(cid)
        if c.exists():
            print(f"Contact {cid}: Name='{c.name}', email='{c.email}', mobile='{c.mobile}', wa='{c.mobile_whatsapp}', list_ids={c.list_ids.mapped('name')}")
            traces = Trace.search([('res_id', '=', cid)])
            print(f"  Traces directly on res_id={cid}: {len(traces)}")
            for tr in traces:
                print(f"    Trace ID {tr.id}: type={tr.trace_type}, status={tr.whatsapp_status}, phone={tr.whatsapp_recipient_number}")

    # Check if there are other contacts with name ANTONIO FELIPE DE MENEZES
    af_contacts = Contact.search([('name', 'ilike', 'ANTONIO FELIPE DE MENEZES')])
    print(f"All contacts with name ANTONIO FELIPE DE MENEZES: {len(af_contacts)}")
    for c in af_contacts:
        print(f"  ID: {c.id} | mobile: {c.mobile} | wa: {c.mobile_whatsapp} | status: {c.wa_status} | sent: {c.wa_status_sent} | deliv: {c.wa_status_delivered} | read: {c.wa_status_read} | lists: {c.list_ids.mapped('name')}")
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
