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

    def test_carousel_template_and_payload(self):
        """Testa a criação de template de carrossel e a montagem do payload oficial da Meta Cloud API v20+"""
        CardModel = self.env['whatsapp.template.card']
        ButtonModel = self.env['whatsapp.template.button']

        carousel_template = self.WhatsAppTemplateModel.create({
            'name': 'carrossel_produtos_demo',
            'account_id': self.account.id,
            'template_type': 'carousel',
            'language': 'pt_BR',
            'category': 'MARKETING',
            'status': 'APPROVED',
            'body_text': 'Confira nossos destaques da semana:',
        })

        card1 = CardModel.create({
            'template_id': carousel_template.id,
            'sequence': 10,
            'name': 'Produto 1 - CRM Inteligente',
            'header_type': 'image',
            'header_media_url': 'https://simplexo.com.br/img/crm.png',
            'body_text': 'Aumente suas vendas com CRM integrado.',
        })

        ButtonModel.create({
            'card_id': card1.id,
            'name': 'Ver Oferta',
            'button_type': 'URL',
            'url_type': 'dynamic',
            'url': 'https://simplexo.com.br/crm/{{1}}',
        })

        card2 = CardModel.create({
            'template_id': carousel_template.id,
            'sequence': 20,
            'name': 'Produto 2 - ERP Simplexo',
            'header_type': 'image',
            'header_media_url': 'https://simplexo.com.br/img/erp.png',
            'body_text': 'Gestão completa para sua empresa.',
        })

        ButtonModel.create({
            'card_id': card2.id,
            'name': 'Falar com Consultor',
            'button_type': 'QUICK_REPLY',
            'payload': 'INTERESSE_ERP',
        })

        # Cria campanha para testar geração de payload
        mailing = self.MailingModel.create({
            'subject': 'Campanha Carrossel de Produtos',
            'mailing_type': 'whatsapp',
            'whatsapp_account_id': self.account.id,
            'whatsapp_template_id': carousel_template.id,
        })

        class MockContact:
            id = 42
            name = 'Roberto Dias'
            company_name = 'Dias Tech'

        payload = mailing._build_meta_payload(self.account, carousel_template, '5511987654321', MockContact())

        self.assertEqual(payload['messaging_product'], 'whatsapp')
        self.assertEqual(payload['type'], 'template')
        self.assertEqual(payload['template']['name'], 'carrossel_produtos_demo')

        components = payload['template']['components']
        carousel_comp = next((c for c in components if c.get('type') == 'carousel'), None)
        self.assertIsNotNone(carousel_comp, "Componente de carrossel deve estar presente no payload")

        cards = carousel_comp.get('cards', [])
        self.assertEqual(len(cards), 2, "Devem existir 2 cartões no payload de carrossel")
        self.assertEqual(cards[0]['card_index'], 0)
        self.assertEqual(cards[1]['card_index'], 1)

        # Checa botão dinâmico no card 1
        card1_btn = next((c for c in cards[0]['components'] if c.get('type') == 'button'), None)
        self.assertIsNotNone(card1_btn)
        self.assertEqual(card1_btn['sub_type'], 'url')
        self.assertEqual(card1_btn['parameters'][0]['text'], '42')

        # Checa botão quick reply com payload no card 2
        card2_btn = next((c for c in cards[1]['components'] if c.get('type') == 'button'), None)
        self.assertIsNotNone(card2_btn)
        self.assertEqual(card2_btn['sub_type'], 'quick_reply')
        self.assertEqual(card2_btn['parameters'][0]['payload'], 'INTERESSE_ERP')

    def test_contact_phoneless_protection(self):
        """Testa que contatos sem telefone não recebem status de envio/entrega/leitura ativo"""
        contact = self.ContactModel.create({
            'name': 'Contato Sem Telefone',
            'email': 'semtelefone@teste.com',
            'wa_status_delivered': True,
            'wa_status': 'delivered'
        })
        self.assertFalse(contact.wa_status_delivered, "Contato sem telefone não pode ter wa_status_delivered=True")
        self.assertEqual(contact.wa_status, 'not_sent', "Contato sem telefone deve ter wa_status='not_sent'")

        # Tentativa de escrita direta
        contact.write({
            'wa_status': 'delivered',
            'wa_status_delivered': True,
            'wa_status_read': True,
        })
        self.assertFalse(contact.wa_status_delivered)
        self.assertFalse(contact.wa_status_read)
        self.assertEqual(contact.wa_status, 'not_sent')

    def test_contact_deduplication_and_list_merge(self):
        """Testa a rotina de desduplicação: mesclagem de listas e remoção de registros redundantes"""
        ListModel = self.env['mailing.list']
        list_a = ListModel.create({'name': 'Lista A Teste'})
        list_b = ListModel.create({'name': 'Lista B Teste'})

        # Cria 2 contatos com o mesmo telefone em listas diferentes
        c1 = self.ContactModel.create({
            'name': 'Cliente Teste Duplicado 1',
            'mobile': '11988887777',
            'list_ids': [(4, list_a.id)],
        })
        c2 = self.ContactModel.create({
            'name': 'Cliente Teste Duplicado 2',
            'mobile': '+5511988887777',
            'company_name': 'Empresa Unificada',
            'list_ids': [(4, list_b.id)],
            'wa_status': 'read',
            'wa_status_read': True,
        })

        # Cria 1 contato sem telefone
        c3 = self.ContactModel.create({
            'name': 'Cliente Sem Telefone Deletar',
            'email': 'deletar@teste.com',
        })

        # Executa ação de higienização
        self.ContactModel.action_clean_duplicates_and_empty()

        # Verifica que c3 foi deletado
        self.assertFalse(c3.exists())

        # Verifica que apenas 1 contato existe com esse telefone
        remaining = self.ContactModel.search([('mobile_whatsapp', '=', '+5511988887777')])
        self.assertEqual(len(remaining), 1, "Deve existir exatamente 1 contato após a desduplicação")

        master = remaining[0]
        # Ambas as listas devem estar unificadas
        self.assertIn(list_a.id, master.list_ids.ids)
        self.assertIn(list_b.id, master.list_ids.ids)
        # O status mais avançado (read) deve ser mantido
        self.assertEqual(master.wa_status, 'read')
        self.assertTrue(master.wa_status_read)
        self.assertEqual(master.company_name, 'Empresa Unificada')

