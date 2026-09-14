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

    @api.depends('mobile', 'phone', 'country_id')
    def _compute_mobile_whatsapp(self):
        for contact in self:
            raw_phone = contact.mobile or contact.phone
            if not raw_phone:
                contact.mobile_whatsapp = False
                continue

            # Tenta sanitizar para E.164
            sanitized = contact._sanitize_whatsapp_number(raw_phone, contact.country_id.code or 'BR')
            contact.mobile_whatsapp = sanitized or raw_phone

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
