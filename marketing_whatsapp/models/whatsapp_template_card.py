# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WhatsAppTemplateCard(models.Model):
    _name = 'whatsapp.template.card'
    _description = 'Cartão de Template em Carrossel WhatsApp'
    _order = 'sequence, id'

    sequence = fields.Integer(string="Sequência / Ordem", default=10)
    template_id = fields.Many2one('whatsapp.template', string="Template Carrossel", ondelete='cascade', required=True)
    name = fields.Char(string="Título do Cartão", required=True)

    header_type = fields.Selection([
        ('image', 'Imagem (JPG/PNG)'),
        ('video', 'Vídeo (MP4)'),
    ], string="Tipo de Mídia", default='image', required=True)

    header_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Anexo de Imagem/Vídeo",
        help="Arquivo enviado no cabeçalho do cartão."
    )
    header_media_url = fields.Char(
        string="URL Pública da Mídia",
        help="URL direta para a imagem ou vídeo caso não carregue arquivo no Odoo."
    )

    body_text = fields.Text(string="Texto do Cartão (Corpo)", required=True)
    button_ids = fields.One2many('whatsapp.template.button', 'card_id', string="Botões do Cartão")
