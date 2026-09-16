# -*- coding: utf-8 -*-
import subprocess
import os

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

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=25)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
