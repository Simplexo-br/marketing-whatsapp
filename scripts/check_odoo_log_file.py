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

remote_cmd = "sudo cat /opt/odoo/conf/simplexo.conf | grep logfile; sudo tail -n 80 $(sudo cat /opt/odoo/conf/simplexo.conf | grep logfile | cut -d '=' -f2 | tr -d ' ') 2>/dev/null"

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
