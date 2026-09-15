# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _


class WhatsAppTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'Template de Mensagem WhatsApp (Meta Cloud API)'
    _inherit = ['mail.thread']

    name = fields.Char(string="Nome Técnico (Meta)", required=True, tracking=True, help="Nome do template cadastrado e aprovado na Meta (letras minúsculas e underscores).")
    account_id = fields.Many2one('whatsapp.account', string="Conta de WhatsApp", required=True, ondelete='cascade')
    meta_template_id = fields.Char(string="ID do Template na Meta", readonly=True)
    language = fields.Char(string="Idioma", default="pt_BR", required=True)

    category = fields.Selection([
        ('MARKETING', 'Marketing (Campanhas & Promoções)'),
        ('UTILITY', 'Utilidade (Avisos, Notificações, Pedidos)'),
        ('AUTHENTICATION', 'Autenticação (Códigos OTP)'),
    ], string="Categoria", default='MARKETING', required=True, tracking=True)

    status = fields.Selection([
        ('APPROVED', '✅ Aprovado'),
        ('PENDING', '⏳ Em Análise'),
        ('REJECTED', '❌ Rejeitado'),
        ('PAUSED', '⚠️ Pausado pela Meta'),
    ], string="Status na Meta", default='APPROVED', tracking=True)

    template_type = fields.Selection([
        ('standard', 'Padrão (Texto / Mídia Única)'),
        ('carousel', 'Carrossel Interativo (Múltiplos Cartões)'),
    ], string="Tipo de Template", default='standard', required=True, tracking=True)

    header_type = fields.Selection([
        ('none', 'Sem Cabeçalho'),
        ('text', 'Texto'),
        ('image', 'Imagem (JPG/PNG)'),
        ('document', 'Documento (PDF)'),
        ('video', 'Vídeo (MP4)'),
    ], string="Tipo de Cabeçalho", default='none')

    header_text = fields.Char(string="Texto do Cabeçalho")
    body_text = fields.Text(string="Corpo da Mensagem (com variáveis {{1}}, {{2}}...)")
    footer_text = fields.Char(string="Rodapé da Mensagem")
    button_ids = fields.One2many('whatsapp.template.button', 'template_id', string="Botões Interativos")
    card_ids = fields.One2many('whatsapp.template.card', 'template_id', string="Cartões do Carrossel")

    body_variables_count = fields.Integer(string="Número de Variáveis no Corpo", compute='_compute_variables_count')
    preview_html = fields.Html(string="Prévia WhatsApp", compute='_compute_preview_html')

    @api.depends('body_text')
    def _compute_variables_count(self):
        for record in self:
            if record.body_text:
                matches = re.findall(r'\{\{(\d+)\}\}', record.body_text)
                record.body_variables_count = len(set(matches))
            else:
                record.body_variables_count = 0

    @api.depends('template_type', 'header_type', 'header_text', 'body_text', 'footer_text', 'button_ids', 'card_ids', 'card_ids.name', 'card_ids.body_text', 'card_ids.button_ids')
    def _compute_preview_html(self):
        for record in self:
            if record.template_type == 'carousel':
                # Renderizador de Carrossel WhatsApp
                preview = "<div style='max-width: 440px; background: #e5ddd5; border-radius: 12px; padding: 14px; font-family: sans-serif; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>"
                if record.body_text:
                    formatted_main_body = record.body_text.replace('\n', '<br/>')
                    preview += f"<div style='background: #ffffff; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 14px; color: #111b21;'>{formatted_main_body}</div>"

                preview += "<div style='display: flex; gap: 10px; overflow-x: auto; padding-bottom: 6px; scroll-snap-type: x mandatory;'>"
                if record.card_ids:
                    for idx, card in enumerate(record.card_ids, 1):
                        preview += "<div style='min-width: 210px; max-width: 210px; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.12); flex-shrink: 0; scroll-snap-align: start;'>"
                        media_icon = "📷 Imagem" if card.header_type == 'image' else "🎥 Vídeo"
                        preview += f"<div style='background: #e9edef; height: 110px; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #54656f; font-weight: 500;'>{media_icon} #{idx}</div>"
                        preview += f"<div style='padding: 8px 10px; font-weight: 600; font-size: 13px; color: #111b21;'>{card.name or 'Item'}</div>"
                        card_body = (card.body_text or '').replace('\n', '<br/>')
                        preview += f"<div style='padding: 0 10px 8px 10px; font-size: 12px; color: #3b4a54; line-height: 1.3;'>{card_body}</div>"
                        if card.button_ids:
                            for btn in card.button_ids:
                                preview += f"<div style='border-top: 1px solid #e9edef; padding: 7px; text-align: center; color: #00a884; font-weight: 500; font-size: 12px;'>{btn.name}</div>"
                        preview += "</div>"
                else:
                    preview += "<div style='color: #667781; font-style: italic; padding: 15px;'>Adicione ao menos um cartão para visualizar o carrossel.</div>"

                preview += "</div></div>"
                record.preview_html = preview
            else:
                # Renderizador de Mensagem Padrão
                preview = "<div style='max-width: 380px; background: #e5ddd5; border-radius: 12px; padding: 14px; font-family: sans-serif; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>"
                preview += "<div style='background: #ffffff; border-radius: 8px; padding: 10px; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>"

                if record.header_type == 'image':
                    preview += "<div style='border-radius: 6px; overflow: hidden; margin-bottom: 8px;'><img src='/marketing_whatsapp/static/src/img/simplexo_banner_marketing.png' style='width: 100%; height: auto; display: block; border-radius: 6px;' alt='Banner WhatsApp'/></div>"
                elif record.header_type == 'document':
                    preview += "<div style='background: #f0f2f5; height: 60px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #54656f; margin-bottom: 8px;'>📄 [Documento PDF]</div>"
                elif record.header_type == 'video':
                    preview += "<div style='background: #f0f2f5; height: 140px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #54656f; margin-bottom: 8px;'>🎥 [Vídeo MP4]</div>"
                elif record.header_type == 'text' and record.header_text:
                    preview += f"<div style='font-weight: bold; color: #111b21; margin-bottom: 6px;'>{record.header_text}</div>"

                formatted_body = (record.body_text or '').replace('\n', '<br/>')
                preview += f"<div style='color: #111b21; font-size: 14px; line-height: 1.4;'>{formatted_body}</div>"

                if record.footer_text:
                    preview += f"<div style='color: #667781; font-size: 11px; margin-top: 6px;'>{record.footer_text}</div>"

                preview += "</div>"

                if record.button_ids:
                    for btn in record.button_ids:
                        btn_icon = "🌐 " if btn.button_type == 'URL' else ("↩️ " if btn.button_type == 'QUICK_REPLY' else "📞 ")
                        preview += f"<div style='margin-top: 4px; background: #ffffff; border-radius: 6px; padding: 8px; text-align: center; color: #00a884; font-weight: 500; font-size: 13px; box-shadow: 0 1px 1px rgba(0,0,0,0.08);'>{btn_icon}{btn.name}</div>"

                preview += "</div>"
                record.preview_html = preview

    def _compute_display_name(self):
        for rec in self:
            label = f"{rec.name} ({rec.language})"
            if rec.status != 'APPROVED':
                label += f" [{rec.status}]"
            rec.display_name = label
