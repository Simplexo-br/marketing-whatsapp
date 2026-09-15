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
    
    # 1. Modelos que contenham whatsapp
    wa_models = [m for m in env.keys() if 'whatsapp' in m]
    print("Modelos com whatsapp no nome:", wa_models)

    # 2. Verificar simplexo.aios.whatsapp.account se existir
    for m in wa_models:
        try:
            count = env[m].search_count([])
            print(f"Modelo {m}: {count} registros")
            if count > 0 and count < 10:
                for rec in env[m].search([]):
                    print(f"   [{rec.id}] {rec.display_name}")
        except Exception as e:
            print(f"Modelo {m} erro: {e}")

    # 3. Parametros do sistema com whatsapp ou meta
    params = env['ir.config_parameter'].search([
        '|', '|',
        ('key', 'ilike', 'whatsapp'),
        ('key', 'ilike', 'meta'),
        ('key', 'ilike', 'aios')
    ])
    print(f"Parametros do sistema ({len(params)}):")
    for p in params:
        print(f"   {p.key} = {p.value[:60] if p.value else 'Vazio'}...")
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
