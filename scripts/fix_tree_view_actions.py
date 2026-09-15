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
    
    # 1. Inspeciona Action 2339
    act = env['ir.actions.act_window'].browse(2339)
    if act.exists():
        print(f"=== ACTION 2339 ENCONTRADA ===")
        print(f"ID: {act.id} | Name: {act.name} | Res_Model: {act.res_model} | View_Mode: {act.view_mode}")
        if 'tree' in (act.view_mode or ''):
            new_mode = act.view_mode.replace('tree', 'list')
            act.write({'view_mode': new_mode})
            print(f"CORRIGIDO ACTION 2339 para view_mode: {new_mode}")
    else:
        print("Action 2339 não encontrada como ir.actions.act_window.")

    # 2. Busca todas as actions no banco com 'tree' no view_mode
    actions_with_tree = env['ir.actions.act_window'].search([('view_mode', 'ilike', 'tree')])
    print(f"=== ACTIONS COM 'tree' NO VIEW_MODE (Total: {len(actions_with_tree)}) ===")
    for a in actions_with_tree:
        old_mode = a.view_mode
        new_mode = old_mode.replace('tree', 'list')
        a.write({'view_mode': new_mode})
        print(f"ID: {a.id} | Name: {a.name} | Model: {a.res_model} | {old_mode} -> {new_mode}")

    # 3. Busca view modes em ir.actions.act_window.view com view_mode = 'tree'
    act_views = env['ir.actions.act_window.view'].search([('view_mode', '=', 'tree')])
    print(f"=== ACT WINDOW VIEWS COM view_mode='tree' (Total: {len(act_views)}) ===")
    for av in act_views:
        print(f"ID: {av.id} | Action: {av.act_window_id.name} | View: {av.view_id.name} -> Atualizando para 'list'")
        av.write({'view_mode': 'list'})

    cr.commit()
    print("Atualizações gravadas com sucesso no banco!")
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
print(stdout)
if stderr:
    print('STDERR:', stderr)
