# -*- coding: utf-8 -*-
import base64
import csv
import io
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportWhatsAppContacts(models.TransientModel):
    _name = 'wizard.import.whatsapp.contacts'
    _description = 'Importar Contatos de Planilha para WhatsApp Marketing'

    file = fields.Binary(string="Arquivo de Planilha (.csv / .xlsx)", required=True)
    file_name = fields.Char(string="Nome do Arquivo")
    mailing_list_id = fields.Many2one('mailing.list', string="Lista de Disparo de Destino", required=True)
    country_id = fields.Many2one(
        'res.country',
        string="País Padrão para DDD/DDI",
        default=lambda self: self.env.ref('base.br', raise_if_not_found=False) or self.env['res.country'].search([('code', '=', 'BR')], limit=1)
    )

    column_name = fields.Char(string="Coluna do Nome", default="Nome", help="Nome da coluna com o nome do contato.")
    column_company = fields.Char(string="Coluna da Empresa", default="Empresa", help="Nome da coluna com a empresa.")
    column_phone = fields.Char(string="Coluna do WhatsApp/Telefone", default="Telefone", help="Nome da coluna com o número de WhatsApp.")
    column_var1 = fields.Char(string="Coluna da Variável 1", default="Var1")
    column_var2 = fields.Char(string="Coluna da Variável 2", default="Var2")
    
    update_existing = fields.Boolean(string="Atualizar contatos existentes", default=True)

    def action_import_contacts(self):
        self.ensure_one()
        if not self.file:
            raise UserError(_("Selecione um arquivo de planilha para importar."))

        file_content = base64.b64decode(self.file)
        rows = []

        # Tenta ler como CSV
        try:
            # Detecta encoding
            try:
                decoded = file_content.decode('utf-8-sig')
            except UnicodeDecodeError:
                decoded = file_content.decode('latin1')

            # Detecta delimitador (, ou ;)
            first_line = decoded.splitlines()[0] if decoded.splitlines() else ''
            delimiter = ';' if ';' in first_line else ','

            csv_reader = csv.DictReader(io.StringIO(decoded), delimiter=delimiter)
            for row in csv_reader:
                rows.append({k.strip().lower(): v.strip() for k, v in row.items() if k})
        except Exception as e:
            raise UserError(_("Erro ao processar arquivo: %s. Certifique-se de salvar em formato CSV (delimitado por vírgula ou ponto-e-vírgula).") % str(e))

        if not rows:
            raise UserError(_("Nenhum registro encontrado na planilha."))

        col_name_key = self.column_name.strip().lower()
        col_company_key = self.column_company.strip().lower()
        col_phone_key = self.column_phone.strip().lower()
        col_var1_key = (self.column_var1 or '').strip().lower()
        col_var2_key = (self.column_var2 or '').strip().lower()

        # Fallback se as colunas não baterem exato
        sample_keys = list(rows[0].keys())
        if col_phone_key not in sample_keys:
            # Procura por chaves que contenham 'tel', 'phone', 'whats', 'cel'
            for k in sample_keys:
                if any(x in k for x in ['tel', 'phone', 'whats', 'cel', 'fone', 'contato']):
                    col_phone_key = k
                    break

        if col_name_key not in sample_keys:
            for k in sample_keys:
                if any(x in k for x in ['nome', 'name', 'cliente', 'lead']):
                    col_name_key = k
                    break

        ContactModel = self.env['mailing.contact']
        country_code = self.country_id.code if self.country_id else 'BR'

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for row in rows:
            raw_phone = row.get(col_phone_key, '')
            if not raw_phone:
                skipped_count += 1
                continue

            sanitized_phone = ContactModel._sanitize_whatsapp_number(raw_phone, country_code)
            if not sanitized_phone:
                skipped_count += 1
                continue

            name = row.get(col_name_key, '') or sanitized_phone
            company = row.get(col_company_key, '')
            var1 = row.get(col_var1_key, '') if col_var1_key in row else ''
            var2 = row.get(col_var2_key, '') if col_var2_key in row else ''

            # Busca se já existe contato com esse número na base de forma ultra-robusta
            clean_digits = ''.join(c for c in sanitized_phone if c.isdigit())
            domain = [
                '|', '|',
                ('mobile_whatsapp', '=', sanitized_phone),
                ('mobile', '=', sanitized_phone),
                ('mobile_whatsapp', 'ilike', clean_digits[-8:] if len(clean_digits) >= 8 else clean_digits)
            ]
            existing_contact = ContactModel.search(domain, limit=1)

            vals = {
                'name': name,
                'company_name': company,
                'mobile': sanitized_phone,
                'mobile_whatsapp': sanitized_phone,
                'country_id': self.country_id.id if self.country_id else False,
                'custom_var1': var1,
                'custom_var2': var2,
            }

            if existing_contact:
                if self.update_existing:
                    existing_contact.write(vals)
                # Vincula à lista de disparo caso não esteja
                if self.mailing_list_id not in existing_contact.list_ids:
                    existing_contact.write({'list_ids': [(4, self.mailing_list_id.id)]})
                updated_count += 1
            else:
                vals['list_ids'] = [(4, self.mailing_list_id.id)]
                ContactModel.create(vals)
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Importação Concluída!'),
                'message': _('Contatos criados: %d | Contatos atualizados: %d | Ignorados (inválidos/vazios): %d') % (
                    created_count, updated_count, skipped_count
                ),
                'type': 'success',
                'sticky': True,
            }
        }
