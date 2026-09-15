# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import subprocess
res = subprocess.run("sudo -u simplexo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /opt/odoo/conf/simplexo.conf -d simplexo --test-enable --test-tags /marketing_whatsapp --no-http --stop-after-init --log-level=test", shell=True, capture_output=True, text=True)
print("Returncode:", res.returncode)
lines = (res.stderr or res.stdout or "").splitlines()
for line in lines[-50:]:
    print(line)
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
stdout, stderr = proc.communicate(input=remote_script, timeout=120)
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print("STDERR:", stderr.encode('ascii', errors='replace').decode('ascii'))
