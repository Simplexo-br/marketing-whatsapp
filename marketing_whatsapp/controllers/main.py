# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, fields
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class WhatsAppWebhookController(http.Controller):

    @http.route('/whatsapp/webhook', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def whatsapp_webhook(self, **kwargs):
        # 1. Handshake de Verificação da Meta (GET)
        if request.httprequest.method == 'GET':
            mode = kwargs.get('hub.mode')
            verify_token = kwargs.get('hub.verify_token')
            challenge = kwargs.get('hub.challenge')

            configured_token = request.env['ir.config_parameter'].sudo().get_param(
                'marketing_whatsapp.webhook_verify_token',
                'AIOS_MARKETING_WHATSAPP_TOKEN'
            )

            if mode == 'subscribe' and verify_token == configured_token:
                _logger.info("WhatsApp Webhook verificado com sucesso pela Meta.")
                return Response(challenge, status=200, content_type='text/plain')
            else:
                _logger.warning("Falha na verificação do WhatsApp Webhook: Token inválido (%s vs %s)", verify_token, configured_token)
                return Response("Forbidden", status=403)

        # 2. Recebimento de Eventos e Status (POST)
        elif request.httprequest.method == 'POST':
            try:
                raw_data = request.httprequest.data
                payload = json.loads(raw_data.decode('utf-8'))
            except Exception as e:
                _logger.error("Erro ao decodificar payload do Webhook: %s", str(e))
                return Response("Bad Request", status=400)

            # Processa entradas do WhatsApp
            entries = payload.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    field_name = change.get('field')

                    # A. Atualização de Status das Mensagens (sent, delivered, read, failed)
                    if 'statuses' in value:
                        self._handle_statuses(value.get('statuses', []))

                    # B. Mensagens Recebidas / Respostas (Detecção de Opt-Out / STOP)
                    if 'messages' in value:
                        self._handle_incoming_messages(value.get('messages', []))

                    # C. Atualização de Quality Rating do Número de Telefone
                    if field_name == 'phone_number_quality_update':
                        self._handle_quality_update(value)

            return Response("EVENT_RECEIVED", status=200)

    def _handle_statuses(self, statuses):
        TraceModel = request.env['mailing.trace'].sudo()
        for status_obj in statuses:
            wamid = status_obj.get('id')
            status = status_obj.get('status')  # sent, delivered, read, failed
            recipient_id = status_obj.get('recipient_id')
            errors = status_obj.get('errors', [])

            trace = TraceModel.search([('whatsapp_message_id', '=', wamid)], limit=1)
            if not trace:
                continue

            vals = {}
            if status == 'delivered':
                vals['whatsapp_status'] = 'delivered'
                vals['whatsapp_delivered_date'] = fields.Datetime.now()
            elif status == 'read':
                vals['whatsapp_status'] = 'read'
                vals['whatsapp_read_date'] = fields.Datetime.now()
            elif status == 'failed':
                vals['whatsapp_status'] = 'failed'
                if errors:
                    err = errors[0]
                    vals['whatsapp_error_code'] = str(err.get('code'))
                    vals['whatsapp_error_message'] = err.get('message', err.get('title', 'Falha no envio'))

            if vals:
                trace.write(vals)

    def _handle_incoming_messages(self, messages):
        auto_blacklist = request.env['ir.config_parameter'].sudo().get_param('marketing_whatsapp.auto_blacklist_on_stop', 'True') == 'True'
        if not auto_blacklist:
            return

        opt_out_keywords = ['SAIR', 'STOP', 'CANCELAR', 'PARAR', 'DESCADASTRO', 'NÃO QUERO', 'NAO QUERO', 'REMOVER']
        BlacklistModel = request.env['phone.blacklist'].sudo()

        for msg in messages:
            sender_number = msg.get('from')
            msg_type = msg.get('type')
            text_content = ""

            if msg_type == 'text':
                text_content = msg.get('text', {}).get('body', '').strip().upper()
            elif msg_type == 'button':
                text_content = msg.get('button', {}).get('text', '').strip().upper()
            elif msg_type == 'interactive':
                interactive_type = msg.get('interactive', {}).get('type')
                if interactive_type == 'button_reply':
                    text_content = msg.get('interactive', {}).get('button_reply', {}).get('title', '').strip().upper()

            # Checa se o texto corresponde a um pedido de opt-out
            if any(kw in text_content for kw in opt_out_keywords):
                formatted_num = f"+{sender_number}" if not sender_number.startswith('+') else sender_number
                _logger.info("Opt-out detectado via WhatsApp para %s. Adicionando ao phone.blacklist.", formatted_num)
                try:
                    if not BlacklistModel.search([('number', '=', formatted_num)], limit=1):
                        BlacklistModel._add([formatted_num])
                except Exception as e:
                    _logger.error("Erro ao adicionar número %s à blacklist: %s", formatted_num, str(e))

    def _handle_quality_update(self, value):
        AccountModel = request.env['whatsapp.account'].sudo()
        display_phone = value.get('display_phone_number')
        current_limit = value.get('current_limit')
        new_status = value.get('event')  # e.g. RED, YELLOW, GREEN

        account = AccountModel.search([('phone_number', 'ilike', display_phone)], limit=1)
        if account and new_status in ['GREEN', 'YELLOW', 'RED']:
            account.write({
                'quality_rating': new_status,
                'messaging_limit_tier': current_limit or account.messaging_limit_tier
            })
            account.message_post(body=f"Alerta da Meta: Classificação de qualidade atualizada para {new_status}.")
