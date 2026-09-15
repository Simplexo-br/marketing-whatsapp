# -*- coding: utf-8 -*-
import subprocess
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

install_script = """
import subprocess

print("==> 1. Parando servico odoo-simplexo...")
subprocess.run("sudo systemctl stop odoo-simplexo", shell=True)

print("==> 2. Executando instalacao do modulo marketing_whatsapp no banco simplexo...")
cmd = "sudo PYTHONPATH=/opt/odoo/odoo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /opt/odoo/conf/simplexo.conf -d simplexo -i marketing_whatsapp --stop-after-init --log-level=info"
p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("Codigo de retorno:", p.returncode)
for line in p.stdout.splitlines():
    if "marketing_whatsapp" in line or "CRITICAL" in line or "ERROR" in line or "odoo.modules.loading: 1 modules loaded" in line or "loading" in line:
        print(line)

print("==> 3. Iniciando servico odoo-simplexo...")
subprocess.run("sudo systemctl start odoo-simplexo", shell=True)

print("==> 4. Status do servico:")
stat = subprocess.run("sudo systemctl status odoo-simplexo --no-pager", shell=True, capture_output=True, text=True)
print(stat.stdout[:500])
"""

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=install_script, timeout=120)

print(stdout)
if stderr:
    print("STDERR:", stderr)
