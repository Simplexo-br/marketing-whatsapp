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
    mailing = env['mailing.mailing'].browse(134)
    print("Campanha:", mailing.name or mailing.subject, "| Estado atual:", mailing.state)
    print("Template associado:", mailing.whatsapp_template_id.name, "| Status:", mailing.whatsapp_template_id.status)

    # Pegar 1 trace que falhou para testar o envio
    failed_trace = env['mailing.trace'].search([
        ('mass_mailing_id', '=', mailing.id),
        ('whatsapp_status', '=', 'failed')
    ], limit=1)

    if not failed_trace:
        print("Nenhum trace com falha encontrado!")
        sys.exit(0)

    print(f"Testando reenvio para o trace ID {failed_trace.id}, Destinatario: {failed_trace.whatsapp_recipient_number}...")
    
    # Preparar chamada direta na Meta
    account = mailing.whatsapp_account_id
    template = mailing.whatsapp_template_id
    clean_digits = ''.join(c for c in failed_trace.whatsapp_recipient_number if c.isdigit())
    target_record = env[failed_trace.model].browse(failed_trace.res_id) if failed_trace.model and failed_trace.res_id else False
    
    payload = mailing._build_meta_payload(account, template, clean_digits, target_record)
    print("Payload preparado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    import requests
    url = f"https://graph.facebook.com/{account._get_api_version()}/{account.phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {account.token.strip()}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    print("\\n=== RESPOSTA DA META ===")
    print("Status code:", resp.status_code)
    print("Corpo da resposta:", resp.json())

    if resp.status_code in [200, 201]:
        wamid = resp.json().get('messages', [{}])[0].get('id')
        print(f"\\nSUCESSO TOTAL! Mensagem enviada com WAMID: {wamid}")
        failed_trace.write({
            'whatsapp_status': 'sent',
            'whatsapp_message_id': wamid,
            'whatsapp_sent_date': odoo.fields.Datetime.now(),
            'whatsapp_error_code': False,
            'whatsapp_error_message': False,
        })
        cr.commit()
        print("Trace atualizado com sucesso no banco!")
    else:
        print("\\nMeta ainda recusou o envio.")
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
