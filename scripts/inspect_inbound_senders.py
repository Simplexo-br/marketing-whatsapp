# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
import re
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, fields, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contact = env['mailing.contact']
    Message = env['simplexo.aios.whatsapp.message']
    
    inbound_msgs = Message.search([('direction', '=', 'inbound')], order='occurred_at asc, id asc')
    distinct_senders = {}
    for m in inbound_msgs:
        sender = m.sender_ref or (m.conversation_id.customer_phone if m.conversation_id else False)
        if sender:
            distinct_senders[sender] = m
            
    print(f"Total de remetentes distintos com inbound: {len(distinct_senders)}")
    
    unmatched = []
    matched = []
    for sender, msg in distinct_senders.items():
        digits = re.sub(r'\\D', '', sender)
        # Tentar 8 digitos finais
        suffix8 = digits[-8:] if len(digits) >= 8 else digits
        # Tentar 9 digitos finais
        suffix9 = digits[-9:] if len(digits) >= 9 else digits
        # Tentar 10 ou 11 digitos finais (DDD + numero)
        suffix11 = digits[-11:] if len(digits) >= 11 else digits
        
        contacts = Contact.search([
            '|', '|', '|', '|',
            ('mobile_whatsapp', 'like', suffix8),
            ('mobile', 'like', suffix8),
            ('mobile_whatsapp', 'like', suffix9),
            ('mobile', 'like', suffix9),
            ('mobile_whatsapp', 'like', suffix11),
        ])
        if contacts:
            matched.append((sender, msg.body, [c.name for c in contacts]))
        else:
            unmatched.append((sender, msg.body, (msg.conversation_id.name if msg.conversation_id else '')))
            
    print(f"Remetentes encontrados em mailing.contact: {len(matched)}")
    print(f"Remetentes NAO encontrados diretamente: {len(unmatched)}")
    print("Exemplos de remetentes nao encontrados:")
    for u in unmatched[:10]:
        print(" ", u)
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=30)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
