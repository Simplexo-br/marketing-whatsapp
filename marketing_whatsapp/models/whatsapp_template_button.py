# -*- coding: utf-8 -*-
from odoo import fields, models


class WhatsAppTemplateButton(models.Model):
    _name = 'whatsapp.template.button'
    _description = 'Botão de Template WhatsApp'
    _order = 'sequence, id'

    sequence = fields.Integer(string="Sequência", default=10)
    template_id = fields.Many2one('whatsapp.template', string="Template", ondelete='cascade', required=True)
    name = fields.Char(string="Texto do Botão", required=True)
    button_type = fields.Selection([
        ('QUICK_REPLY', 'Resposta Rápida (Quick Reply)'),
        ('URL', 'Link Web (URL)'),
        ('PHONE_NUMBER', 'Ligar para Número (Phone Call)'),
        ('OTP', 'Código de Autenticação (OTP)'),
    ], string="Tipo de Botão", default='QUICK_REPLY', required=True)
    url = fields.Char(string="URL de Destino")
    phone_number = fields.Char(string="Número de Telefone")
