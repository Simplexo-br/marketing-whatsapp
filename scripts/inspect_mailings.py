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
    all_mailings = Mailing.search([])
    print(f"Total de registros em mailing.mailing: {len(all_mailings)}")
    for m in all_mailings:
        print(f"ID: {m.id} | Titulo: {m.subject} | Tipo: {m.mailing_type} | Estado: {m.state} | Criado em: {m.create_date} | Total Destinatarios: {m.total}")
        if m.mailing_type == 'whatsapp':
            print(f"   Conta WA: {m.whatsapp_account_id.name if m.whatsapp_account_id else 'NENHUMA'} | Template: {m.whatsapp_template_id.name if m.whatsapp_template_id else 'NENHUM'}")
            print(f"   Model Alvo: {m.mailing_model_id.name if m.mailing_model_id else 'NENHUM'} | Listas: {m.contact_list_ids.mapped('name')}")
            print(f"   Entregues: {m.whatsapp_delivered_count} | Lidos: {m.whatsapp_read_count} | Falhas: {m.whatsapp_failed_count}")

    # Checar se ha filas ou crons de disparo de mailing pendentes
    crons = env['ir.cron'].search([('model_name', '=', 'mailing.mailing')])
    print(f"Crons de mailing.mailing ({len(crons)}):")
    for c in crons:
        print(f"   Cron: {c.name} | Ativo: {c.active} | Proxima execucao: {c.nextcall} | Intervalo: {c.interval_number} {c.interval_type}")
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
