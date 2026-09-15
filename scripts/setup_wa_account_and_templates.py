# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import os
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 1. Obter empresa Simplexo Tecnologia
    company = env['res.company'].browse(1)
    print(f"Empresa: {company.name} (ID: {company.id})")
    
    # 2. Obter plano Enterprise
    Plan = env['whatsapp.subscription.plan']
    plan_ent = Plan.search([('code', '=', 'enterprise')], limit=1)
    if not plan_ent:
        plan_ent = Plan.search([], limit=1)
    print(f"Plano: {plan_ent.name} (ID: {plan_ent.id})")
    
    # 3. Criar Assinatura se nao existir
    Sub = env['whatsapp.subscription']
    sub = Sub.search([('company_id', '=', company.id)], limit=1)
    if not sub:
        sub = Sub.create({
            'partner_id': company.partner_id.id,
            'company_id': company.id,
            'plan_id': plan_ent.id,
            'state': 'active',
        })
        print(f"Assinatura criada: {sub.name} (ID: {sub.id})")
    else:
        print(f"Assinatura existente: {sub.name} (ID: {sub.id})")
        
    # 4. Criar ou Atualizar Conta de WhatsApp
    token = os.environ.get('META_WHATSAPP_TOKEN', '').strip()
    Account = env['whatsapp.account']
    account = Account.search([('phone_number_id', '=', '1037479776125011')], limit=1)
    if not account:
        account = Account.create({
            'name': 'Simplexo Tecnologia Oficial',
            'company_id': company.id,
            'phone_number': '+55 11 5028-8495',
            'phone_number_id': '1037479776125011',
            'waba_id': '852874847875747',
            'token': token,
        })
        print(f"Conta de WhatsApp criada: {account.name} (ID: {account.id})")
    else:
        print(f"Conta de WhatsApp existente: {account.name} (ID: {account.id})")
        
    # 5. Testar Conexao
    account.action_test_connection()
    print(f"Status da Conta: {account.status} | Qualidade: {account.quality_rating} | Limite: {account.messaging_limit_tier}")
    
    # 6. Sincronizar Templates
    account.action_sync_templates()
    templates = env['whatsapp.template'].search([('account_id', '=', account.id)])
    print(f"Templates sincronizados ({len(templates)}):")
    for t in templates:
        print(f"  [{t.id}] {t.name} | Categoria: {t.category} | Status: {t.status}")
        
    cr.commit()
    print("CONFIGURACAO SALVA COM SUCESSO!")
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
