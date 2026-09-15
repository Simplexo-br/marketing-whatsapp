# -*- coding: utf-8 -*-
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
bastion = 'fellipe_ramalho@35.224.220.67'
internal_server = 'fellipe_ramalho@34.45.88.55'

remote_script = '''# -*- coding: utf-8 -*-
import os

for mod in ['simplexo_ai_assistant_aios', 'simplexo_aios_whatsapp_ai', 'simplexo_ai_assistant']:
    mod_path = os.path.join('/opt/odoo/addons', mod)
    if os.path.exists(mod_path):
        print(f"=== ESTRUTURA DO MODULO {mod} ===")
        for root, dirs, files in os.walk(mod_path):
            for f in files:
                if f.endswith('.py') or f.endswith('.xml'):
                    rel = os.path.relpath(os.path.join(root, f), mod_path)
                    print(f"  {rel}")
'''

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3"

cmd = [
    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15',
    '-i', ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
print(stdout)
if stderr:
    print('STDERR:', stderr)
