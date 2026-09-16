# -*- coding: utf-8 -*-
import subprocess
import os
import base64

remote_script = """# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    Dept = env['simplexo.aios.whatsapp.department']
    print("=== DEPARTAMENTOS ===")
    for d in Dept.search([]):
        ai_en = getattr(d, 'ai_enabled', 'N/A')
        ai_prof = getattr(d, 'ai_profile_id', False)
        ai_prof_name = ai_prof.name if ai_prof else 'None'
        ai_prof_state = getattr(ai_prof, 'state', 'N/A') if ai_prof else 'N/A'
        ai_agent = getattr(d, 'ai_agent_id', False)
        ai_agent_name = ai_agent.name if ai_agent else 'None'
        print(f"Dept ID {d.id} | Name: {d.name} | Code: {d.code} | ai_enabled: {ai_en} | ai_profile: {ai_prof_name} (state: {ai_prof_state}) | ai_agent: {ai_agent_name}")

    if 'simplexo.aios.whatsapp.ai.profile' in env:
        print("\\n=== AI PROFILES ===")
        Profile = env['simplexo.aios.whatsapp.ai.profile']
        for p in Profile.search([]):
            print(f"Profile ID {p.id} | Name: {p.name} | State: {getattr(p, 'state', 'N/A')} | allow_auto_reply: {getattr(p, 'allow_auto_reply', 'N/A')} | allow_external_io: {getattr(p, 'allow_external_io', 'N/A')}")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} \"{remote_cmd}\""
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
print(stdout)
if stderr:
    print('STDERR:', stderr)
