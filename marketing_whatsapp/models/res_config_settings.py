# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_default_account_id = fields.Many2one(
        'whatsapp.account',
        string="Conta Padrão de WhatsApp",
        config_parameter='marketing_whatsapp.default_account_id',
        help="Conta padrão utilizada para disparo de campanhas caso não seja informada explicitamente."
    )
    whatsapp_api_version = fields.Char(
        string="Versão da Graph API Meta",
        default="v20.0",
        config_parameter='marketing_whatsapp.api_version',
        help="Versão da Meta Graph API utilizada nas chamadas (ex: v20.0)."
    )
    whatsapp_webhook_verify_token = fields.Char(
        string="Token de Verificação do Webhook",
        config_parameter='marketing_whatsapp.webhook_verify_token',
        default="AIOS_MARKETING_WHATSAPP_TOKEN",
        help="Token de segurança configurado no painel da Meta Developers para validação do Webhook."
    )
    whatsapp_batch_size = fields.Integer(
        string="Tamanho do Lote por Execução",
        default=50,
        config_parameter='marketing_whatsapp.batch_size',
        help="Quantidade de mensagens enviadas por ciclo de cron (Pacing Anti-Ban)."
    )
    whatsapp_delay_between_messages = fields.Float(
        string="Intervalo entre Envios (segundos)",
        default=0.2,
        config_parameter='marketing_whatsapp.delay_between_messages',
        help="Pequena pausa entre requisições para evitar picos de vazão (Throughput MPS)."
    )
    whatsapp_auto_blacklist_on_stop = fields.Boolean(
        string="Adicionar à Blacklist ao receber 'SAIR' / 'STOP'",
        default=True,
        config_parameter='marketing_whatsapp.auto_blacklist_on_stop',
        help="Se ativado, adiciona automaticamente o número de telefone ao phone.blacklist quando o cliente solicitar descadastro."
    )
