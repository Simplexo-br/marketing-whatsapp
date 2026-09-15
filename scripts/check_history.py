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
    # Check mail.tracking.value or mail.message for c9567
    c9567 = env['mailing.contact'].browse(9567)
    print("Messages on 9567:", c9567.message_ids.mapped('body'))
    print("Trackings on 9567:", c9567.message_ids.mapped('tracking_value_ids'))
    for m in c9567.message_ids:
        print(f"Msg: author={m.author_id.name}, date={m.date}, subtype={m.subtype_id.name}")
        for t in m.tracking_value_ids:
            print(f"  Field: {t.field_desc}: {t.old_value_char or t.old_value_integer} -> {t.new_value_char or t.new_value_integer}")
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
