# -*- coding: utf-8 -*-
import subprocess
import os
import base64
import sys

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
import odoo
from odoo import api, SUPERUSER_ID
import json

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Executa a ação do menu de Canais
    res = env['whatsapp.account'].action_open_channels_management()
    print("=== RESPOSTA DA AÇÃO 'Canais & WhatsApp Seguro' ===")
    print("Action retornada:", res)
    
    # Testa serialização JSON (o que a web RPC do Odoo faz)
    json_str = json.dumps(res)
    print("JSON Serializado OK! Tamanho:", len(json_str))
'''

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15',
    '-i', ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
sys.stdout.buffer.write((stdout + "\n").encode('utf-8'))
if stderr:
    sys.stderr.buffer.write((stderr + "\n").encode('utf-8'))
