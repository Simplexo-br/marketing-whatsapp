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
    # Check conversation messages or contacts
    if 'simplexo.aios.whatsapp.conversation' in env:
        Conv = env['simplexo.aios.whatsapp.conversation']
        for conv in Conv.search([]):
            phone = conv.customer_phone or conv.customer_wa_id
            print(f"Conv ID: {conv.id}, customer_phone: {conv.customer_phone}, customer_wa_id: {conv.customer_wa_id}")
            # check messages in conv
            msgs = conv.message_ids
            print(f"   Msgs count: {len(msgs)}")
            for m in msgs[:3]:
                print(f"     msg id: {m.id}, dir: {m.direction}, state: {m.state}, to: {getattr(m, 'to', '')}, from: {getattr(m, 'from_phone', '')}")
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
