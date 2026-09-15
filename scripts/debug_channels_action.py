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
    
    # 1. Testa a chamada action_open_channels_management
    print("=== TESTANDO action_open_channels_management ===")
    try:
        res = env['whatsapp.account'].action_open_channels_management()
        print(f"Resultado: {res}")
        
        # Inspeciona a action retornada
        act_id = res.get('id')
        if act_id:
            act = env['ir.actions.act_window'].browse(act_id)
            print(f"Action ID: {act.id} | Name: {act.name} | Res_Model: {act.res_model} | View_Mode: {act.view_mode}")
            
            # Testa carregar as views da action
            ChannelModel = env[act.res_model]
            print(f"Total registros em {act.res_model}: {ChannelModel.search_count([])}")
            
            # Testa get_views
            views_info = ChannelModel.get_views([(False, 'kanban'), (False, 'list'), (False, 'form')])
            print("get_views executou com SUCESSO!")
    except Exception as e:
        import traceback
        print("ERRO AO EXECUTAR:")
        traceback.print_exc()

    # 2. Inspeciona a action simplexo_aios_whatsapp.action_aios_whatsapp_channels
    ref_act = env.ref('simplexo_aios_whatsapp.action_aios_whatsapp_channels', raise_if_not_found=False)
    if ref_act:
        print(f"\\n=== REF ACTION simplexo_aios_whatsapp.action_aios_whatsapp_channels ===")
        print(f"ID: {ref_act.id} | Name: {ref_act.name} | Res_Model: {ref_act.res_model} | View_Mode: {ref_act.view_mode}")
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
