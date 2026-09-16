# -*- coding: utf-8 -*-
remote_script = """# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
db = odoo.sql_db.db_connect('simplexo')
with db.cursor() as cr:
    ids = [24373, 26193, 22573, 22568, 24019, 25551, 23039]
    print("=== VERIFYING UPDATED MAILING CONTACTS ===")
    cr.execute("SELECT id, name, wa_status, wa_status_opt_out, wa_opt_out_date FROM mailing_contact WHERE id = ANY(%s)", [ids])
    for r in cr.fetchall():
        print("  Contact:", r)

    print("\\n=== VERIFYING SUBSCRIPTIONS ===")
    cr.execute("SELECT contact_id, opt_out, opt_out_datetime FROM mailing_subscription WHERE contact_id = ANY(%s)", [ids])
    for r in cr.fetchall():
        print("  Subscription:", r)
"""

import subprocess
import os
import base64

default_keys = [
    os.environ.get('SIMPLEXO_SSH_KEY'),
    os.path.expanduser('~/.ssh/simplexo_vm'),
    os.path.expanduser('~/.ssh/simplexo_gpt_desktop'),
    r'C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm',
]
ssh_key = next((k for k in default_keys if k and os.path.exists(k)), default_keys[-1])
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

import base64
b64_script = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')

remote_cmd = f'''
echo "{b64_script}" | base64 -d | sudo tee /tmp/check_nandia.py > /dev/null
sudo /opt/odoo/venv/bin/python3 /tmp/check_nandia.py
'''

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(timeout=60)
print("=== STDOUT ===")
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("=== STDERR ===")
    print(stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
