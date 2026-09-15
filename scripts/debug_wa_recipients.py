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
    recipients = m._get_recipients()
    sample = recipients[:5]
    for r in sample:
        print(f"ID: {r.id} | Name: {r.name}")
        print(f"  has mobile_whatsapp: {hasattr(r, 'mobile_whatsapp')} ({getattr(r, 'mobile_whatsapp', None)})")
        print(f"  has mobile: {hasattr(r, 'mobile')} ({getattr(r, 'mobile', None)})")
        print(f"  has phone: {hasattr(r, 'phone')} ({getattr(r, 'phone', None)})")
        
        # Test sanitize
        phone_raw = r.mobile_whatsapp or r.mobile or False
        sanitized = env['mailing.contact']._sanitize_whatsapp_number(
            phone_raw,
            getattr(r, 'country_id', False) and r.country_id.code or 'BR'
        )
        print(f"  phone_raw: {phone_raw} => sanitized: {sanitized}")
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
