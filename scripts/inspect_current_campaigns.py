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

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    mailings = env['mailing.mailing'].search([('mailing_type', '=', 'whatsapp')])
    print('=== CAMPANHAS DE WHATSAPP NO BANCO ===')
    for m in mailings:
        traces_outgoing = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'outgoing')])
        traces_sent = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'sent')])
        traces_failed = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id), ('whatsapp_status', '=', 'failed')])
        traces_total = env['mailing.trace'].search_count([('mass_mailing_id', '=', m.id)])
        print(f'ID: {m.id} | Titulo: {m.subject or m.name} | State: {m.state} | Outgoing: {traces_outgoing} | Sent: {traces_sent} | Failed: {traces_failed} | Total: {traces_total}')

    crons = env['ir.cron'].search(['|', ('name', 'ilike', 'whatsapp'), ('model_name', 'ilike', 'mailing')])
    print('=== CRONS DE WHATSAPP / MAILING ===')
    for c in crons:
        print(f'CRON ID: {c.id} | Nome: {c.name} | Model: {c.model_name} | Method: {c.code} | Active: {c.active} | Interval: {c.interval_number} {c.interval_type} | Nextcall: {c.nextcall}')
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
