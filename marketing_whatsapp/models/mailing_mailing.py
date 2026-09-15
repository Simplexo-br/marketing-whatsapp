# -*- coding: utf-8 -*-
import base64
import json
import logging
import time
import requests
import phonenumbers
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    mailing_type = fields.Selection(selection_add=[
        ('whatsapp', 'Marketing WhatsApp')
    ], ondelete={'whatsapp': 'set default'})

    whatsapp_account_id = fields.Many2one(
        'whatsapp.account',
        string="Conta de Envio",
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param('marketing_whatsapp.default_account_id') or self.env['whatsapp.account'].search([], limit=1).id
    )
    whatsapp_template_id = fields.Many2one(
        'whatsapp.template',
        string="Template WhatsApp",
        domain="[('account_id', '=', whatsapp_account_id), ('status', '=', 'APPROVED')]"
    )
    whatsapp_header_media_type = fields.Selection(
        related='whatsapp_template_id.header_type',
        string="Tipo de Mídia do Cabeçalho",
        readonly=True
    )
    whatsapp_media_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Anexo de Mídia (Imagem/PDF/Vídeo)",
        help="Arquivo que será enviado como cabeçalho da mensagem (para templates com mídia)."
    )
    whatsapp_media_url = fields.Char(
        string="URL Pública da Mídia",
        help="URL direta para a imagem ou documento caso prefira não carregar o arquivo no Odoo."
    )
    company_id = fields.Many2one(
        'res.company',
        string="Empresa",
        default=lambda self: (self.whatsapp_account_id.company_id if hasattr(self, 'whatsapp_account_id') and self.whatsapp_account_id else self.env.company)
    )

    # Variáveis dinâmicas para interpolação
    whatsapp_var1_field = fields.Selection([
        ('name', 'Nome do Contato / Lead'),
        ('company_name', 'Nome da Empresa / Parceiro'),
        ('custom_var1', 'Variável Personalizada 1'),
        ('custom_var2', 'Variável Personalizada 2'),
        ('email', 'E-mail'),
    ], string="Variável {{1}}", default='name')

    whatsapp_var2_field = fields.Selection([
        ('name', 'Nome do Contato / Lead'),
        ('company_name', 'Nome da Empresa / Parceiro'),
        ('custom_var1', 'Variável Personalizada 1'),
        ('custom_var2', 'Variável Personalizada 2'),
        ('email', 'E-mail'),
    ], string="Variável {{2}}", default='company_name')

    whatsapp_var3_field = fields.Selection([
        ('name', 'Nome do Contato / Lead'),
        ('company_name', 'Nome da Empresa / Parceiro'),
        ('custom_var1', 'Variável Personalizada 1'),
        ('custom_var2', 'Variável Personalizada 2'),
        ('email', 'E-mail'),
    ], string="Variável {{3}}", default='custom_var1')

    whatsapp_preview_html = fields.Html(
        string="Prévia da Mensagem",
        compute='_compute_whatsapp_preview_html'
    )

    # Estatísticas de Entrega
    whatsapp_sent_count = fields.Integer(string="Enviados", compute='_compute_whatsapp_stats')
    whatsapp_delivered_count = fields.Integer(string="Entregues", compute='_compute_whatsapp_stats')
    whatsapp_read_count = fields.Integer(string="Lidos", compute='_compute_whatsapp_stats')
    whatsapp_failed_count = fields.Integer(string="Falhas", compute='_compute_whatsapp_stats')

    @api.depends('whatsapp_template_id', 'whatsapp_media_attachment_id')
    def _compute_whatsapp_preview_html(self):
        for mailing in self:
            if mailing.whatsapp_template_id:
                mailing.whatsapp_preview_html = mailing.whatsapp_template_id.preview_html
            else:
                mailing.whatsapp_preview_html = "<div style='color: #888; font-style: italic; padding: 20px;'>Selecione um template aprovado para visualizar a mensagem.</div>"

    def _compute_whatsapp_stats(self):
        for mailing in self:
            traces = self.env['mailing.trace'].search([('mass_mailing_id', '=', mailing.id)])
            mailing.whatsapp_sent_count = len(traces.filtered(lambda t: t.whatsapp_status in ['sent', 'delivered', 'read']))
            mailing.whatsapp_delivered_count = len(traces.filtered(lambda t: t.whatsapp_status in ['delivered', 'read']))
            mailing.whatsapp_read_count = len(traces.filtered(lambda t: t.whatsapp_status == 'read'))
            mailing.whatsapp_failed_count = len(traces.filtered(lambda t: t.whatsapp_status == 'failed'))

    def _get_active_subscription(self):
        """Busca assinatura de WhatsApp ativa associada à empresa do usuário"""
        company = (
            (self.whatsapp_account_id and self.whatsapp_account_id.company_id)
            or (hasattr(self, 'company_id') and self.company_id)
            or self.env.company
        )
        return self.env['whatsapp.subscription'].sudo().search([
            ('company_id', '=', company.id),
            ('state', '=', 'active')
        ], limit=1)

    def action_test_whatsapp(self):
        self.ensure_one()
        return {
            'name': _('Enviar Teste de WhatsApp'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.mailing.whatsapp.test',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_mailing_id': self.id,
                'default_whatsapp_account_id': self.whatsapp_account_id.id,
                'default_whatsapp_template_id': self.whatsapp_template_id.id,
            }
        }

    def action_send_whatsapp_now(self):
        for mailing in self:
            if not mailing.whatsapp_account_id or not mailing.whatsapp_template_id:
                raise UserError(_("Selecione uma conta de WhatsApp e um template aprovado antes de disparar."))
            
            # Validação de Assinatura & Quota
            sub = mailing._get_active_subscription()
            recipients = mailing._get_whatsapp_recipients()
            if sub:
                sub.check_can_send(len(recipients))

            # Gera os traces se não existirem
            mailing._create_whatsapp_traces()
            mailing.write({'state': 'sending'})
            # Processa o primeiro lote
            mailing._process_whatsapp_queue(batch_limit=50)

    def action_put_in_queue(self):
        whatsapp_mailings = self.filtered(lambda m: m.mailing_type == 'whatsapp')
        for mailing in whatsapp_mailings:
            if not mailing.whatsapp_account_id or not mailing.whatsapp_template_id:
                raise UserError(_("Selecione uma conta de WhatsApp e um template aprovado antes de colocar na fila."))
            
            # Validação de Quota
            sub = mailing._get_active_subscription()
            recipients = mailing._get_whatsapp_recipients()
            if sub:
                sub.check_can_send(len(recipients))

            mailing._create_whatsapp_traces()
            mailing.write({'state': 'in_queue'})
        return super(MailingMailing, self - whatsapp_mailings).action_put_in_queue()

    def _create_whatsapp_traces(self):
        self.ensure_one()
        TraceModel = self.env['mailing.trace']
        recipients = self._get_whatsapp_recipients()

        existing_traces = TraceModel.search([('mass_mailing_id', '=', self.id)])
        existing_res_ids = set(existing_traces.mapped('res_id'))
        existing_phones = set(''.join(filter(str.isdigit, p or '')) for p in existing_traces.mapped('whatsapp_recipient_number'))

        traces_to_create = []
        for target in recipients:
            target_phone_clean = ''.join(filter(str.isdigit, target.get('phone') or ''))
            if target['res_id'] in existing_res_ids or (target_phone_clean and target_phone_clean in existing_phones):
                continue
            if target_phone_clean:
                existing_phones.add(target_phone_clean)

            traces_to_create.append({
                'mass_mailing_id': self.id,
                'model': self.mailing_model_real,
                'res_id': target['res_id'],
                'trace_type': 'whatsapp',
                'whatsapp_account_id': self.whatsapp_account_id.id,
                'whatsapp_recipient_number': target['phone'],
                'whatsapp_status': 'outgoing',
            })

        if traces_to_create:
            TraceModel.create(traces_to_create)

    def _get_whatsapp_recipients(self):
        self.ensure_one()
        records = self._get_recipients()
        recipients = []
        
        for record in records:
            phone_raw = False
            if hasattr(record, 'mobile_whatsapp') and record.mobile_whatsapp:
                phone_raw = record.mobile_whatsapp
            elif hasattr(record, 'mobile') and record.mobile:
                phone_raw = record.mobile
            elif hasattr(record, 'phone') and record.phone:
                phone_raw = record.phone

            if not phone_raw:
                continue

            sanitized_phone = self.env['mailing.contact']._sanitize_whatsapp_number(
                phone_raw,
                getattr(record, 'country_id', False) and record.country_id.code or 'BR'
            )

            if sanitized_phone:
                recipients.append({
                    'res_id': record.id,
                    'record': record,
                    'phone': sanitized_phone,
                })

        return recipients

    @api.model
    def _cron_process_whatsapp_queue(self):
        """Método chamado pelo Scheduled Action (ir.cron) para disparar lotes pendentes"""
        active_mailings = self.search([
            ('mailing_type', '=', 'whatsapp'),
            ('state', 'in', ['in_queue', 'sending'])
        ])
        for mailing in active_mailings:
            mailing._process_whatsapp_queue(batch_limit=50)

    def _process_whatsapp_queue(self, batch_limit=50):
        self.ensure_one()
        TraceModel = self.env['mailing.trace']
        pending_traces = TraceModel.search([
            ('mass_mailing_id', '=', self.id),
            ('whatsapp_status', '=', 'outgoing')
        ], limit=batch_limit)

        if not pending_traces:
            if self.state in ['in_queue', 'sending']:
                self.write({'state': 'done'})
            return

        account = self.whatsapp_account_id
        template = self.whatsapp_template_id
        api_version = account._get_api_version()
        url = f"https://graph.facebook.com/{api_version}/{account.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {account.token.strip()}",
            "Content-Type": "application/json"
        }

        blacklisted_records = self.env['phone.blacklist'].sudo().search([])
        blacklisted_numbers = set(blacklisted_records.mapped('number'))

        delay = float(self.env['ir.config_parameter'].sudo().get_param('marketing_whatsapp.delay_between_messages', 0.1))
        sub = self._get_active_subscription()
        sent_success_count = 0

        for trace in pending_traces:
            dest_phone = trace.whatsapp_recipient_number
            clean_digits = ''.join(c for c in dest_phone if c.isdigit())

            # Checagem de Blacklist
            if dest_phone in blacklisted_numbers or f"+{clean_digits}" in blacklisted_numbers:
                trace.write({
                    'whatsapp_status': 'canceled',
                    'whatsapp_error_message': 'Número presente na lista de descadastro (Blacklist).'
                })
                continue

            target_record = self.env[trace.model].browse(trace.res_id) if trace.model and trace.res_id else False
            payload = self._build_meta_payload(account, template, clean_digits, target_record)

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=12)
                res_data = response.json()

                if response.status_code in [200, 201]:
                    messages = res_data.get('messages', [])
                    wamid = messages[0].get('id') if messages else False
                    trace.write({
                        'whatsapp_status': 'sent',
                        'whatsapp_message_id': wamid,
                        'whatsapp_sent_date': fields.Datetime.now(),
                        'whatsapp_error_message': False,
                    })
                    sent_success_count += 1
                else:
                    err = res_data.get('error', {})
                    err_code = err.get('code')
                    # Meta Cloud API: 131056 = Business conversation limit reached
                    # 131048 = Business account conversation limit reached
                    if err_code in [131056, 131048]:
                        _logger.warning("Limite diário de conversas da Meta atingido para %s (Tier limit). Pausando lote.", account.name)
                        self.message_post(body=_(
                            "⚠️ <b>Limite Diário da Meta Atingido (Tier 1 - 1.000 msgs/24h)</b>.<br/>"
                            "Os disparos foram pausados preventivamente para manter a alta qualidade do número.<br/>"
                            "A fila será retomada automaticamente na próxima janela ou após a Meta liberar o Tier 2."
                        ))
                        break
                    else:
                        trace.write({
                            'whatsapp_status': 'failed',
                            'whatsapp_error_code': str(err_code),
                            'whatsapp_error_message': err.get('message', response.text),
                        })

            except requests.exceptions.RequestException as e:
                trace.write({
                    'whatsapp_status': 'failed',
                    'whatsapp_error_message': f"Erro de conexão: {str(e)}"
                })

            if delay > 0:
                time.sleep(delay)

        # Atualiza consumo no plano de assinatura
        if sub and sent_success_count > 0:
            sub.register_sent_messages(count=sent_success_count)

        remaining = TraceModel.search_count([
            ('mass_mailing_id', '=', self.id),
            ('whatsapp_status', '=', 'outgoing')
        ])
        if remaining == 0:
            self.write({'state': 'done'})

    def _build_meta_payload(self, account, template, clean_phone, target_record=False):
        components = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')

        if template.template_type == 'carousel' and template.card_ids:
            # 1. Estrutura de Carrossel Meta Cloud API v20+
            cards_payload = []
            for c_idx, card in enumerate(template.card_ids):
                card_components = []
                # Mídia do Cartão (Header)
                card_media_url = card.header_media_url
                if not card_media_url and card.header_attachment_id:
                    card_media_url = f"{base_url}/web/content/{card.header_attachment_id.id}"

                if card_media_url:
                    card_components.append({
                        "type": "header",
                        "parameters": [{
                            "type": card.header_type,
                            card.header_type: {"link": card_media_url}
                        }]
                    })

                # Botões do Cartão
                for b_idx, btn in enumerate(card.button_ids):
                    if btn.button_type == 'URL' and btn.url_type == 'dynamic':
                        # Interpolação de URL dinâmica com ID do destinatário ou UTM
                        contact_id = getattr(target_record, 'id', '1')
                        card_components.append({
                            "type": "button",
                            "sub_type": "url",
                            "index": b_idx,
                            "parameters": [{
                                "type": "text",
                                "text": str(contact_id)
                            }]
                        })
                    elif btn.button_type == 'QUICK_REPLY' and btn.payload:
                        card_components.append({
                            "type": "button",
                            "sub_type": "quick_reply",
                            "index": b_idx,
                            "parameters": [{
                                "type": "payload",
                                "payload": btn.payload
                            }]
                        })

                cards_payload.append({
                    "card_index": c_idx,
                    "components": card_components
                })

            components.append({
                "type": "carousel",
                "cards": cards_payload
            })

            # Se houver corpo de texto na mensagem que acompanha o carrossel
            if template.body_variables_count > 0:
                body_params = []
                for i in range(1, template.body_variables_count + 1):
                    val = self._extract_variable_value(i, target_record)
                    body_params.append({
                        "type": "text",
                        "text": str(val or '')
                    })
                components.insert(0, {
                    "type": "body",
                    "parameters": body_params
                })

        else:
            # 2. Estrutura de Mensagem Padrão (Texto / Mídia)
            if template.header_type in ['image', 'document', 'video']:
                media_param = {}
                if self.whatsapp_media_url:
                    media_param = {"link": self.whatsapp_media_url}
                elif self.whatsapp_media_attachment_id:
                    media_url = f"{base_url}/web/content/{self.whatsapp_media_attachment_id.id}"
                    media_param = {"link": media_url}

                if media_param:
                    components.append({
                        "type": "header",
                        "parameters": [{
                            "type": template.header_type,
                            template.header_type: media_param
                        }]
                    })

            if template.body_variables_count > 0:
                body_params = []
                for i in range(1, template.body_variables_count + 1):
                    val = self._extract_variable_value(i, target_record)
                    body_params.append({
                        "type": "text",
                        "text": str(val or '')
                    })
                components.append({
                    "type": "body",
                    "parameters": body_params
                })

            # Botões dinâmicos do template principal
            for b_idx, btn in enumerate(template.button_ids):
                if btn.button_type == 'URL' and btn.url_type == 'dynamic':
                    contact_id = getattr(target_record, 'id', '1')
                    components.append({
                        "type": "button",
                        "sub_type": "url",
                        "index": b_idx,
                        "parameters": [{
                            "type": "text",
                            "text": str(contact_id)
                        }]
                    })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template.name,
                "language": {
                    "code": template.language
                }
            }
        }
        if components:
            payload["template"]["components"] = components

        return payload

    def _extract_variable_value(self, index, record):
        if not record:
            return f"Valor {index}"
        
        field_choice = getattr(self, f'whatsapp_var{index}_field', False) if index in [1, 2, 3] else 'name'
        if not field_choice:
            field_choice = 'name'

        if field_choice == 'name':
            return getattr(record, 'name', '') or getattr(record, 'contact_name', '') or 'Cliente'
        elif field_choice == 'company_name':
            return getattr(record, 'company_name', '') or getattr(record, 'partner_name', '') or (record.partner_id.name if hasattr(record, 'partner_id') and record.partner_id else '') or ''
        elif field_choice == 'custom_var1' and hasattr(record, 'custom_var1'):
            return record.custom_var1 or ''
        elif field_choice == 'custom_var2' and hasattr(record, 'custom_var2'):
            return record.custom_var2 or ''
        elif field_choice == 'email':
            return getattr(record, 'email', '') or getattr(record, 'email_from', '') or ''
        return ''

    def action_view_whatsapp_traces(self):
        self.ensure_one()
        return {
            'name': _('Rastreamento de Mensagens'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'mailing.trace',
            'domain': [('mass_mailing_id', '=', self.id)],
            'context': dict(self._context, default_mass_mailing_id=self.id),
        }
