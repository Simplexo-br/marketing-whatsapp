# -*- coding: utf-8 -*-
import subprocess
import os
import sys

# Ensure stdout uses utf-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"
import base64

remote_code = '''# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID, fields

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    data = env['whatsapp.dashboard'].get_dashboard_data('all')
    import pprint
    print("=== DADOS DO DASHBOARD DE MARKETING WHATSAPP ===")
    pprint.pprint(data)

'''

b64_code = base64.b64encode(remote_code.encode('utf-8')).decode('ascii')
check_script = f"echo '{b64_code}' | base64 -d | sudo /opt/odoo/venv/bin/python3 -"


cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "sed -i \'\' 2>/dev/null || true; python3 -c \\"import sys, subprocess; subprocess.run([\'bash\'], input=sys.stdin.read().replace(\'\\\\r\', \'\'), text=True)\\""'
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
stdout, stderr = proc.communicate(input=check_script.encode('utf-8'), timeout=180)

print(stdout.decode('utf-8', errors='replace'))
if stderr:
    print("STDERR:", stderr.decode('utf-8', errors='replace'))
