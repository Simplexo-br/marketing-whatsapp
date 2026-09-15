# -*- coding: utf-8 -*-
import subprocess
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

check_script = """
import subprocess

print("==> Verificando arquivos em /opt/odoo/addons/marketing_whatsapp:")
p1 = subprocess.run("ls -la /opt/odoo/addons/marketing_whatsapp", shell=True, capture_output=True, text=True)
print(p1.stdout)

print("==> Testando importacao do modulo via script python:")
test_code = '''
import odoo
from odoo.tools import config
config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf'])
from odoo.modules.module import get_module_path
print("Caminho do marketing_whatsapp:", get_module_path("marketing_whatsapp"))
'''
p2 = subprocess.run("sudo /opt/odoo/venv/bin/python3 -c \\"" + test_code + "\\"", shell=True, capture_output=True, text=True)
print("Stdout:", p2.stdout)
print("Stderr:", p2.stderr)
"""

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=check_script, timeout=60)

print(stdout)
if stderr:
    print("STDERR:", stderr)
