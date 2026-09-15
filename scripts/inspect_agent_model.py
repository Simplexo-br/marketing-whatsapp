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
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    Agent = env['simplexo.ai.agent']
    print("=== CAMPOS DO MODELO simplexo.ai.agent ===")
    for fname, ffield in sorted(Agent._fields.items()):
        print(f"Campo: {fname} ({ffield.type}) - {ffield.string}")

    print("\\n=== REGISTROS DE AGENTES ATUAIS ===")
    agents = Agent.search([])
    for a in agents:
        print(f"ID: {a.id} | Name: {a.name} | Type/Role: {getattr(a, 'agent_type', getattr(a, 'role', 'N/A'))} | Active: {a.active if hasattr(a, 'active') else 'N/A'}")
        if hasattr(a, 'system_prompt'):
            print(f"   System Prompt (primeiros 200 chars): {str(a.system_prompt)[:200]}")
        if hasattr(a, 'channel_ids'):
            print(f"   Canais vinculados: {a.channel_ids.mapped('name')}")
        if hasattr(a, 'whatsapp_account_ids'):
            print(f"   Contas WhatsApp vinculadas: {a.whatsapp_account_ids.mapped('name')}")

    # Checa modelos relacionados ao fluxo de atendimento de WhatsApp e IA
    print("\\n=== MODELOS AIOS WHATSAPP AI ===")
    ai_models = [m for m in env.registry.keys() if 'simplexo.ai' in m or 'whatsapp.ai' in m or 'customer_care' in m or 'assistant' in m]
    for m in ai_models:
        print(f"- {m}")
'''

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15',
    '-i', ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

p = subprocess.run(cmd, capture_output=True, text=True)
print(p.stdout)
if p.stderr:
    print('STDERR:', p.stderr)
