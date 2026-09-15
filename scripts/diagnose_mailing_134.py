# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Mailing = env['mailing.mailing']
    m = Mailing.browse(134)
    print(f"Mailing 134:")
    print(f"mailing_model_id: {m.mailing_model_id.model} ({m.mailing_model_id.id})")
    print(f"mailing_model_real: {m.mailing_model_real}")
    print(f"mailing_domain: {m.mailing_domain}")
    print(f"contact_list_ids count: {len(m.contact_list_ids)}")
    recipients = m._get_recipients()
    print(f"_get_recipients: {len(recipients)}")
    wa_recipients = m._get_whatsapp_recipients()
    print(f"_get_whatsapp_recipients: {len(wa_recipients)}")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo -E /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace'))
