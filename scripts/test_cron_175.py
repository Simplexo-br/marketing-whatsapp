# -*- coding: utf-8 -*-
import subprocess
import os
import base64

remote_script = """# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    cron_175 = env['ir.cron'].browse(175)
    print("=== DETALHES DO CRON 175 ===")
    print("Nome:", cron_175.name.encode('ascii', errors='replace').decode('ascii'))
    print("Ativo:", cron_175.active)
    print("Intervalo:", cron_175.interval_number, cron_175.interval_type)
    print("Proxima chamada:", cron_175.nextcall)
    print("Ultima execucao / write_date:", cron_175.write_date)
    
    # Testa uma execucao manual do metodo para certificar que roda 100% sem erros
    try:
        env['mailing.contact']._cron_sync_whatsapp_contact_statuses()
        print("Execucao do metodo _cron_sync_whatsapp_contact_statuses() concluiu com SUCESSO!")
    except Exception as e:
        print("Erro ao executar _cron_sync_whatsapp_contact_statuses():", e)
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} \"{remote_cmd}\""
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
print(stdout.encode('ascii', errors='replace').decode('ascii'))
if stderr:
    print('STDERR:', stderr.encode('ascii', errors='replace').decode('ascii'))
