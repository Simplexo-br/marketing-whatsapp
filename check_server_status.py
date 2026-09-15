# -*- coding: utf-8 -*-
import subprocess
import os
import sys

# Ensure stdout uses utf-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

check_script = """
import subprocess

print("==> Status do Servico odoo-simplexo:")
stat = subprocess.run("sudo systemctl status odoo-simplexo --no-pager", shell=True, capture_output=True, text=True)
print(stat.stdout)

print("==> Verificando instalacao do modulo no Odoo:")
check_cmd = "/opt/odoo/venv/bin/python3 -c \\"import odoo; from odoo import api, SUPERUSER_ID; odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf']); env = api.Environment(odoo.registry('simplexo').cursor(), SUPERUSER_ID, {}); mod = env['ir.module.module'].search([('name', '=', 'marketing_whatsapp')]); print('STATUS DO MODULO MARKETING_WHATSAPP:', mod.state if mod else 'NAO ENCONTRADO')\\""
res = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)
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
