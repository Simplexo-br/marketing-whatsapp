# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import subprocess

cmd = "grep -rnE 'simplexo\\.ai\\.agent|action_generate_reply|generate_reply|ai_agent' /opt/odoo/addons/simplexo_aios_whatsapp /opt/odoo/addons/marketing_whatsapp /opt/odoo/addons/simplexo_ai"
p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
print("Ocorrências de AI Agent:")
print(p.stdout[:3000])
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=20)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
