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
    mailing = env['mailing.mailing'].browse(134)
    print(f"Campanha ID 134: '{mailing.name or mailing.subject}'")
    print(f"Estado anterior: {mailing.state}")

    # Executa action_retry_failed
    mailing.action_retry_failed()
    cr.commit()

    print(f"Estado apos acionar reenvio: {mailing.state}")
    
    # Contagem de traces
    TraceModel = env['mailing.trace']
    outgoing_count = TraceModel.search_count([('mass_mailing_id', '=', 134), ('whatsapp_status', '=', 'outgoing')])
    failed_count = TraceModel.search_count([('mass_mailing_id', '=', 134), ('whatsapp_status', '=', 'failed')])
    sent_count = TraceModel.search_count([('mass_mailing_id', '=', 134), ('whatsapp_status', 'in', ['sent', 'delivered', 'read'])])
    
    print(f"Traces da Campanha 134 agora:")
    print(f"  - Na fila para envio (outgoing): {outgoing_count}")
    print(f"  - Enviados/Entregues: {sent_count}")
    print(f"  - Com falha restante: {failed_count}")
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
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
