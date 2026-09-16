# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import subprocess

print("=== NGINX ACCESS LOGS (WHATSAPP/WEBHOOK) ===")
res = subprocess.run("grep -i 'webhook' /var/log/nginx/access.log | tail -n 20", shell=True, capture_output=True, text=True)
print(res.stdout)
if not res.stdout:
    print("Nenhum webhook recente em /var/log/nginx/access.log")

print("=== VERIFICANDO OUTROS LOGS NGINX ===")
res2 = subprocess.run("tail -n 20 /var/log/nginx/access.log", shell=True, capture_output=True, text=True)
print(res2.stdout)
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
