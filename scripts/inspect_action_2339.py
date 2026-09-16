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

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    act = env['ir.actions.act_window'].browse(2339)
    if act.exists():
        print("=== ACTION 2339 ===")
        print("Name:", act.name)
        print("Model:", act.res_model)
        print("View Mode:", act.view_mode)
        print("Views:", act.views)
        print("View IDs:", act.view_ids.mapped(lambda v: (v.id, v.view_mode, v.sequence)))
        
        # Garante que seja list,form
        act.write({
            'view_mode': 'list,form'
        })
        for v in act.view_ids:
            if v.view_mode == 'tree':
                v.write({'view_mode': 'list'})
                
        print("Após write -> View Mode:", act.view_mode, "Views:", act.views)

    # Busca qualquer outra action com 'tree' no banco
    actions_with_tree = env['ir.actions.act_window'].search([('view_mode', 'ilike', 'tree')])
    print(f"=== ACTIONS COM 'tree' NO BANCO (Total: {len(actions_with_tree)}) ===")
    for a in actions_with_tree:
        print(f"Action ID {a.id}: {a.name} ({a.res_model}) -> {a.view_mode}")
        a.write({'view_mode': a.view_mode.replace('tree', 'list')})

    # Busca qualquer act_window_view com view_mode = 'tree'
    aw_views = env['ir.actions.act_window.view'].search([('view_mode', '=', 'tree')])
    print(f"=== ACT WINDOW VIEWS COM view_mode='tree' (Total: {len(aw_views)}) ===")
    for av in aw_views:
        print(f"AW View ID {av.id}: Action {av.act_window_id.name} -> alterando para 'list'")
        av.write({'view_mode': 'list'})

    cr.commit()
    print("Commit realizado com sucesso!")
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
