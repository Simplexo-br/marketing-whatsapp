# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWhatsAppCampaign(TransactionCase):

    def setUp(self):
        super(TestWhatsAppCampaign, self).setUp()
        self.ContactModel = self.env['mailing.contact']
        self.WhatsAppAccountModel = self.env['whatsapp.account']
        self.WhatsAppTemplateModel = self.env['whatsapp.template']
        self.MailingModel = self.env['mailing.mailing']
        self.MailingListModel = self.env['mailing.list']

        # Cria conta de WhatsApp
        self.account = self.WhatsAppAccountModel.create({
            'name': 'AIOS Marketing Test Account',
            'phone_number_id': '100000000000001',
            'waba_id': '4045641195567198',
            'token': 'EAAB_TEST_TOKEN',
            'status': 'connected',
            'quality_rating': 'GREEN',
            'messaging_limit_tier': 'TIER_1K'
        })

        # Cria template aprovado
        self.template = self.WhatsAppTemplateModel.create({
            'name': 'oferta_especial_teste',
            'account_id': self.account.id,
            'language': 'pt_BR',
            'category': 'MARKETING',
            'status': 'APPROVED',
            'header_type': 'text',
            'header_text': 'Aviso Importante',
            'body_text': 'Olá {{1}}, confira as novidades para a empresa {{2}}!',
            'footer_text': 'Responda STOP para cancelar'
        })

        # Cria lista de contatos
        self.mailing_list = self.MailingListModel.create({
            'name': 'Lista Leads Teste'
        })

    def test_phone_sanitization(self):
        """Testa se o número de telefone brasileiro é corretamente sanitizado para o formato E.164"""
        sanitized_1 = self.ContactModel._sanitize_whatsapp_number('11 98765-4321', 'BR')
        self.assertEqual(sanitized_1, '+5511987654321')

        sanitized_2 = self.ContactModel._sanitize_whatsapp_number('+55 21 99999-8888', 'BR')
        self.assertEqual(sanitized_2, '+5521999998888')

    def test_template_variables_count(self):
        """Testa o cálculo automático da quantidade de variáveis dinâmicas no corpo"""
        self.assertEqual(self.template.body_variables_count, 2)

    def test_whatsapp_campaign_creation(self):
        """Testa a criação de campanha e geração da prévia visual"""
        mailing = self.MailingModel.create({
            'subject': 'Campanha de Teste WhatsApp',
            'mailing_type': 'whatsapp',
            'whatsapp_account_id': self.account.id,
            'whatsapp_template_id': self.template.id,
            'contact_list_ids': [(4, self.mailing_list.id)],
        })
        self.assertEqual(mailing.mailing_type, 'whatsapp')
        self.assertTrue(mailing.whatsapp_preview_html)
