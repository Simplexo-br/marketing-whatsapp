# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contact = env['mailing.contact']
    total = Contact.search_count([])
    
    contacts = Contact.search([])
    no_phone_contacts = []
    has_phone_contacts = []
    
    for c in contacts:
        p = c.mobile_whatsapp or c.mobile or getattr(c, 'phone', False)
        if not p or not any(char.isdigit() for char in str(p)):
            no_phone_contacts.append(c)
        else:
            has_phone_contacts.append(c)

    print(f"TOTAL CONTATOS: {total}")
    print(f"CONTATOS SEM TELEFONE: {len(no_phone_contacts)}")
    print(f"CONTATOS COM TELEFONE: {len(has_phone_contacts)}")

    # Verificar os contatos sem telefone que estão marcados como entregue/lido
    no_phone_marked = [c for c in no_phone_contacts if c.wa_status_delivered or c.wa_status_read or c.wa_status_sent or c.wa_status != 'not_sent']
    print(f"CONTATOS SEM TELEFONE MARCADOS COMO ENTREGUE/LIDO/ENVIADO: {len(no_phone_marked)}")
    for c in no_phone_marked[:15]:
        print(f" - ID: {c.id} | Nome: {c.name} | Empresa: {c.company_name} | Mobile: {c.mobile} | WhatsApp: {c.mobile_whatsapp} | Status: {c.wa_status} | Entregue: {c.wa_status_delivered} | Lido: {c.wa_status_read}")

    # Verificar duplicidades entre contatos com telefone
    from collections import defaultdict
    phone_map = defaultdict(list)
    for c in has_phone_contacts:
        p = c.mobile_whatsapp or c.mobile or getattr(c, 'phone', False)
        clean_p = ''.join(ch for ch in str(p) if ch.isdigit())
        phone_map[clean_p].append(c)

    duplicates = {p: clist for p, clist in phone_map.items() if len(clist) > 1}
    print(f"TOTAL DE TELEFONES DUPLICADOS: {len(duplicates)}")
    total_dup_records = sum(len(clist) for clist in duplicates.values())
    print(f"TOTAL DE REGISTROS DUPLICADOS ENVOLVIDOS: {total_dup_records}")
    for p, clist in list(duplicates.items())[:10]:
        print(f" * Telefone {p} ({len(clist)} registros):")
        for c in clist:
            print(f"    -> ID: {c.id} | Nome: {c.name} | Criado em: {c.create_date} | Status: {c.wa_status} | Listas: {c.list_ids.mapped('name')}")
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
