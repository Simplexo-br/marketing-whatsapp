# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestWhatsAppCampaign(TransactionCase):

    def setUp(self):
        super(TestWhatsAppCampaign, self).setUp()
        self.ContactModel = self.env['mailing.contact']
        self.WhatsAppAccountModel = self.env['whatsapp.account']
        self.WhatsAppTemplateModel = self.env['whatsapp.template']
        self.MailingModel = self.env['mailing.mailing']
        self.MailingListModel = self.env['mailing.list']
        self.PlanModel = self.env['whatsapp.subscription.plan']
        self.SubModel = self.env['whatsapp.subscription']
        self.PartnerModel = self.env['res.partner']

        # Cria plano Starter
        self.plan_starter = self.PlanModel.create({
            'name': 'Starter Teste',
            'code': 'starter',
            'monthly_price': 149.0,
            'monthly_message_limit': 100,
            'max_whatsapp_accounts': 1,
        })

        # Cria parceiro e assinatura
        self.partner = self.PartnerModel.create({
            'name': 'Empresa Cliente Teste LTDA',
            'email': 'cliente@teste.com'
        })

        self.subscription = self.SubModel.create({
            'partner_id': self.partner.id,
            'plan_id': self.plan_starter.id,
            'state': 'active',
            'messages_sent_period': 0,
        })

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

    def test_subscription_quota_enforcement(self):
        """Testa a trava de limite de mensagens da assinatura"""
        self.assertTrue(self.subscription.check_can_send(50))
        self.subscription.register_sent_messages(90)
        self.assertEqual(self.subscription.messages_remaining, 10)

        # Tentativa de enviar 20 mensagens quando restam apenas 10 deve disparar UserError
        with self.assertRaises(UserError):
            self.subscription.check_can_send(20)

    def test_subscription_invoice_generation(self):
        """Testa a geração automática de fatura de cliente no módulo financeiro"""
        action = self.subscription.action_generate_invoice()
        self.assertTrue(action.get('res_id'))
        invoice = self.env['account.move'].browse(action['res_id'])
        self.assertEqual(invoice.move_type, 'out_invoice')
        self.assertEqual(invoice.partner_id.id, self.partner.id)
        self.assertEqual(invoice.amount_total, 149.0)
