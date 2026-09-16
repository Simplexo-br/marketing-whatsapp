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
    Trace = env['mailing.trace']
    Message = env['simplexo.aios.whatsapp.message']
    
    print("=== SINCRONIZANDO RESPOSTAS INBOUND DOS CLIENTES ===")
    inbound_msgs = Message.search([('direction', '=', 'inbound')], order='occurred_at asc, id asc')
    print(f"Total de mensagens inbound encontradas: {len(inbound_msgs)}")
    
    synced_contacts = 0
    opt_out_keywords = ['2', '2.', 'opcao 2', 'opção 2', 'parar', 'stop', 'sair', 'cancelar', 'nao', 'não', 'remover', 'descadastrar']
    
    for msg in inbound_msgs:
        phone = msg.sender_ref or (msg.conversation_id.customer_phone if msg.conversation_id else False)
        if not phone:
            continue
        digits = re.sub(r'\\D', '', phone)
        if len(digits) < 8:
            continue
        suffix = digits[-8:]
        
        contacts = Contact.search(['|', ('mobile_whatsapp', 'like', suffix), ('mobile', 'like', suffix)])
        if not contacts:
            continue
            
        body = (msg.body or '').strip()
        lower_body = body.lower()
        
        for c in contacts:
            c_vals = {
                'wa_status_replied': True,
                'wa_replied_date': msg.occurred_at or msg.create_date or fields.Datetime.now(),
                'wa_last_response': body[:200] if body else 'Resposta recebida',
                'wa_status': 'replied'
            }
            if lower_body in opt_out_keywords or lower_body.startswith('2'):
                c_vals['wa_status_opt_out'] = True
                c_vals['wa_opt_out_date'] = msg.occurred_at or msg.create_date or fields.Datetime.now()
                c_vals['wa_status'] = 'opt_out'
                c_vals['wa_status_replied'] = False
                
                # Blacklist
                p_blk = c.mobile_whatsapp or c.mobile
                if p_blk:
                    s_blk = re.sub(r'[^0-9+]', '', p_blk)
                    if not env['phone.blacklist'].sudo().search([('number', '=', s_blk)], limit=1):
                        env['phone.blacklist'].sudo().create({'number': s_blk})
            
            c.write(c_vals)
            synced_contacts += 1

    print(f"Total de contatos atualizados com respostas: {synced_contacts}")
    
    cr.commit()
    
    # Conferir contagem final
    replied = Contact.search_count([('wa_status_replied', '=', True)])
    opt_out = Contact.search_count([('wa_status_opt_out', '=', True)])
    print(f"Contatos marcados como REPLIED: {replied}")
    print(f"Contatos marcados como OPT_OUT: {opt_out}")
    
    # Listar as primeiras 5 respostas
    recent = Contact.search([('wa_status_replied', '=', True)], order='wa_replied_date desc', limit=5)
    for r in recent:
        print(f"  [{r.wa_replied_date}] {r.name} ({r.mobile_whatsapp or r.mobile}): {r.wa_last_response}")
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
