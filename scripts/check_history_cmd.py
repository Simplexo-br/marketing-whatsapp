# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import os
print("Checking history and scripts...")
os.system("tail -n 50 ~/.bash_history")
print("--- root history ---")
os.system("sudo tail -n 50 /root/.bash_history")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'python3 -c \"{remote_script}\"'"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(timeout=60)
print(stdout)
if stderr:
    print("STDERR:", stderr)
