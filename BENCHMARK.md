# 📊 Benchmark de Mercado: Soluções de WhatsApp Marketing & Disparo em Massa

Este documento apresenta uma análise comparativa e de mercado detalhada entre as principais plataformas globais e nacionais de WhatsApp Marketing (Brevo, Bird, SocialHub, Odoo Enterprise) e a solução desenhada para o módulo open-source **Marketing WhatsApp (`marketing_whatsapp`)** no **Odoo 18**.

---

## 1. Visão Geral dos Concorrentes Analisados

| Plataforma | Modelo de Negócio | Integração Odoo | Tipo de API / Conexão | Pontos Fortes | Pontos Fracos |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Brevo** (ex-Sendinblue) | SaaS + Créditos Pré-pagos | Parcial (via API externa / Zapier) | Meta Cloud API Oficial | Interface intuitiva, automação multicanal (Email + SMS + WhatsApp), gestão de consentimento. | Markup sobre a taxa da Meta, sem integração nativa ao CRM Odoo Community. |
| **Bird** (MessageBird) | Enterprise SaaS + Mensalidade + API | Externa / Webhooks | Meta Cloud API Oficial / BSP | Alta capacidade de throughput (até 1.000 MPS), infraestrutura robusta e suporte omnicanal. | Custo elevado para PMEs, curva de aprendizado alta, dependência de middleware. |
| **SocialHub** | SaaS Brasileiro (Mensalidade) | Nenhuma direta (planilhas / manual) | Web Scraping / QR Code / API não oficial / Parcial WABA | Fácil para pequenas empresas, disparo rápido de listas. | Alto risco de banimento (se usar QR Code/não-oficial), falta de integração nativa com ERP. |
| **Odoo Enterprise (Nativo)** | Licença Odoo Enterprise + IAP | Nativa (Odoo Enterprise) | Odoo IAP Proxy / Meta Cloud API | Totalmente integrado ao Chatter e CRM. | Restrito à versão Enterprise paga, custo por mensagem via IAP com margem Odoo, recursos de mailing limitados em comparação ao email/SMS. |
| **Marketing WhatsApp (Este Projeto)** | **Open-Source / Nativo Odoo 18** | **100% Nativo (Odoo 18 Community & Enterprise)** | **Meta Cloud API Oficial Direta (App AIOS)** | **Custo zero de mensalidade/markup (paga direto à Meta), integrado nativo ao CRM/Listas/Importação Excel, Anti-Ban Engine, Pacing inteligente.** | Exige configuração da conta Meta Business / WABA pelo administrador. |

---

## 2. Matriz Comparativa de Funcionalidades

| Funcionalidade | Brevo | Bird | SocialHub | Odoo Nativo (Ent.) | Marketing WhatsApp (Odoo 18) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **API Oficial Meta Cloud (WABA)** | ✅ | ✅ | ⚠️ Misto | ✅ | ✅ |
| **Risco de Banimento por Conexão Não-Oficial** | Baixo | Baixo | Alto | Baixo | **Zero (100% Cloud API v20+)** |
| **Importação de Planilha (Excel/CSV)** | ✅ | ✅ | ✅ | ⚠️ Via Contatos | ✅ **Wizard Dedicado (Nome, Empresa, Fone)** |
| **Segmentação Nativa com CRM / Leads** | ❌ | ❌ | ❌ | ✅ | ✅ **Filtro dinâmico Odoo CRM/Leads/Partners** |
| **Disparo de Imagens, Vídeos e Docs** | ✅ | ✅ | ✅ | ✅ | ✅ **Templates com Rich Media & Preview** |
| **Botões Interativos (Quick Reply / URL / Opt-out)** | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| **Pacing & Throttle Inteligente (Anti-Ban)** | ✅ (Meta) | ✅ | ❌ | ⚠️ Básico | ✅ **Motor Odoo Cron com Rate Limiter (MPS)** |
| **Gestão de Opt-Out / Blacklist Automática** | ✅ | ✅ | ❌ | ⚠️ | ✅ **Integração com `phone.blacklist`** |
| **Monitoramento do Quality Rating Meta** | ✅ | ✅ | ❌ | ❌ | ✅ **Webhook em Tempo Real (Verde/Amarelo/Vermelho)** |
| **Custo de Intermediação / Markup** | Sim ($$$) | Sim ($$$$) | Mensalidade fixa | Sim (Créditos IAP) | **R$ 0,00 (Direto no cartão da Meta)** |

---

## 3. Análise Detalhada dos Concorrentes

### 3.1. Brevo (Sendinblue)
- **Como funciona:** O usuário cria templates no painel da Brevo, importa listas CSV/Excel e agenda disparos.
- **Vantagens:** Excelente interface de validação visual e pré-visualização de mensagens.
- **Desvantagens para quem usa Odoo:** Os contatos do Odoo CRM precisam ser exportados ou sincronizados via API/Zapier, duplicando a base de dados e gerando custo duplicado de SaaS.

### 3.2. Bird (MessageBird)
- **Como funciona:** Foco em médias e grandes corporações, automação de jornada e alto volume de envio.
- **Vantagens:** Altíssima performance e relatórios detalhados de entrega.
- **Desvantagens:** Complexidade excessiva para equipes comerciais e marketing convencionais que só querem subir uma lista e disparar uma campanha no ERP.

### 3.3. SocialHub
- **Como funciona:** Focado no mercado brasileiro para pequenas empresas e marketing direto.
- **Desvantagens críticas:** Muitas soluções desse segmento utilizam emulação de WhatsApp Web (QR Code / Chromium), violando os Termos de Serviço da Meta e provocando o banimento imediato de números comerciais.
- **Lição para o nosso módulo:** O módulo Odoo deve usar **exclusivamente a Meta Cloud API oficial** do aplicativo AIOS aprovado.

---

## 4. Oportunidade e Diferencial do Módulo "Marketing WhatsApp"

1. **Mesma Experiência de Usuário (UX) do Odoo:**
   - O menu segue o padrão visual nativo: `Marketing por e-mail`, `Marketing por SMS` e `Marketing WhatsApp`.
   - Utiliza a estrutura consolidada de `mailing.mailing` e `mailing.list` do Odoo.
2. **Importação Rápida de Planilhas:**
   - Permite ao operador carregar arquivos `.xlsx` / `.csv` contendo colunas como `Nome`, `Empresa`, `WhatsApp` e criar listas de disparo instantaneamente no Odoo.
3. **Economia Financeira Máxima:**
   - Conexão direta entre o Odoo da empresa e a API Oficial da Meta (sem passar por BSPs que cobram mensalidades de centenas de dólares).
4. **Proteção Anti-Ban Rigorosa:**
   - Controle de taxa de envio (pacing), respeitando os tiers diários (1k, 10k, 100k) e o throughput de MPS (Messages Per Second).
   - Gerenciamento automático de pedidos de descadastro (`STOP` / `SAIR`), evitando denúncias de spam que derrubam o Quality Rating do número.
