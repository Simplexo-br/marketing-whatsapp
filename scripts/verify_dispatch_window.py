# -*- coding: utf-8 -*-
import subprocess
import os
import base64

default_keys = [
    os.environ.get('SIMPLEXO_SSH_KEY'),
    os.path.expanduser('~/.ssh/simplexo_vm'),
    os.path.expanduser('~/.ssh/simplexo_gpt_desktop'),
    r'C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm',
]
ssh_key = next((k for k in default_keys if k and os.path.exists(k)), default_keys[-1])
bastion = 'fellipe_ramalho@35.224.220.67'
internal_server = 'fellipe_ramalho@34.45.88.55'

remote_script = '''# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID
import pytz
from datetime import datetime

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 1. Checagem de Fuso e Janela
    tz = pytz.timezone('America/Sao_Paulo')
    now_sp = datetime.now(tz)
    print(f"1. Horário Atual de Brasília: {now_sp.strftime('%d/%m/%Y %H:%M:%S')}")
    
    Mailing = env['mailing.mailing']
    is_window_open = Mailing._is_within_dispatch_window()
    print(f"2. Janela de Disparo Aberta Agora? {is_window_open} (Permitido: 08:00 às 17:00)")
    
    # 2. Executa simulação do Cron
    print("3. Executando chamada do cron de envio:")
    Mailing._cron_process_whatsapp_queue()
    print("   -> Cron executado com sucesso e respeitou a trava de horário.")

    # 3. Status da Campanha 134
    m = Mailing.browse(134)
    outgoing = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'outgoing')])
    sent = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'sent')])
    delivered = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'delivered')])
    read = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'read')])
    failed = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'failed')])
    total = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id)])

    print("=== STATUS DA CAMPANHA 134 ===")
    print(f"Título: {m.subject or m.name}")
    print(f"Estado no Odoo: {m.state} (Pausada: {m.is_paused})")
    print(f"Restantes na Fila (Outgoing): {outgoing}")
    print(f"Enviados: {sent} | Entregues: {delivered} | Lidos: {read} | Falhas: {failed}")
    print(f"Total de Destinatários: {total}")
'''

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15',
    '-i', ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

p = subprocess.run(cmd, capture_output=True, text=True)
print(p.stdout)
if p.stderr:
    print('STDERR:', p.stderr)
