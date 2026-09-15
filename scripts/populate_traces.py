# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    Account = env['whatsapp.account']
    account = Account.search([], limit=1)
    
    Template = env['whatsapp.template']
    template = Template.search([('name', '=', 'simplexo_erp_vendas_pdv_v1')], limit=1)
    
    Mailing = env['mailing.mailing']
    campaign_title = "🚀 Sua Empresa Pronta para Vender Mais e Emitir Notas em Segundos!"
    
    campaign = Mailing.search([
        ('subject', '=', campaign_title),
        ('mailing_type', '=', 'whatsapp')
    ], limit=1)
    
    if not campaign:
        raise Exception("Campanha não encontrada!")
        
    print(f"Campanha ID: {campaign.id} | Estado atual: {campaign.state}")
    
    # Gerar traces da fila de disparo
    campaign._create_whatsapp_traces()
    
    Trace = env['mailing.trace']
    traces = Trace.search([('mass_mailing_id', '=', campaign.id)])
    print(f"Traces gerados com sucesso: {len(traces)}")
    print(f"Status dos traces: outgoing={len(traces.filtered(lambda t: t.whatsapp_status == 'outgoing'))}")
    
    if campaign.state != 'in_queue':
        campaign.write({'state': 'in_queue'})
    print(f"Estado final da campanha: {campaign.state}")
    
    cr.commit()
    print("CONCLUÍDO COM SUCESSO!")
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=180)
print(stdout_bytes.decode('utf-8', errors='replace'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace'))
