# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WhatsAppSubscriptionPlan(models.Model):
    _name = 'whatsapp.subscription.plan'
    _description = 'Plano de Assinatura WhatsApp Marketing'
    _order = 'sequence, id'

    name = fields.Char(string="Nome do Plano", required=True)
    code = fields.Selection([
        ('starter', 'Starter (Básico)'),
        ('pro', 'Pro (Crescimento)'),
        ('enterprise', 'Enterprise (Escala / Ilimitado)'),
    ], string="Código do Plano", required=True, default='starter')
    sequence = fields.Integer(string="Sequência", default=10)
    active = fields.Boolean(string="Ativo", default=True)

    monthly_price = fields.Float(string="Mensalidade (R$)", required=True, default=149.0)
    yearly_price = fields.Float(string="Anuidade com Desconto (R$)", default=1490.0)
    
    monthly_message_limit = fields.Integer(
        string="Limite Mensal de Mensagens",
        default=5000,
        help="Quantidade máxima de mensagens no ciclo mensal. Insira 0 para ilimitado."
    )
    max_whatsapp_accounts = fields.Integer(
        string="Máximo de Números Conectados",
        default=1,
        help="Quantidade máxima de contas/números oficiais do WhatsApp que o cliente pode conectar."
    )
    
    allow_rich_media = fields.Boolean(string="Permitir Mídia Rica (Imagens, PDFs, Vídeos)", default=True)
    allow_advanced_carousels = fields.Boolean(string="Permitir Templates em Carrossel & Flows", default=False)
    allow_custom_variables = fields.Boolean(string="Variáveis Ilimitadas em Planilhas", default=True)
    priority_support = fields.Boolean(string="Suporte Prioritário VIP", default=False)

    description = fields.Text(string="Descrição Comercial do Plano")
    subscription_count = fields.Integer(string="Assinantes Ativos", compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        for plan in self:
            plan.subscription_count = self.env['whatsapp.subscription'].search_count([
                ('plan_id', '=', plan.id),
                ('state', '=', 'active')
            ])
