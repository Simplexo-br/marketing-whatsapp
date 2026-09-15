# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import base64

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

updated_body_text = (
    "🚀 *Sua Empresa Pronta para Vender Mais, Emitir Notas e Conquistar Clientes no WhatsApp!*\n\n"
    "Olá, tudo bem? Se você busca simplificar a rotina da sua empresa, eliminar retrabalho e acelerar suas vendas, conheça o *Simplexo ERP*:\n\n"
    "✅ *ERP & Gestão Completa:* Controle de estoque em tempo real, fluxo de caixa, contas a pagar/receber e relatórios inteligentes.\n"
    "✅ *Emissão de Notas Fiscais Automática:* Emita NF-e, NFC-e e NFS-e sem complicação e 100% integrado ao faturamento.\n"
    "✅ *Frente de Caixa (PDV Ágil):* Ponto de venda ultra-rápido com TEF, Pix integrado e estabilidade total.\n"
    "✅ *Aplicativo Força de Vendas:* Seus vendedores tiram pedidos na rua pelo celular (online/offline) e fecham negócios na hora!\n"
    "✅ *Marketing WhatsApp Integrado:* Conquiste mais clientes e fidelize sua base com campanhas de WhatsApp em massa oficiais, com métricas de entrega, leitura e proteção anti-bloqueio!\n\n"
    "📊 *Mais de 25.000 empresas e distribuidores já aceleram sua gestão conosco.*\n\n"
    "👉 *Quer ver na prática como o Simplexo se adapta ao seu negócio?*\n\n"
    "🌐 *Acesse:* https://simplexo.com.br\n"
    "📱 *Responda 1* para falar com um consultor ou agendar uma demonstração gratuita de 15 minutos!\n"
    "🚫 *Responda 2* para não receber mais mensagens.\n\n"
    "*Simplexo Tecnologia — Simples, Inteligente e Escalável.*"
)

remote_python = f'''# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
body_text = """{updated_body_text}"""

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {{}})
    if 'whatsapp.template' in env:
        for t in env['whatsapp.template'].search([]):
            t.write({{'body_text': body_text}})
            print("Template ID:", t.id, t.name)
    if 'simplexo.aios.whatsapp.template' in env:
        for at in env['simplexo.aios.whatsapp.template'].search([]):
            at.write({{'body_preview': body_text}})
            print("AIOS Template ID:", at.id, at.name)
    cr.commit()
print("FINALIZADO_SUCESSO")
'''

b64_code = base64.b64encode(remote_python.encode('utf-8')).decode('ascii')
check_script = f"echo '{b64_code}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{check_script}"'
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
stdout, stderr = proc.communicate(timeout=60)

print(stdout.decode('utf-8', errors='replace'))
if stderr:
    print("STDERR:", stderr.decode('utf-8', errors='replace'))

