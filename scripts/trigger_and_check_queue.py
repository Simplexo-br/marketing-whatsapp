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
    Mailing = env['mailing.mailing']
    m = Mailing.browse(134)
    print(f"Campanha ID: {m.id} | Titulo: {m.subject} | Estado: {m.state}")
    
    Trace = env['mailing.trace']
    traces = Trace.search([('mass_mailing_id', '=', m.id)])
    sent_count = len(traces.filtered(lambda t: t.whatsapp_status == 'sent'))
    outgoing_count = len(traces.filtered(lambda t: t.whatsapp_status == 'outgoing'))
    delivered_count = len(traces.filtered(lambda t: t.whatsapp_status == 'delivered'))
    failed_count = len(traces.filtered(lambda t: t.whatsapp_status == 'failed'))
    print(f"Status Atual dos Traces (Total {len(traces)}):")
    print(f"  Enviados (sent): {sent_count}")
    print(f"  Entregues (delivered): {delivered_count}")
    print(f"  Na fila (outgoing): {outgoing_count}")
    print(f"  Falhas (failed): {failed_count}")
    
    # Se ainda estiver tudo outgoing e o cron ainda não rodou, vamos disparar o primeiro lote!
    if sent_count == 0 and outgoing_count > 0:
        print("Disparando o primeiro lote de 50 mensagens para iniciar o fluxo da fila...")
        m.write({'state': 'sending'})
        m._process_whatsapp_queue(batch_limit=50)
        cr.commit()
        
        # Recontar
        sent_count2 = len(traces.filtered(lambda t: t.whatsapp_status == 'sent'))
        outgoing_count2 = len(traces.filtered(lambda t: t.whatsapp_status == 'outgoing'))
        failed_count2 = len(traces.filtered(lambda t: t.whatsapp_status == 'failed'))
        print(f"Apos primeiro lote: sent={sent_count2}, outgoing={outgoing_count2}, failed={failed_count2}")
        
        # Amostra de mensagens enviadas
        sent_samples = traces.filtered(lambda t: t.whatsapp_status == 'sent')[:3]
        for s in sent_samples:
            print(f"  Destinatario: {s.whatsapp_recipient_number} | WAMID: {s.whatsapp_message_id} | Data: {s.whatsapp_sent_date}")
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
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
