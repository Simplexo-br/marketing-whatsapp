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
    
    ch = env['simplexo.aios.whatsapp.channel'].browse(3)
    print("=== CANAL 3 (+55 11 5028-8495) ===")
    print("Name:", ch.name)
    print("Phone:", ch.phone_number)
    print("enable_welcome_routing:", getattr(ch, 'enable_welcome_routing', 'N/A'))
    print("welcome_header:", getattr(ch, 'welcome_header', 'N/A'))
    print("welcome_button_text:", getattr(ch, 'welcome_button_text', 'N/A'))
    print("welcome_message_body:", repr(getattr(ch, 'welcome_message_body', 'N/A')))
    print("dept_1_id:", getattr(ch, 'dept_1_id', False) and (ch.dept_1_id.id, ch.dept_1_id.name))
    print("dept_2_id:", getattr(ch, 'dept_2_id', False) and (ch.dept_2_id.id, ch.dept_2_id.name))
    print("dept_3_id:", getattr(ch, 'dept_3_id', False) and (ch.dept_3_id.id, ch.dept_3_id.name))
    print("dept_4_id:", getattr(ch, 'dept_4_id', False) and (ch.dept_4_id.id, ch.dept_4_id.name))

    print("\\n=== DEPARTAMENTOS EXISTENTES ===")
    for d in env['simplexo.aios.whatsapp.department'].search([]):
        print(f"ID: {d.id} | Code: {d.code} | Name: {d.name}")
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
