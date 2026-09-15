# -*- coding: utf-8 -*-
{
    'name': 'Marketing WhatsApp',
    'version': '18.0.1.0.0',
    'category': 'Marketing/WhatsApp',
    'summary': 'Disparos em massa de campanhas de WhatsApp via Meta Cloud API Oficial com planos de assinatura, faturamento automático e proteção Anti-Ban',
    'description': """
Marketing WhatsApp para Odoo 18 (Comercialização Simplexo)
==========================================================
Módulo completo e profissional para criação e disparo em massa de campanhas de WhatsApp marketing através da API oficial da Meta (Cloud API v20+).

Principais Recursos:
-------------------
* Interface idêntica ao Marketing por E-mail e Marketing por SMS.
* Modelo Comercial SaaS: 3 Planos de Assinatura (Starter, Pro, Enterprise) com limites de mensagens e cobrança automática.
* Integração com Faturamento Odoo: Emissão automática de faturas de clientes e gestão de ciclo de renovação.
* Conexão direta com a Meta Cloud API (App AIOS) - sem custos adicionais de intermediários.
* Importador de planilhas Excel/CSV (Nome, Empresa, Telefone) com higienização internacional E.164.
* Segmentação flexível: Disparo para CRM (Leads/Oportunidades), Contatos/Parceiros ou Listas de Disparo.
* Suporte completo a Mídia Rica: Imagens, PDFs, Vídeos e Botões Interativos (Quick Reply, URL, Opt-Out).
* Motor Anti-Ban & Pacing: Controle de vazão (taxa de mensagens por minuto/hora), respeito aos limites diários de Tiers (1k, 10k, 100k) e monitoramento de Quality Rating.
* Webhook em tempo real: Recepção de status (Enviado, Entregue, Lido, Falha) e auto-cadastro de Opt-Out na Blacklist.
    """,
    'author': 'Simplexo / AIOS',
    'website': 'https://github.com/Simplexo-br/marketing-whatsapp',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'account',
        'mass_mailing',
        'phone_validation',
        'crm',
        'contacts',
    ],
    'external_dependencies': {
        'python': ['requests', 'phonenumbers'],
    },
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data & Cron
        'data/whatsapp_subscription_plan_data.xml',
        'data/ir_cron_data.xml',

        # Views
        'views/whatsapp_dashboard_views.xml',
        'views/whatsapp_subscription_views.xml',
        'views/whatsapp_template_views.xml',
        'views/whatsapp_account_views.xml',
        'views/mailing_mailing_views.xml',
        'views/mailing_contact_views.xml',
        'views/res_config_settings_views.xml',

        # Wizards
        'wizard/import_whatsapp_contacts_views.xml',
        'wizard/mailing_whatsapp_test_views.xml',

        # Menus (carregados por último para ter todas as ações disponíveis)
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'marketing_whatsapp/static/src/dashboard/**/*',
        ],
    },
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
