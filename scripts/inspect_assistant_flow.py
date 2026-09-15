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
    
    # 1. Canais de WhatsApp configurados
    print("=== CANAIS WHATSAPP (simplexo.aios.whatsapp.channel) ===")
    channels = env['simplexo.aios.whatsapp.channel'].search([])
    for ch in channels:
        print(f"ID: {ch.id} | Name: {ch.name} | Phone: {getattr(ch, 'phone_number', 'N/A')} | Provider: {getattr(ch, 'provider', 'N/A')} | Status: {getattr(ch, 'status', 'N/A')} | Default Agent: {getattr(ch, 'default_agent_id', getattr(ch, 'agent_id', 'N/A'))}")
        for f in ['auto_reply', 'ai_enabled', 'agent_id', 'department_id', 'routing_strategy', 'ai_profile_id']:
            if hasattr(ch, f):
                print(f"   {f}: {getattr(ch, f)}")

    # 2. simplexo.aios.whatsapp.ai.profile
    if 'simplexo.aios.whatsapp.ai.profile' in env:
        print("\\n=== PERFIS DE IA WHATSAPP (simplexo.aios.whatsapp.ai.profile) ===")
        profiles = env['simplexo.aios.whatsapp.ai.profile'].search([])
        for p in profiles:
            print(f"ID: {p.id} | Name: {p.name}")
            for f in ['system_prompt', 'prompt', 'model_name', 'temperature', 'active', 'agent_id']:
                if hasattr(p, f):
                    print(f"   {f}: {getattr(p, f)}")

    # 3. Modelos e Arquivos do modulo simplexo_ai_assistant_aios e simplexo_aios_whatsapp_ai
    print("\\n=== DETALHES DOS AGENTES simplexo.ai.agent ===")
    agents = env['simplexo.ai.agent'].search([])
    for a in agents:
        print(f"--- AGENTE ID: {a.id} | {a.name} ---")
        for f in ['agent_type', 'role', 'model_provider', 'model_name', 'active', 'system_prompt', 'is_active', 'temperature']:
            if hasattr(a, f):
                val = getattr(a, f)
                if f == 'system_prompt':
                    print(f"   system_prompt (len {len(str(val))}):\\n{str(val)[:300]}...")
                else:
                    print(f"   {f}: {val}")
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
