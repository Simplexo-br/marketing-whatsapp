# -*- coding: utf-8 -*-
import logging
import phonenumbers
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    company_name = fields.Char(string="Nome da Empresa")
    mobile_whatsapp = fields.Char(string="WhatsApp (E.164)", compute='_compute_mobile_whatsapp', store=True, readonly=False, index=True)
    custom_var1 = fields.Char(string="Variável Personalizada 1")
    custom_var2 = fields.Char(string="Variável Personalizada 2")
    custom_var3 = fields.Char(string="Variável Personalizada 3")

    # Campos de Rastreamento de Status WhatsApp
    wa_status = fields.Selection([
        ('not_sent', 'Não Enviado'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('read', 'Visualizado'),
        ('replied', 'Respondido / Engajado'),
        ('opt_out', 'Opt-Out (Respondeu 2 / Sair)'),
    ], string="Status WhatsApp", default='not_sent', index=True)

    wa_status_sent = fields.Boolean(string="Enviado", default=False, index=True)
    wa_status_delivered = fields.Boolean(string="Entregue", default=False, index=True)
    wa_status_read = fields.Boolean(string="Visualizado", default=False, index=True)
    wa_status_replied = fields.Boolean(string="Respondido", default=False, index=True)
    wa_status_opt_out = fields.Boolean(string="Opt-Out (Respondeu 2)", default=False, index=True)

    wa_sent_date = fields.Datetime(string="Data de Envio")
    wa_read_date = fields.Datetime(string="Data de Visualização")
    wa_replied_date = fields.Datetime(string="Data de Resposta")
    wa_opt_out_date = fields.Datetime(string="Data do Opt-Out")
    wa_last_response = fields.Text(string="Última Resposta")

    @api.depends('country_id', 'mobile')
    def _compute_mobile_whatsapp(self):
        for contact in self:
            raw_phone = getattr(contact, 'mobile', False) or getattr(contact, 'phone', False) or getattr(contact, 'phone_sanitized', False)
            if not raw_phone:
                contact.mobile_whatsapp = False
                continue

            country_code = contact.country_id.code if contact.country_id else 'BR'
            sanitized = contact._sanitize_whatsapp_number(raw_phone, country_code)
            contact.mobile_whatsapp = sanitized or raw_phone

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            has_phone = vals.get('mobile_whatsapp') or vals.get('mobile') or vals.get('phone')
            if not has_phone:
                vals['wa_status'] = 'not_sent'
                vals['wa_status_sent'] = False
                vals['wa_status_delivered'] = False
                vals['wa_status_read'] = False
                vals['wa_status_replied'] = False
                vals['wa_status_opt_out'] = False
        return super().create(vals_list)

    def write(self, vals):
        if any(vals.get(f) for f in ['wa_status_sent', 'wa_status_delivered', 'wa_status_read', 'wa_status_replied', 'wa_status_opt_out']) or (vals.get('wa_status') and vals.get('wa_status') != 'not_sent'):
            for record in self:
                has_phone = vals.get('mobile_whatsapp') or vals.get('mobile') or record.mobile_whatsapp or record.mobile or getattr(record, 'phone', False)
                if not has_phone:
                    vals['wa_status'] = 'not_sent'
                    vals['wa_status_sent'] = False
                    vals['wa_status_delivered'] = False
                    vals['wa_status_read'] = False
                    vals['wa_status_replied'] = False
                    vals['wa_status_opt_out'] = False
                    break
        return super().write(vals)

    @api.model
    def _sanitize_whatsapp_number(self, phone_str, default_country='BR'):
        if not phone_str:
            return False
        cleaned = ''.join(c for c in phone_str if c.isdigit() or c == '+')
        try:
            parsed = phonenumbers.parse(cleaned, default_country)
            if phonenumbers.is_possible_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            pass
        
        # Fallback simples se o parser falhar mas começar com dígitos
        digits = ''.join(c for c in phone_str if c.isdigit())
        if digits:
            if not digits.startswith('55') and len(digits) in [10, 11] and default_country == 'BR':
                return f"+55{digits}"
            return f"+{digits}"
        return False

    @api.model
    def _cron_sync_whatsapp_contact_statuses(self):
        """Cron executado a cada 1 hora para sincronizar o status de Envio, Visualização, Respostas e Opt-Out dos contatos."""
        _logger.info("Iniciando sincronização horária de status dos contatos WhatsApp...")
        
        # 1. Sincronizar via mailing.trace (se existirem traces de WhatsApp)
        if 'mailing.trace' in self.env:
            traces = self.env['mailing.trace'].search([('trace_type', '=', 'whatsapp')])
            for tr in traces:
                if not tr.contact_id or not (tr.contact_id.mobile_whatsapp or tr.contact_id.mobile):
                    continue
                contact = tr.contact_id
                vals = {}
                if tr.sent_datetime and not contact.wa_status_sent:
                    vals['wa_status_sent'] = True
                    vals['wa_sent_date'] = tr.sent_datetime
                    vals['wa_status'] = 'sent'
                if tr.delivered_datetime and not contact.wa_status_delivered:
                    vals['wa_status_delivered'] = True
                    vals['wa_status'] = 'delivered'
                if tr.open_datetime and not contact.wa_status_read:
                    vals['wa_status_read'] = True
                    vals['wa_read_date'] = tr.open_datetime
                    vals['wa_status'] = 'read'
                if tr.reply_datetime and not contact.wa_status_replied:
                    vals['wa_status_replied'] = True
                    vals['wa_replied_date'] = tr.reply_datetime
                    vals['wa_status'] = 'replied'
                if vals:
                    contact.write(vals)

        # 2. Sincronizar via simplexo.aios.whatsapp.conversation (central multicanal do Odoo)
        if 'simplexo.aios.whatsapp.conversation' in self.env:
            convs = self.env['simplexo.aios.whatsapp.conversation'].search([])
            for conv in convs:
                phone = conv.customer_phone or conv.customer_wa_id
                if not phone:
                    continue
                clean_phone = ''.join(c for c in phone if c.isdigit())
                if len(clean_phone) >= 8:
                    domain = ['|', ('mobile_whatsapp', 'ilike', clean_phone[-8:]), ('mobile', 'ilike', clean_phone[-8:])]
                    matching_contacts = self.search(domain)
                    for contact in matching_contacts:
                        if not (contact.mobile_whatsapp or contact.mobile):
                            continue
                        vals = {}
                        # Checa se houve mensagens enviadas
                        outbound_msgs = conv.message_ids.filtered(lambda m: m.direction == 'outbound')
                        if outbound_msgs:
                            vals['wa_status_sent'] = True
                            if not contact.wa_sent_date and outbound_msgs[0].create_date:
                                vals['wa_sent_date'] = outbound_msgs[0].create_date
                            if any(m.state in ['delivered', 'read'] for m in outbound_msgs):
                                vals['wa_status_delivered'] = True
                            if any(m.state == 'read' or m.read_at for m in outbound_msgs):
                                vals['wa_status_read'] = True
                                vals['wa_read_date'] = outbound_msgs.filtered(lambda m: m.read_at)[:1].read_at or fields.Datetime.now()
                        
                        # Checa se houve respostas recebidas (inbound)
                        inbound_msgs = conv.message_ids.filtered(lambda m: m.direction == 'inbound')
                        if inbound_msgs:
                            last_msg = inbound_msgs[-1]
                            last_body = (last_msg.body or '').strip().lower()
                            vals['wa_replied_date'] = last_msg.create_date or fields.Datetime.now()
                            vals['wa_last_response'] = last_msg.body[:200] if last_msg.body else ''

                            # Identifica se o cliente respondeu "2" para Opt-Out / Não receber mais mensagens
                            opt_out_keywords = ['2', '2.', 'opcao 2', 'opção 2', 'parar', 'stop', 'sair', 'cancelar', 'nao', 'não', 'remover', 'descadastrar']
                            if last_body in opt_out_keywords or last_body.startswith('2'):
                                vals['wa_status_opt_out'] = True
                                vals['wa_opt_out_date'] = last_msg.create_date or fields.Datetime.now()
                                vals['wa_status'] = 'opt_out'
                                vals['wa_status_replied'] = False
                                
                                # Adiciona automaticamente na Blacklist do Odoo
                                if 'phone.blacklist' in self.env:
                                    phone_to_block = contact.mobile_whatsapp or contact.mobile
                                    if phone_to_block:
                                        sanitized_block = ''.join(c for c in phone_to_block if c.isdigit() or c == '+')
                                        existing_bl = self.env['phone.blacklist'].sudo().search([('number', '=', sanitized_block)])
                                        if not existing_bl:
                                            try:
                                                self.env['phone.blacklist'].sudo().create({'number': sanitized_block})
                                                _logger.info(f"Número {sanitized_block} inserido na Blacklist por responder 2 (Opt-Out).")
                                            except Exception as bl_err:
                                                _logger.warning(f"Erro ao adicionar na blacklist: {bl_err}")
                            else:
                                vals['wa_status_replied'] = True
                                vals['wa_status'] = 'replied'

                        # Se não for opt_out nem replied, ajusta conforme leitura/entrega/envio
                        if not vals.get('wa_status'):
                            if vals.get('wa_status_read'):
                                vals['wa_status'] = 'read'
                            elif vals.get('wa_status_delivered'):
                                vals['wa_status'] = 'delivered'
                            elif vals.get('wa_status_sent'):
                                vals['wa_status'] = 'sent'

                        if vals:
                            contact.write(vals)

        _logger.info("Sincronização horária de status dos contatos WhatsApp concluída.")

    @api.model
    def action_clean_duplicates_and_empty(self):
        """Ação administrativa para higienizar a base: mesclar contatos duplicados por telefone e remover contatos sem número."""
        from collections import defaultdict

        # 1. Resetar status de contatos que não têm telefone
        self._cr.execute("""
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
        """)

        all_contacts = self.search([])
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
            if not digits.startswith('55') and len(digits) in (10, 11):
                key = '+55' + digits
            elif digits.startswith('55') and len(digits) in (12, 13):
                key = '+' + digits
            else:
                try:
                    p = phonenumbers.parse('+' + digits if not digits.startswith('+') else digits, 'BR')
                    if phonenumbers.is_possible_number(p):
                        key = phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
                    else:
                        key = '+' + digits
                except Exception:
                    key = '+' + digits
            phone_groups[key].append(c)

        status_weights = {'opt_out': 5, 'replied': 4, 'read': 3, 'delivered': 2, 'sent': 1, 'not_sent': 0}
        merged_groups = 0
        records_to_delete_ids = []

        for key, clist in phone_groups.items():
            if len(clist) <= 1:
                single = clist[0]
                if single.mobile_whatsapp != key or single.mobile != key:
                    single.write({'mobile_whatsapp': key, 'mobile': key})
                continue

            def score_contact(c):
                return (status_weights.get(c.wa_status, 0), len(c.list_ids), 1 if c.name and c.name != key else 0, 1 if c.company_name else 0, -c.id)

            clist.sort(key=score_contact, reverse=True)
            master = clist[0]
            duplicates = clist[1:]

            combined_lists = set(master.list_ids.ids)
            best_status = master.wa_status or 'not_sent'
            sent = master.wa_status_sent
            delivered = master.wa_status_delivered
            read = master.wa_status_read
            replied = master.wa_status_replied
            opt_out = master.wa_status_opt_out
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
                dup_st = dup.wa_status or 'not_sent'
                if status_weights.get(dup_st, 0) > status_weights.get(best_status, 0):
                    best_status = dup_st
                sent = sent or dup.wa_status_sent
                delivered = delivered or dup.wa_status_delivered
                read = read or dup.wa_status_read
                replied = replied or dup.wa_status_replied
                opt_out = opt_out or dup.wa_status_opt_out
                records_to_delete_ids.append(dup.id)

            master.write({
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
                'list_ids': [(6, 0, list(combined_lists))]
            })
            merged_groups += 1

        all_deleted = records_to_delete_ids + no_phone_ids
        if all_deleted:
            try:
                self._cr.execute("DELETE FROM simplexo_aios_whatsapp_mailing_contact_map WHERE mailing_contact_id = ANY(%s);", (all_deleted,))
            except Exception:
                pass
            self._cr.execute("DELETE FROM mailing_subscription WHERE contact_id = ANY(%s);", (all_deleted,))
            self._cr.execute("DELETE FROM mailing_contact_mailing_contact_to_list_rel WHERE mailing_contact_id = ANY(%s);", (all_deleted,))
            self._cr.execute("DELETE FROM mailing_contact WHERE id = ANY(%s);", (all_deleted,))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Higienização Concluída"),
                'message': _("Sucesso: %s grupos duplicados mesclados (%s registros eliminados) e %s contatos sem telefone removidos.") % (merged_groups, len(records_to_delete_ids), len(no_phone_ids)),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'}
            }
        }
