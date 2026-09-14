# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MailingWhatsAppTest(models.TransientModel):
    _name = 'wizard.mailing.whatsapp.test'
    _description = 'Enviar Teste de WhatsApp'

    mailing_id = fields.Many2one('mailing.mailing', string="Campanha", required=True)
    whatsapp_account_id = fields.Many2one('whatsapp.account', string="Conta de Envio", required=True)
    whatsapp_template_id = fields.Many2one('whatsapp.template', string="Template", required=True)
    test_phone_number = fields.Char(string="Número de WhatsApp para Teste", required=True, help="Número com DDD (ex: +5511999998888 ou 11999998888)")
    test_contact_name = fields.Char(string="Nome para Simulação {{1}}", default="Contato Teste")
    test_company_name = fields.Char(string="Empresa para Simulação {{2}}", default="Empresa Teste")

    def action_send_test(self):
        self.ensure_one()
        account = self.whatsapp_account_id
        template = self.whatsapp_template_id

        # Sanitiza número de telefone
        sanitized_phone = self.env['mailing.contact']._sanitize_whatsapp_number(self.test_phone_number, 'BR')
        if not sanitized_phone:
            raise UserError(_("Número de telefone de teste inválido."))

        clean_digits = ''.join(c for c in sanitized_phone if c.isdigit())
        api_version = account._get_api_version()
        url = f"https://graph.facebook.com/{api_version}/{account.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {account.token.strip()}",
            "Content-Type": "application/json"
        }

        # Mock record para extração de variáveis
        class MockRecord:
            name = self.test_contact_name
            company_name = self.test_company_name
            custom_var1 = "Var1 Teste"
            custom_var2 = "Var2 Teste"
            email = "teste@exemplo.com"

        payload = self.mailing_id._build_meta_payload(account, template, clean_digits, MockRecord())

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            data = response.json()

            if response.status_code in [200, 201]:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Mensagem de Teste Enviada!'),
                        'message': _('A mensagem de teste foi enviada com sucesso para %s.') % sanitized_phone,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                err_msg = data.get('error', {}).get('message', response.text)
                raise UserError(_("Erro ao enviar mensagem de teste pela Meta API: %s") % err_msg)

        except requests.exceptions.RequestException as e:
            raise UserError(_("Falha de conexão com a Meta: %s") % str(e))
