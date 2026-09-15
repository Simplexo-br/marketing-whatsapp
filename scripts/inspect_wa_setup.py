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
    Mailing = env['mailing.mailing']
    
    # Inspecionar contas de whatsapp disponiveis
    Account = env['whatsapp.account']
    accounts = Account.search([])
    print(f"Contas de WhatsApp cadastradas ({len(accounts)}):")
    for a in accounts:
        print(f"  ID: {a.id} | Nome: {a.name} | Status: {a.status} | Phone ID: {a.phone_number_id} | WABA: {a.waba_id}")

    # Inspecionar templates de whatsapp disponiveis
    Template = env['whatsapp.template']
    templates = Template.search([])
    print(f"Templates de WhatsApp cadastrados ({len(templates)}):")
    for t in templates:
        print(f"  ID: {t.id} | Nome: {t.name} | Status: {t.status} | Tipo: {t.template_type} | Conta: {t.account_id.name if t.account_id else 'NENHUMA'}")

    # Testar default_get para mailing_type = 'whatsapp'
    defaults = Mailing.with_context(default_mailing_type='whatsapp').default_get(list(Mailing._fields.keys()))
    print("Defaults de criacao:", {k: v for k, v in defaults.items() if 'whatsapp' in k or k in ['mailing_type', 'subject', 'state', 'mailing_model_id']})
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
