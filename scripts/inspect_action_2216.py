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
    
    # 1. Busca Action 2216
    action = env['ir.actions.act_window'].browse(2216)
    if action.exists():
        print(f"=== ACTION 2216 ===")
        print(f"ID: {action.id} | Name: {action.name} | Res_Model: {action.res_model} | View_Mode: {action.view_mode} | Domain: {action.domain} | Context: {action.context}")
    else:
        # Busca por id genérico em ir.actions.actions
        act_gen = env['ir.actions.actions'].browse(2216)
        print(f"=== ACTION GEN 2216 ===")
        print(f"ID: {act_gen.id} | Name: {act_gen.name} | Type: {act_gen.type}")

    # 2. Busca módulos relacionados a AIOS / Assistente / Atendente
    modules = env['ir.module.module'].search([('name', 'ilike', 'aios'), ('state', '=', 'installed')])
    print("=== MÓDULOS AIOS INSTALADOS ===")
    for m in modules:
        print(f"Modulo: {m.name} | Shortdesc: {m.shortdesc}")

    # 3. Modelos de Assistente / Atendente / Agent
    assistant_models = [m for m in env.models.keys() if 'assistant' in m or 'agent' in m or 'bot' in m or 'aios' in m]
    print("=== MODELOS RELACIONADOS ===")
    for m in sorted(assistant_models):
        print(f"- {m}")
        
    # 4. Registros existentes no modelo da action 2216 se existir
    if action.exists() and action.res_model:
        recs = env[action.res_model].search([])
        print(f"=== REGISTROS EM {action.res_model} (Total: {len(recs)}) ===")
        for r in recs:
            disp_name = getattr(r, 'name', str(r.id))
            print(f"ID: {r.id} | Nome: {disp_name}")
            # Campos do modelo
            for f_name, f_obj in r._fields.items():
                if f_name in ['name', 'system_prompt', 'prompt', 'model', 'role', 'temperature', 'channel_id', 'active', 'is_active', 'provider', 'type']:
                    print(f"   {f_name}: {getattr(r, f_name, None)}")
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
