# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Checar modelos do simplexo_aios_whatsapp
    for m in ['simplexo.aios.whatsapp.channel', 'simplexo.aios.whatsapp.account', 'whatsapp.account', 'whatsapp.template', 'mailing.mailing']:
        if m in env:
            try:
                cnt = env[m].search_count([])
                print(f"{m}: {cnt} registros")
                for rec in env[m].search([], limit=10):
                    print(f"   [{rec.id}] {rec.display_name}")
            except Exception as e:
                print(f"{m} error: {e}")
                cr.rollback()

    # Checar como o modulo marketing_whatsapp conecta com simplexo_aios_whatsapp
    # ou se existe sincronizacao automatica de contas
    Account = env.get('whatsapp.account')
    if Account is not None:
        print("Campos de whatsapp.account:", list(Account._fields.keys()))
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
stdout, stderr = proc.communicate(input=remote_script, timeout=60)
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print("STDERR:", stderr.encode('ascii', errors='replace').decode('ascii'))
