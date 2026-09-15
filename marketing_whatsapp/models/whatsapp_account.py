# -*- coding: utf-8 -*-
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WhatsAppAccount(models.Model):
    _name = 'whatsapp.account'
    _description = 'Conta WhatsApp Business (Meta Cloud API)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nome da Conta", required=True, tracking=True)
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.company)
    phone_number = fields.Char(string="Número de Telefone", tracking=True, help="Número no formato internacional (ex: +55 11 99999-8888)")
    phone_number_id = fields.Char(string="Phone Number ID", required=True, tracking=True, help="ID do número fornecido pela Meta Cloud API.")
    waba_id = fields.Char(string="WABA ID (WhatsApp Business Account)", required=True, tracking=True, help="ID da Conta WhatsApp Business.")
    token = fields.Char(string="Token de Acesso Permanente", required=True, tracking=True, help="System User Token gerado no Meta Business Manager.")
    app_id = fields.Char(string="App ID", default="1488457783279199")
    business_id = fields.Char(string="Business ID", default="4045641195567198")

    status = fields.Selection([
        ('disconnected', 'Desconectado'),
        ('connected', 'Conectado'),
        ('error', 'Erro de Autenticação')
    ], string="Status da Conexão", default='disconnected', readonly=True, tracking=True)

    quality_rating = fields.Selection([
        ('UNKNOWN', 'Desconhecido'),
        ('GREEN', '🟢 Alta Qualidade (Verde)'),
        ('YELLOW', '🟡 Média Qualidade (Amarelo)'),
        ('RED', '🔴 Baixa Qualidade (Vermelho - Risco)'),
    ], string="Classificação de Qualidade", default='UNKNOWN', readonly=True, tracking=True)

    messaging_limit_tier = fields.Selection([
        ('TIER_250', '250 conversas / 24h'),
        ('TIER_1K', '1.000 conversas / 24h (Tier 1)'),
        ('TIER_10K', '10.000 conversas / 24h (Tier 2)'),
        ('TIER_100K', '100.000 conversas / 24h (Tier 3)'),
        ('TIER_UNLIMITED', 'Ilimitado (Tier 4)'),
    ], string="Limite de Envio Diário", default='TIER_1K', readonly=True, tracking=True)
    daily_limit = fields.Integer(string="Limite Diário Numérico", compute='_compute_daily_limit')

    @api.depends('messaging_limit_tier')
    def _compute_daily_limit(self):
        tier_map = {
            'TIER_250': 250,
            'TIER_1K': 1000,
            'TIER_10K': 10000,
            'TIER_100K': 100000,
            'TIER_UNLIMITED': 999999,
        }
        for record in self:
            record.daily_limit = tier_map.get(record.messaging_limit_tier, 1000)

    last_connection_test = fields.Datetime(string="Último Teste de Conexão", readonly=True)
    error_message = fields.Text(string="Mensagem de Erro", readonly=True)
    template_ids = fields.One2many('whatsapp.template', 'account_id', string="Templates Aprovados")
    template_count = fields.Integer(string="Total de Templates", compute='_compute_template_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id') or self.env.company.id
            sub = self.env['whatsapp.subscription'].sudo().search([
                ('company_id', '=', company_id),
                ('state', '=', 'active')
            ], limit=1)
            if sub and sub.plan_id and sub.plan_id.max_whatsapp_accounts > 0:
                current_accounts_count = self.search_count([('company_id', '=', company_id)])
                if current_accounts_count >= sub.plan_id.max_whatsapp_accounts:
                    raise UserError(_(
                        "Limite de contas atingido para o plano %s (Máximo: %d contas).\n"
                        "Faça upgrade para o Plano Pro ou Enterprise para adicionar mais números."
                    ) % (sub.plan_id.name, sub.plan_id.max_whatsapp_accounts))
        return super(WhatsAppAccount, self).create(vals_list)

    @api.depends('template_ids')
    def _compute_template_count(self):
        for record in self:
            record.template_count = len(record.template_ids)

    def _get_api_version(self):
        return self.env['ir.config_parameter'].sudo().get_param('marketing_whatsapp.api_version', 'v20.0')

    def action_test_connection(self):
        self.ensure_one()
        api_version = self._get_api_version()
        url = f"https://graph.facebook.com/{api_version}/{self.phone_number_id}"
        headers = {
            "Authorization": f"Bearer {self.token.strip()}",
            "Content-Type": "application/json"
        }
        params = {
            "fields": "verified_name,display_phone_number,quality_rating,messaging_limit_tier,code_verification_status"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            data = response.json()

            if response.status_code == 200:
                self.write({
                    'status': 'connected',
                    'quality_rating': data.get('quality_rating', 'UNKNOWN'),
                    'messaging_limit_tier': data.get('messaging_limit_tier', 'TIER_1K'),
                    'phone_number': data.get('display_phone_number', self.phone_number),
                    'last_connection_test': fields.Datetime.now(),
                    'error_message': False,
                })
                self.message_post(body=_(
                    "Conexão com Meta Cloud API testada com sucesso!<br/>"
                    "<b>Nome Verificado:</b> %s<br/>"
                    "<b>Número:</b> %s<br/>"
                    "<b>Qualidade:</b> %s<br/>"
                    "<b>Limite:</b> %s"
                ) % (
                    data.get('verified_name', 'N/A'),
                    data.get('display_phone_number', 'N/A'),
                    data.get('quality_rating', 'N/A'),
                    data.get('messaging_limit_tier', 'N/A')
                ))
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Conexão Estabelecida!'),
                        'message': _('Conexão com a Meta Cloud API verificada com sucesso.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                err_msg = data.get('error', {}).get('message', response.text)
                self.write({
                    'status': 'error',
                    'error_message': err_msg,
                    'last_connection_test': fields.Datetime.now()
                })
                raise UserError(_("Erro ao conectar à Meta API: %s") % err_msg)

        except requests.exceptions.RequestException as e:
            self.write({
                'status': 'error',
                'error_message': str(e),
                'last_connection_test': fields.Datetime.now()
            })
            raise UserError(_("Falha de comunicação com o servidor da Meta: %s") % str(e))

    def action_sync_templates(self):
        self.ensure_one()
        api_version = self._get_api_version()
        url = f"https://graph.facebook.com/{api_version}/{self.waba_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {self.token.strip()}",
            "Content-Type": "application/json"
        }
        params = {"limit": 100}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            data = response.json()

            if response.status_code != 200:
                raise UserError(_("Erro ao buscar templates na Meta: %s") % data.get('error', {}).get('message', response.text))

            templates_data = data.get('data', [])
            TemplateModel = self.env['whatsapp.template']
            ButtonModel = self.env['whatsapp.template.button']
            CardModel = self.env['whatsapp.template.card']
            synced_count = 0

            for tmpl in templates_data:
                name = tmpl.get('name')
                language = tmpl.get('language')
                status = tmpl.get('status', '').upper()
                category = tmpl.get('category', 'MARKETING').upper()
                meta_template_id = tmpl.get('id')

                template_type = 'standard'
                header_type = 'none'
                header_text = False
                body_text = False
                footer_text = False
                buttons_list = []
                cards_list = []

                for comp in tmpl.get('components', []):
                    comp_type = comp.get('type')
                    if comp_type == 'HEADER':
                        fmt = comp.get('format', 'TEXT').lower()
                        header_type = fmt
                        header_text = comp.get('text')
                    elif comp_type == 'BODY':
                        body_text = comp.get('text')
                    elif comp_type == 'FOOTER':
                        footer_text = comp.get('text')
                    elif comp_type == 'BUTTONS':
                        for btn in comp.get('buttons', []):
                            buttons_list.append({
                                'button_type': btn.get('type', 'QUICK_REPLY'),
                                'name': btn.get('text', ''),
                                'url': btn.get('url', ''),
                                'phone_number': btn.get('phone_number', '')
                            })
                    elif comp_type == 'CAROUSEL':
                        template_type = 'carousel'
                        for card_idx, card_obj in enumerate(comp.get('cards', []), 1):
                            c_header_type = 'image'
                            c_body = ''
                            c_buttons = []
                            for c_comp in card_obj.get('components', []):
                                c_type = c_comp.get('type')
                                if c_type == 'HEADER':
                                    c_header_type = c_comp.get('format', 'IMAGE').lower()
                                elif c_type == 'BODY':
                                    c_body = c_comp.get('text', '')
                                elif c_type == 'BUTTONS':
                                    for c_btn in c_comp.get('buttons', []):
                                        c_buttons.append({
                                            'button_type': c_btn.get('type', 'QUICK_REPLY'),
                                            'name': c_btn.get('text', ''),
                                            'url': c_btn.get('url', ''),
                                            'phone_number': c_btn.get('phone_number', '')
                                        })
                            cards_list.append({
                                'name': f"Cartão #{card_idx}",
                                'sequence': card_idx * 10,
                                'header_type': c_header_type if c_header_type in ['image', 'video'] else 'image',
                                'body_text': c_body,
                                'buttons': c_buttons
                            })

                existing = TemplateModel.search([
                    ('account_id', '=', self.id),
                    ('name', '=', name),
                    ('language', '=', language)
                ], limit=1)

                vals = {
                    'account_id': self.id,
                    'name': name,
                    'meta_template_id': meta_template_id,
                    'language': language,
                    'category': category if category in ['MARKETING', 'UTILITY', 'AUTHENTICATION'] else 'MARKETING',
                    'status': status if status in ['APPROVED', 'PENDING', 'REJECTED', 'PAUSED'] else 'PENDING',
                    'template_type': template_type,
                    'header_type': header_type if header_type in ['none', 'text', 'image', 'document', 'video'] else 'none',
                    'header_text': header_text,
                    'body_text': body_text or '',
                    'footer_text': footer_text,
                }

                if existing:
                    existing.write(vals)
                    record_tmpl = existing
                else:
                    record_tmpl = TemplateModel.create(vals)

                # Atualiza botões do template principal
                record_tmpl.button_ids.unlink()
                for btn_data in buttons_list:
                    btn_data['template_id'] = record_tmpl.id
                    ButtonModel.create(btn_data)

                # Atualiza cartões do carrossel se aplicável
                if template_type == 'carousel':
                    record_tmpl.card_ids.unlink()
                    for c_info in cards_list:
                        c_buttons = c_info.pop('buttons', [])
                        c_info['template_id'] = record_tmpl.id
                        new_card = CardModel.create(c_info)
                        for b_data in c_buttons:
                            b_data['card_id'] = new_card.id
                            ButtonModel.create(b_data)

                synced_count += 1

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Templates Sincronizados!'),
                    'message': _('%d templates foram sincronizados com sucesso da Meta.') % synced_count,
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            raise UserError(_("Falha ao sincronizar templates: %s") % str(e))

    @api.model
    def action_open_channels_management(self):
        """Abre a gestão de canais do AIOS se instalado, ou as contas de WhatsApp nativas."""
        if 'simplexo.aios.whatsapp.channel' in self.env:
            action = self.env.ref('simplexo_aios_whatsapp.action_aios_whatsapp_channels', raise_if_not_found=False)
            if action:
                return action.read()[0]
        return self.env.ref('marketing_whatsapp.action_whatsapp_account').read()[0]
