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
    
    # Verificar se Conta e Templates estao acessiveis para criacao de mailing
    Account = env['whatsapp.account']
    Template = env['whatsapp.template']
    account = Account.search([], limit=1)
    templates = Template.search([('account_id', '=', account.id)])
    print(f"Conta padrao: {account.name} (ID: {account.id})")
    print(f"Total de templates disponiveis: {len(templates)}")
    
    # Testar criacao de um mailing WhatsApp em RASCUNHO (Draft)
    Mailing = env['mailing.mailing']
    test_draft = Mailing.create({
        'subject': 'Exemplo / Rascunho de Campanha WhatsApp',
        'mailing_type': 'whatsapp',
        'whatsapp_account_id': account.id,
        'whatsapp_template_id': templates[0].id if templates else False,
        'state': 'draft',
    })
    print(f"Mailing criado com sucesso em Rascunho! ID: {test_draft.id} | Titulo: {test_draft.subject} | Estado: {test_draft.state}")
    cr.commit()
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo -E /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=60)
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print("STDERR:", stderr.encode('ascii', errors='replace').decode('ascii'))
