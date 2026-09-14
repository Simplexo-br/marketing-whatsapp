# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WhatsAppSubscription(models.Model):
    _name = 'whatsapp.subscription'
    _description = 'Assinatura de Cliente - WhatsApp Marketing'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Código da Assinatura", required=True, default=lambda self: _('Nova Assinatura'), copy=False)
    partner_id = fields.Many2one('res.partner', string="Cliente / Empresa", required=True, tracking=True)
    plan_id = fields.Many2one('whatsapp.subscription.plan', string="Plano Contratado", required=True, tracking=True)
    company_id = fields.Many2one('res.company', string="Empresa Emissora", default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('active', '🟢 Ativa'),
        ('pending_payment', '🟡 Aguardando Pagamento'),
        ('suspended', '🔴 Suspensa por Inadimplência'),
        ('canceled', '⚪ Cancelada'),
    ], string="Status da Assinatura", default='draft', tracking=True)

    billing_interval = fields.Selection([
        ('monthly', 'Mensal'),
        ('yearly', 'Anual'),
    ], string="Ciclo de Cobrança", default='monthly', required=True, tracking=True)

    recurring_price = fields.Float(string="Valor Recorrente (R$)", compute='_compute_recurring_price', store=True, readonly=False)

    current_period_start = fields.Date(string="Início do Ciclo Atual", default=fields.Date.today)
    current_period_end = fields.Date(string="Fim do Ciclo Atual", compute='_compute_period_end', store=True, readonly=False)

    messages_limit = fields.Integer(string="Limite de Mensagens no Ciclo", related='plan_id.monthly_message_limit', readonly=True)
    messages_sent_period = fields.Integer(string="Mensagens Enviadas no Ciclo", default=0, tracking=True)
    messages_remaining = fields.Integer(string="Mensagens Restantes", compute='_compute_messages_remaining')
    usage_percentage = fields.Float(string="% de Consumo", compute='_compute_messages_remaining')

    auto_invoice = fields.Boolean(string="Gerar Fatura Automaticamente", default=True, help="Emite fatura e envia link de cobrança automaticamente no vencimento.")
    invoice_ids = fields.Many2many('account.move', string="Faturas Geradas", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nova Assinatura')) == _('Nova Assinatura'):
                vals['name'] = self.env['ir.sequence'].next_by_code('whatsapp.subscription') or f"SUB-WPP-{fields.Date.today().strftime('%Y%m%d')}"
        return super(WhatsAppSubscription, self).create(vals_list)

    @api.depends('plan_id', 'billing_interval')
    def _compute_recurring_price(self):
        for sub in self:
            if sub.plan_id:
                sub.recurring_price = sub.plan_id.yearly_price if sub.billing_interval == 'yearly' else sub.plan_id.monthly_price
            else:
                sub.recurring_price = 0.0

    @api.depends('current_period_start', 'billing_interval')
    def _compute_period_end(self):
        for sub in self:
            if sub.current_period_start:
                if sub.billing_interval == 'yearly':
                    sub.current_period_end = sub.current_period_start + timedelta(days=365)
                else:
                    sub.current_period_end = sub.current_period_start + timedelta(days=30)

    @api.depends('messages_sent_period', 'messages_limit')
    def _compute_messages_remaining(self):
        for sub in self:
            if sub.messages_limit == 0:  # Ilimitado
                sub.messages_remaining = 999999
                sub.usage_percentage = 0.0
            else:
                remaining = sub.messages_limit - sub.messages_sent_period
                sub.messages_remaining = max(0, remaining)
                sub.usage_percentage = min(100.0, round((sub.messages_sent_period / sub.messages_limit) * 100, 1)) if sub.messages_limit > 0 else 0.0

    def action_activate(self):
        for sub in self:
            sub.write({
                'state': 'active',
                'current_period_start': fields.Date.today()
            })
            sub.message_post(body=_("Assinatura ativada com sucesso. Plano: %s") % sub.plan_id.name)

    def action_suspend(self):
        for sub in self:
            sub.write({'state': 'suspended'})
            sub.message_post(body=_("Assinatura suspensa. Os disparos de WhatsApp foram pausados."))

    def action_cancel(self):
        for sub in self:
            sub.write({'state': 'canceled'})

    def action_generate_invoice(self):
        """Gera fatura de cliente no Odoo Faturamento (account.move)"""
        self.ensure_one()
        AccountMove = self.env['account.move']

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f"Assinatura Marketing WhatsApp - Plano {self.plan_id.name} ({'Anual' if self.billing_interval == 'yearly' else 'Mensal'})",
                'quantity': 1,
                'price_unit': self.recurring_price,
            })],
        }

        invoice = AccountMove.create(invoice_vals)
        self.write({'invoice_ids': [(4, invoice.id)]})

        return {
            'name': _('Fatura de Cobrança'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }

    @api.model
    def _cron_recurring_subscription_billing(self):
        """Cron diário: Emite cobranças para assinaturas vencendo e reseta quotas no início de novo ciclo"""
        today = fields.Date.today()
        subscriptions = self.search([('state', 'in', ['active', 'pending_payment'])])

        for sub in subscriptions:
            # 1. Checa se o ciclo terminou para resetar contador e renovar
            if sub.current_period_end and today >= sub.current_period_end:
                if sub.auto_invoice:
                    sub.action_generate_invoice()
                
                # Inicia novo ciclo
                sub.write({
                    'current_period_start': today,
                    'messages_sent_period': 0,
                })
                sub.message_post(body=_("Novo ciclo de faturamento iniciado. Quota de mensagens renovada."))

    def check_can_send(self, requested_count=1):
        """Verifica se a assinatura permite o envio da quantidade solicitada de mensagens"""
        self.ensure_one()
        if self.state != 'active':
            raise UserError(_("Não é possível realizar disparos: A assinatura de WhatsApp do cliente %s está com status '%s'.") % (
                self.partner_id.name, dict(self._fields['state'].selection).get(self.state)
            ))
        
        if self.messages_limit > 0 and (self.messages_sent_period + requested_count) > self.messages_limit:
            raise UserError(_(
                "Limite mensal do plano atingido!\n"
                "Plano: %s\n"
                "Limite mensal: %d mensagens\n"
                "Já enviadas no ciclo: %d\n"
                "Tentativa de envio: %d\n"
                "Saldo disponível: %d\n\n"
                "Por favor, faça upgrade para o Plano Pro ou Enterprise."
            ) % (
                self.plan_id.name, self.messages_limit, self.messages_sent_period, requested_count, self.messages_remaining
            ))
        return True

    def register_sent_messages(self, count=1):
        """Incrementa o contador de mensagens consumidas no ciclo"""
        self.ensure_one()
        self.write({'messages_sent_period': self.messages_sent_period + count})
