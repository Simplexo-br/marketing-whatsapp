# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import subprocess
res = subprocess.run("sudo -u simplexo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /opt/odoo/conf/simplexo.conf -d simplexo -u marketing_whatsapp --stop-after-init --no-http", shell=True, capture_output=True, text=True)
print("Returncode:", res.returncode)
print("Stdout:", res.stdout[-2000:] if res.stdout else "EMPTY")
print("Stderr:", res.stderr[-2000:] if res.stderr else "EMPTY")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=90)
print(stdout)
if stderr:
    print("STDERR:", stderr)
