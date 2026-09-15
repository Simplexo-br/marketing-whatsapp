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
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo.tools import config

config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf'])
registry = odoo.registry('simplexo')

with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    mod = env['ir.module.module'].search([('name', '=', 'marketing_whatsapp')])
    if mod:
        print(f"==> Instalando modulo {mod.name} ({mod.shortdesc})...")
        mod.button_immediate_install()
        cr.commit()
        print(f"==> Modulo instalado com sucesso! Novo estado: {mod.state}")
    else:
        print("==> Modulo nao encontrado!")
"""

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=install_script, timeout=120)

if stdout:
    print(stdout.encode("ascii", errors="replace").decode("ascii"))
if stderr:
    print("STDERR:", stderr.encode("ascii", errors="replace").decode("ascii"))
