# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
import json
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    acc = env['whatsapp.account'].search([('status', '=', 'connected')], limit=1)
    tmpl = env['whatsapp.template'].search([('name', '=', 'simplexo_gestao_completa_v1')], limit=1)
    mailing = env['mailing.mailing'].search([('mailing_type', '=', 'whatsapp')], limit=1)
    if not mailing:
        mailing = env['mailing.mailing'].create({
            'name': 'Campanha Teste Imagem',
            'subject': 'Campanha Simplexo Imagem',
            'mailing_type': 'whatsapp',
            'whatsapp_account_id': acc.id,
            'whatsapp_template_id': tmpl.id,
        })
    else:
        mailing.write({'whatsapp_template_id': tmpl.id})

    payload = mailing._build_meta_payload(acc, tmpl, '5511999999999', target_record=False)
    print("META PAYLOAD GERADO:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo -E /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=45)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
