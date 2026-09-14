# -*- coding: utf-8 -*-
from odoo import fields, models


class MailingTrace(models.Model):
    _inherit = 'mailing.trace'

    trace_type = fields.Selection(selection_add=[
        ('whatsapp', 'WhatsApp')
    ], ondelete={'whatsapp': 'cascade'})

    whatsapp_account_id = fields.Many2one('whatsapp.account', string="Conta de Envio")
    whatsapp_message_id = fields.Char(string="Meta Message ID (WAMID)", index=True)
    whatsapp_recipient_number = fields.Char(string="Número de Destino")
    
    whatsapp_status = fields.Selection([
        ('outgoing', 'Na Fila'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('read', 'Lido'),
        ('failed', 'Falha'),
        ('canceled', 'Cancelado / Blacklist')
    ], string="Status WhatsApp", default='outgoing', index=True)

    whatsapp_error_code = fields.Char(string="Código de Erro Meta")
    whatsapp_error_message = fields.Text(string="Detalhes do Erro")

    whatsapp_sent_date = fields.Datetime(string="Data de Envio")
    whatsapp_delivered_date = fields.Datetime(string="Data de Entrega")
    whatsapp_read_date = fields.Datetime(string="Data de Leitura")
