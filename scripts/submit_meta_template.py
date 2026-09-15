# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import os
import requests
import json

token = os.environ.get('META_WHATSAPP_TOKEN', '').strip()
waba_id = "852874847875747"

body_text = (
    "Olá, tudo bem? Se você busca simplificar a rotina da sua empresa, eliminar retrabalho e ter total controle das suas vendas, conheça o Simplexo ERP:\\n\\n"
    "✅ ERP & Gestão Completa: Controle de estoque em tempo real, fluxo de caixa, contas a pagar/receber e relatórios gerenciais inteligentes.\\n"
    "✅ Emissão de Notas Fiscais Automática: Emita NF-e, NFC-e e NFS-e sem complicação e 100% integrado ao faturamento.\\n"
    "✅ Frente de Caixa (PDV Ágil): Ponto de venda ultra-rápido, suporte a leitor de código de barras, TEF/Pix e funcionamento estável.\\n"
    "✅ Aplicativo Força de Vendas: Seus vendedores externos tiram pedidos na rua direto pelo celular (online e offline), consultam estoque e fecham vendas na hora!\\n\\n"
    "📊 Mais de 25.000 empresas e distribuidores já aceleram sua gestão conosco.\\n\\n"
    "👉 Quer ver na prática como o Simplexo se adapta ao seu negócio?\\n\\n"
    "🌐 Acesse: https://simplexo.com.br\\n"
    "📱 Responda 1 para agendar uma demonstração gratuita de 15 minutos!\\n"
    "📱 Responda 2 para cancelar"
)

payload = {
    "name": "simplexo_erp_vendas_pdv_v1",
    "category": "MARKETING",
    "language": "pt_BR",
    "components": [
        {
            "type": "BODY",
            "text": body_text
        }
    ]
}

url = f"https://graph.facebook.com/v20.0/{waba_id}/message_templates"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

resp = requests.post(url, headers=headers, json=payload)
print("Status Code:", resp.status_code)
print("Response:", resp.text)
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace'))
