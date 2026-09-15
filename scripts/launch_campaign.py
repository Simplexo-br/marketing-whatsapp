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
    if not template:
        raise Exception("Template simplexo_erp_vendas_pdv_v1 não encontrado!")
        
    MailingList = env['mailing.list']
    all_valid_lists = MailingList.search([('contact_count', '>', 0)])
    print(f"Listas selecionadas: {len(all_valid_lists)}")
    
    Mailing = env['mailing.mailing']
    campaign_title = "🚀 Sua Empresa Pronta para Vender Mais e Emitir Notas em Segundos!"
    
    # Verificar se já existe uma campanha com este título
    existing_campaign = Mailing.search([
        ('subject', '=', campaign_title),
        ('mailing_type', '=', 'whatsapp')
    ], limit=1)
    
    if existing_campaign:
        campaign = existing_campaign
        print(f"Campanha já existente encontrada (ID: {campaign.id}, Estado: {campaign.state})")
    else:
        campaign = Mailing.create({
            'subject': campaign_title,
            'mailing_type': 'whatsapp',
            'whatsapp_account_id': account.id,
            'whatsapp_template_id': template.id,
            'mailing_model_id': env['ir.model']._get_id('mailing.list'),
            'contact_list_ids': [(6, 0, all_valid_lists.ids)],
            'state': 'draft',
        })
        print(f"Campanha criada com sucesso! ID: {campaign.id}")
        
    # Colocar na fila de disparo (action_put_in_queue)
    if campaign.state == 'draft':
        campaign.action_put_in_queue()
        print(f"Campanha colocada na fila de disparo com sucesso! Estado: {campaign.state}")
    
    # Contar traces gerados
    Trace = env['mailing.trace']
    traces = Trace.search([('mass_mailing_id', '=', campaign.id)])
    print(f"Total de destinatários / traces gerados para a campanha: {len(traces)}")
    print(f"Status dos traces: outgoing={len(traces.filtered(lambda t: t.whatsapp_status == 'outgoing'))}, sent={len(traces.filtered(lambda t: t.whatsapp_status == 'sent'))}")
    
    cr.commit()
    print("TRANSAÇÃO CONFIRMADA NO BANCO DE DADOS!")
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=120)
print(stdout_bytes.decode('utf-8', errors='replace'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace'))
