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
    mod = env['ir.module.module'].search([('name', '=', 'marketing_whatsapp')])
    print(f"Status do Modulo: {mod.name} | Estado: {mod.state} | Versao Instalada: {mod.installed_version}")
    
    Contact = env['mailing.contact']
    total_contacts = Contact.search_count([])
    no_phone = Contact.search_count([('mobile_whatsapp', '=', False), ('mobile', '=', False)])
    wa_active = Contact.search_count([('wa_status', '!=', 'not_sent')])
    
    print(f"Total de contatos no Odoo: {total_contacts}")
    print(f"Contatos sem telefone: {no_phone}")
    print(f"Contatos com status WhatsApp ativo: {wa_active}")
    
    # Testar se a Server Action esta registrada
    action = env['ir.actions.server'].search([('name', 'ilike', 'Higienizar Base')])
    print(f"Server Action de Higienizacao registrada: {action.name if action else 'NAO ENCONTRADA'}")
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
