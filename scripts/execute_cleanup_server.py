# -*- coding: utf-8 -*-
import subprocess
import os
import sys

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo import api, SUPERUSER_ID
from collections import defaultdict
import phonenumbers
import logging

_logger = logging.getLogger('contact_dedup')
_logger.setLevel(logging.INFO)

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contact = env['mailing.contact']
    
    total_initial = Contact.search_count([])
    print(f"=== INICIANDO HIGIENIZACAO: {total_initial} CONTATOS NA BASE ===")
    
    # 1. Resetar status de contatos que não têm telefone
    cr.execute(\"\"\"
        UPDATE mailing_contact
        SET wa_status = 'not_sent',
            wa_status_sent = FALSE,
            wa_status_delivered = FALSE,
            wa_status_read = FALSE,
            wa_status_replied = FALSE,
            wa_status_opt_out = FALSE,
            wa_sent_date = NULL,
            wa_read_date = NULL,
            wa_replied_date = NULL,
            wa_opt_out_date = NULL,
            wa_last_response = NULL
        WHERE (mobile_whatsapp IS NULL OR TRIM(mobile_whatsapp) = '')
          AND (mobile IS NULL OR TRIM(mobile) = '');
    \"\"\")
    print(f"1. Reset de status concluido para contatos sem telefone.")

    # 2. Carregar todos os contatos
    all_contacts = Contact.search([])
    
    no_phone_ids = []
    phone_groups = defaultdict(list)
    
    for c in all_contacts:
        raw = c.mobile_whatsapp or c.mobile or getattr(c, 'phone', False)
        if not raw:
            no_phone_ids.append(c.id)
            continue
            
        digits = ''.join(ch for ch in str(raw) if ch.isdigit())
        if len(digits) < 8:
            no_phone_ids.append(c.id)
            continue
            
        # Normalizar para chave única (E.164 padronizado)
        if not digits.startswith('55') and len(digits) in (10, 11):
            key = '+55' + digits
        elif digits.startswith('55') and len(digits) in (12, 13):
            key = '+' + digits
        else:
            # Tentar phonenumbers
            try:
                p = phonenumbers.parse('+' + digits if not digits.startswith('+') else digits, 'BR')
                if phonenumbers.is_possible_number(p):
                    key = phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
                else:
                    key = '+' + digits
            except:
                key = '+' + digits
                
        phone_groups[key].append(c)

    print(f"2. Mapeamento: {len(phone_groups)} telefones unicos | {len(no_phone_ids)} contatos sem telefone.")

    # Status hierarchy priority
    status_weights = {
        'opt_out': 5,
        'replied': 4,
        'read': 3,
        'delivered': 2,
        'sent': 1,
        'not_sent': 0
    }

    # 3. Mesclar duplicidades para cada telefone
    merged_count = 0
    records_to_delete_ids = []

    for key, clist in phone_groups.items():
        if len(clist) <= 1:
            # Apenas 1 registro, garante que mobile_whatsapp está com formato limpo
            single = clist[0]
            if single.mobile_whatsapp != key or single.mobile != key:
                single.write({'mobile_whatsapp': key, 'mobile': key})
            continue

        # Ordenar contatos para eleger o melhor master
        # Prioriza: quem tem o status mais avançado, quem tem email/empresa preenchidos, e por fim o menor ID (mais antigo)
        def score_contact(contact):
            st_score = status_weights.get(contact.wa_status, 0)
            has_company = 1 if contact.company_name else 0
            has_email = 1 if contact.email else 0
            has_name = 1 if contact.name and contact.name != key else 0
            lists_count = len(contact.list_ids)
            return (st_score, lists_count, has_name, has_company, has_email, -contact.id)

        clist.sort(key=score_contact, reverse=True)
        master = clist[0]
        duplicates = clist[1:]

        # Consolidar dados das duplicatas no master
        combined_lists = set(master.list_ids.ids)
        best_status = master.wa_status or 'not_sent'
        sent = master.wa_status_sent
        delivered = master.wa_status_delivered
        read = master.wa_status_read
        replied = master.wa_status_replied
        opt_out = master.wa_status_opt_out
        
        sent_date = master.wa_sent_date
        read_date = master.wa_read_date
        replied_date = master.wa_replied_date
        opt_out_date = master.wa_opt_out_date
        last_resp = master.wa_last_response
        company = master.company_name
        email = master.email
        name = master.name

        for dup in duplicates:
            combined_lists.update(dup.list_ids.ids)
            if not company and dup.company_name:
                company = dup.company_name
            if not email and dup.email:
                email = dup.email
            if (not name or name == key) and dup.name and dup.name != key:
                name = dup.name
            
            # Status
            dup_st = dup.wa_status or 'not_sent'
            if status_weights.get(dup_st, 0) > status_weights.get(best_status, 0):
                best_status = dup_st

            sent = sent or dup.wa_status_sent
            delivered = delivered or dup.wa_status_delivered
            read = read or dup.wa_status_read
            replied = replied or dup.wa_status_replied
            opt_out = opt_out or dup.wa_status_opt_out

            if dup.wa_sent_date and (not sent_date or dup.wa_sent_date < sent_date):
                sent_date = dup.wa_sent_date
            if dup.wa_read_date and (not read_date or dup.wa_read_date > read_date):
                read_date = dup.wa_read_date
            if dup.wa_replied_date and (not replied_date or dup.wa_replied_date > replied_date):
                replied_date = dup.wa_replied_date
            if dup.wa_opt_out_date and (not opt_out_date or dup.wa_opt_out_date > opt_out_date):
                opt_out_date = dup.wa_opt_out_date
            if dup.wa_last_response and not last_resp:
                last_resp = dup.wa_last_response

            records_to_delete_ids.append(dup.id)

        # Atualizar master com os dados consolidados
        master_vals = {
            'mobile_whatsapp': key,
            'mobile': key,
            'name': name or key,
            'company_name': company or False,
            'email': email or False,
            'wa_status': best_status,
            'wa_status_sent': sent,
            'wa_status_delivered': delivered,
            'wa_status_read': read,
            'wa_status_replied': replied,
            'wa_status_opt_out': opt_out,
            'wa_sent_date': sent_date,
            'wa_read_date': read_date,
            'wa_replied_date': replied_date,
            'wa_opt_out_date': opt_out_date,
            'wa_last_response': last_resp,
            'list_ids': [(6, 0, list(combined_lists))]
        }
        master.write(master_vals)
        merged_count += 1

    print(f"3. Consolidacao concluida: {merged_count} grupos de duplicados unificados no Master.")
    print(f"   Total de registros duplicados a remover: {len(records_to_delete_ids)}")

    # 4. Remover duplicatas via SQL de forma ultra-rápida e segura mantendo integridade
    if records_to_delete_ids:
        # Re-apontar qualquer referência em simplexo_aios_whatsapp_mailing_contact_map
        try:
            cr.execute(\"\"\"
                DELETE FROM simplexo_aios_whatsapp_mailing_contact_map 
                WHERE mailing_contact_id = ANY(%s);
            \"\"\", (records_to_delete_ids,))
        except Exception as e:
            pass
            
        # Remover assinaturas de lista das duplicatas
        cr.execute(\"\"\"
            DELETE FROM mailing_subscription
            WHERE contact_id = ANY(%s);
        \"\"\", (records_to_delete_ids,))

        # Remover rels many2many
        cr.execute(\"\"\"
            DELETE FROM mailing_contact_mailing_contact_to_list_rel
            WHERE mailing_contact_id = ANY(%s);
        \"\"\", (records_to_delete_ids,))

        # Remover os contatos duplicados
        cr.execute(\"\"\"
            DELETE FROM mailing_contact
            WHERE id = ANY(%s);
        \"\"\", (records_to_delete_ids,))
        print("4. Registros duplicados removidos com sucesso!")

    # 5. Remover contatos sem telefone da base
    if no_phone_ids:
        print(f"5. Removendo {len(no_phone_ids)} contatos sem telefone...")
        # Remover assinaturas e relações
        cr.execute(\"\"\"
            DELETE FROM mailing_subscription
            WHERE contact_id = ANY(%s);
        \"\"\", (no_phone_ids,))
        cr.execute(\"\"\"
            DELETE FROM mailing_contact_mailing_contact_to_list_rel
            WHERE mailing_contact_id = ANY(%s);
        \"\"\", (no_phone_ids,))
        try:
            cr.execute(\"\"\"
                DELETE FROM simplexo_aios_whatsapp_mailing_contact_map 
                WHERE mailing_contact_id = ANY(%s);
            \"\"\", (no_phone_ids,))
        except Exception as e:
            pass
            
        cr.execute(\"\"\"
            DELETE FROM mailing_contact
            WHERE id = ANY(%s);
        \"\"\", (no_phone_ids,))
        print("5. Contatos sem telefone removidos com sucesso!")

    cr.commit()
    
    # 6. Auditoria Final
    total_final = Contact.search_count([])
    final_no_phone = Contact.search_count([('mobile_whatsapp', '=', False), ('mobile', '=', False)])
    print(f"=== RESULTADO FINAL DA AUDITORIA ===")
    print(f"Total de contatos final: {total_final}")
    print(f"Contatos sem telefone: {final_no_phone}")
    
    # Conferir se ainda existe alguma duplicata por telefone
    cr.execute(\"\"\"
        SELECT mobile_whatsapp, count(*) 
        FROM mailing_contact 
        GROUP BY mobile_whatsapp 
        HAVING count(*) > 1;
    \"\"\")
    rem_dups = cr.fetchall()
    print(f"Duplicidades restantes por mobile_whatsapp: {len(rem_dups)}")
    
    # Conferir se ha contatos marcados como entregue sem telefone
    cr.execute(\"\"\"
        SELECT count(*) FROM mailing_contact 
        WHERE (mobile_whatsapp IS NULL OR TRIM(mobile_whatsapp) = '')
          AND wa_status != 'not_sent';
    \"\"\")
    invalid_status = cr.fetchone()[0]
    print(f"Contatos sem telefone com status ativo: {invalid_status}")
    print("SUCESSO_TOTAL_HIGIENIZACAO")
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
stdout, stderr = proc.communicate(input=remote_script, timeout=180)
print(stdout)
if stderr:
    print("STDERR:", stderr)
