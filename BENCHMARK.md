# 📊 Benchmark de Mercado: Soluções de WhatsApp Marketing & Disparo em Massa

Este documento apresenta uma análise comparativa e de mercado detalhada entre as principais plataformas globais e nacionais de WhatsApp Marketing (**Brevo, Bird, Wati, ManyChat, Respond.io, SleekFlow, SocialHub, Odoo Enterprise**) e a solução desenhada para o módulo open-source **Marketing WhatsApp (`marketing_whatsapp`)** no **Odoo 18**.

---

## 1. Visão Geral dos Concorrentes Analisados

| Plataforma | Modelo de Negócio | Integração Odoo | Tipo de API / Conexão | Pontos Fortes | Pontos Fracos |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Marketing WhatsApp (Este Projeto)** | **Open-Source / Nativo Odoo 18** | **100% Nativo (Odoo 18 Community & Enterprise)** | **Meta Cloud API Oficial Direta (App AIOS)** | **Custo zero de mensalidade/markup (paga direto à Meta), integrado nativo ao CRM/Listas/Importação Excel, Anti-Ban Engine, Pacing inteligente.** | Exige configuração inicial da conta Meta Business / WABA pelo administrador. |
| **Brevo** (ex-Sendinblue) | SaaS + Créditos Pré-pagos | Parcial (via API externa / Zapier) | Meta Cloud API Oficial | Interface intuitiva, automação multicanal (Email + SMS + WhatsApp), gestão de consentimento. | Markup sobre a taxa da Meta, sem integração nativa ao CRM Odoo Community. |
| **Wati** | SaaS ($49-$299/mês) + Taxas Meta | Nenhuma direta (Webhook/Zapier) | Meta Cloud API Oficial | Foco exclusivo em WhatsApp, construtor no-code, caixa de entrada compartilhada para equipes. | Custo mensal em dólar por usuário, dados ficam isolados fora do ERP Odoo. |
| **ManyChat** | SaaS ($15-$150+/mês) | Nenhuma direta | Meta Cloud API Oficial | Líder em funis sociais (Instagram DMs + Click-to-WhatsApp Ads), automação visual drag-and-drop. | Foco em e-commerce B2C/Creators, não possui gestão de ERP corporativo/CRM B2B. |
| **Respond.io** | Enterprise SaaS ($79-$299+/mês) | Externa (API / Zapier) | Meta Cloud API Oficial | Roteamento avançado de suporte, automação de múltiplos canais (WhatsApp, Telegram, IG). | Preço elevado para PMEs, curva de implementação complexa. |
| **SleekFlow** | SaaS ($129+/mês) | Externa | Meta Cloud API Oficial | Social commerce, catálogo de produtos e links de pagamento no chat. | Custo proibitivo para pequenas empresas no Brasil, sem integração com faturamento Odoo. |
| **Bird** (MessageBird) | Enterprise SaaS + Mensalidade + API | Externa / Webhooks | Meta Cloud API Oficial / BSP | Alta capacidade de throughput (até 1.000 MPS), infraestrutura robusta. | Custo elevado para PMEs, curva de aprendizado alta, dependência de middleware. |
| **SocialHub** | SaaS Brasileiro (Mensalidade) | Nenhuma direta (planilhas / manual) | Web Scraping / QR Code / Não-oficial | Fácil para pequenas empresas, disparo rápido de listas. | **Alto risco de banimento** (conexão não-oficial), falta de integração nativa com ERP. |
| **Odoo Enterprise (Nativo)** | Licença Enterprise + IAP | Nativa (Odoo Enterprise) | Odoo IAP Proxy / Meta Cloud API | Integrado ao Chatter e CRM. | Restrito à versão paga Enterprise, custo adicional por mensagem via IAP com margem da Odoo. |

---

## 2. Matriz Comparativa de Funcionalidades Técnicas

| Funcionalidade | Wati | ManyChat | Brevo | Odoo Nativo (Ent.) | Marketing WhatsApp (Odoo 18) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **API Oficial Meta Cloud (WABA)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Risco de Banimento por API Não-Oficial** | Baixo | Baixo | Baixo | Baixo | **Zero (100% Cloud API v20+)** |
| **Importação de Planilha (Excel/CSV)** | ✅ | ✅ | ✅ | ⚠️ Via Contatos | ✅ **Wizard Dedicado (Nome, Empresa, Fone)** |
| **Segmentação Nativa com CRM / Leads** | ❌ | ❌ | ❌ | ✅ | ✅ **Filtro dinâmico Odoo CRM/Leads/Partners** |
| **Disparo de Imagens, Vídeos e Docs** | ✅ | ✅ | ✅ | ✅ | ✅ **Templates com Rich Media & Preview** |
| **Botões Interativos (Quick Reply / URL / STOP)** | ✅ | ✅ | ✅ | ✅ | ✅ **Botões Nativos Meta** |
| **Templates Carrossel (Múltiplos Cards)** | ✅ | ✅ | ⚠️ | ❌ | 🔄 **Roadmap Fase 2** |
| **WhatsApp Flows (Formulários Nativos no Chat)** | ✅ | ❌ | ❌ | ❌ | 🔄 **Roadmap Fase 3** |
| **Pacing & Throttle Inteligente (Anti-Ban)** | ✅ | ✅ | ✅ | ⚠️ Básico | ✅ **Motor Cron com Rate Limiter (MPS)** |
| **Gestão de Opt-Out / Blacklist Automática** | ✅ | ✅ | ✅ | ⚠️ | ✅ **Integração com `phone.blacklist`** |
| **Monitoramento do Quality Rating Meta** | ✅ | ✅ | ✅ | ❌ | ✅ **Webhook em Tempo Real (Verde/Amarelo/Vermelho)** |
| **Custo de Intermediação / Markup** | Sim ($$$) | Sim ($$$) | Sim ($$) | Sim (Créditos IAP) | **R$ 0,00 (Direto no cartão da Meta)** |

---

## 3. Principais Recursos Emergentes na Meta Cloud API

1. **WhatsApp Flows (Formulários Nativos no Chat):**
   - Permite que o cliente preencha formulários estruturados (agendamentos, orçamentos, pesquisas de satisfação) diretamente dentro do WhatsApp, sem abrir links externos no navegador, aumentando as taxas de conversão em até 3x.
2. **Mensagens em Carrossel (Carousel Templates):**
   - Exibição de até 10 cartões horizontais navegáveis, cada um com sua imagem, título descritivo e botão de ação (Call-to-Action).
3. **List Messages (Menus Interativos de até 10 opções):**
   - Pop-ups limpos para escolha de departamentos, categorias de produtos ou filiais.
4. **Rastreamento de Campanhas Click-to-WhatsApp Ads (CTWA):**
   - Identificação da origem do lead vindo de anúncios no Facebook e Instagram diretamente para a conversa do WhatsApp no Odoo CRM.
