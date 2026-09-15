# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID
from collections import defaultdict

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contact = env['mailing.contact']
    
    total_before = Contact.search_count([])
    all_contacts = Contact.search([])
    
    no_phone = []
    by_phone = defaultdict(list)
    
    for c in all_contacts:
        raw = c.mobile_whatsapp or c.mobile or getattr(c, 'phone', False)
        if not raw:
            no_phone.append(c)
            continue
        digits = ''.join(ch for ch in str(raw) if ch.isdigit())
        if len(digits) < 8:
            no_phone.append(c)
            continue
        # Normalizar para chave única: se tiver 10 ou 11 dígitos no Brasil, prefixa 55
        if not digits.startswith('55') and len(digits) in (10, 11):
            key = '55' + digits
        else:
            key = digits
        by_phone[key].append(c)
        
    print(f"Total antes: {total_before}")
    print(f"Sem telefone válido para remover: {len(no_phone)}")
    print(f"Total de telefones únicos: {len(by_phone)}")
    
    duplicates_count = sum(len(clist) - 1 for clist in by_phone.values() if len(clist) > 1)
    print(f"Registros duplicados que serão mesclados e removidos: {duplicates_count}")
    print(f"Total final esperado de contatos únicos na base: {len(by_phone)}")
    
    # Simulação de mesclagem para os 5 primeiros duplicados
    for key, clist in list(by_phone.items())[:5]:
        if len(clist) > 1:
            master = clist[0]
            dups = clist[1:]
            merged_lists = set(master.list_ids.ids)
            for d in dups:
                merged_lists.update(d.list_ids.ids)
            print(f"Exemplo {key}: Master ID {master.id} ({master.name}), Duplicatas {[d.id for d in dups]}, Listas unificadas: {len(merged_lists)}")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=60)
print(stdout)
if stderr:
    print("STDERR:", stderr)
