# 🚀 Marketing WhatsApp - Odoo 18 (Simplexo)

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://www.odoo.com)
[![Meta Cloud API](https://img.shields.io/badge/Meta%20Cloud%20API-v20%2B-green.svg)](https://developers.facebook.com/docs/whatsapp/cloud-api)
[![Anti-Ban Protection](https://img.shields.io/badge/Anti--Ban-Rate%20Limiter%20%26%20Pacing-orange.svg)]()
[![License](https://img.shields.io/badge/License-LGPL--3-purple.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)

Módulo completo, profissional e nativo para o **Odoo 18 (Community e Enterprise)** desenvolvido para criação, automação e disparo em massa de campanhas de **WhatsApp Marketing** através da **Meta Cloud API Oficial (v20+)**, com gestão de planos SaaS, faturamento integrado e motor anti-ban de alta performance.

---

## 🌟 Principais Diferenciais

* **Conexão Direta com a Meta Cloud API (WABA):** Risco zero de banimento de chip por uso de APIs não oficiais (Z-API, Evolution, Baileys). O cliente paga o custo oficial de conversa direto à Meta no cartão de crédito, sem markups ou cobranças intermediárias ocultas.
* **Templates em Carrossel (Fase 2 do Roadmap):** Suporte nativo para até 10 cartões interativos navegáveis na horizontal, cada um com sua imagem de destaque, texto e botões dinâmicos de Call-to-Action (URL personalizada com UTMs e Resposta Rápida).
* **Motor Anti-Ban & Pacing:** Fila assíncrona gerenciada por cron (`ir.cron`) com controle rígido de vazão (mensagens por minuto), respeito aos tiers da Meta (1k, 10k, 100k/dia) e monitoramento de Quality Rating em tempo real.
* **Gestão Automática de Opt-Out:** Reconhecimento em tempo real de mensagens de descadastro (`STOP`, `SAIR`, `2`, `CANCELAR`) via Webhook, sincronizando automaticamente com o `phone.blacklist` do Odoo.
* **Modelo Comercial SaaS Integrado:** 3 planos prontos (Starter, Pro, Enterprise) com limites mensais de mensagens, controle de cotas (metering) e faturamento automático gerando faturas (`account.move`) com QR Code Pix / Boleto.
* **Importador Dedicado de Planilhas:** Wizard com detecção inteligente de delimitadores CSV/XLSX, mapeamento flexível de colunas (Nome, Empresa, Telefone, Variáveis) e higienização para o formato internacional **E.164** via biblioteca `phonenumbers`.
* **Dashboard Executivo OWL:** Painel interativo nativo em OWL com gráficos e KPIs de entrega, visualização, taxa de resposta, saúde do canal e consumo de cotas.

---

## 🏛️ Arquitetura do Sistema

```mermaid
graph TD
    A[Usuário / Gestor de Marketing] -->|Cria Campanha / Segmentação| B(mailing.mailing - WhatsApp)
    B -->|Importa Planilhas / Filtra CRM| C[Lista de Destinatários]
    B -->|Verifica Cota| D[whatsapp.subscription]
    B -->|Fila de Disparo| E[ir.cron - _process_whatsapp_queue]
    
    subgraph "Motor Anti-Ban & Dispatch"
        E -->|Rate Limiter / Pacing| F[Meta Cloud API Endpoint]
        F -->|POST /v20.0/{phone_id}/messages| G((Servidores da Meta))
    end
    
    subgraph "Recepção de Eventos & Status"
        G -->|Status: sent, delivered, read, failed| H[Webhook Controller /whatsapp/webhook]
        G -->|Respostas / Opt-Out STOP| H
        H -->|Atualiza Traces & Métricas| I[mailing.trace]
        H -->|Auto-Bloqueio de Opt-Out| J[phone.blacklist]
    end
    
    subgraph "Painel de Controle"
        I --> K[Dashboard OWL Executivo]
    end
```

---

## 📦 Planos Comerciais SaaS

O módulo já traz configurados de fábrica 3 planos no faturamento:

| Plano | Limite Mensal de Mensagens | Contas Meta | Preço Mensal | Preço Anual |
| :--- | :---: | :---: | :---: | :---: |
| **Starter** | 5.000 msgs/mês | 1 Linha Oficial | R$ 149,00/mês | R$ 1.490,00/ano |
| **Pro** | 25.000 msgs/mês | 3 Linhas Oficiais | R$ 349,00/mês | R$ 3.490,00/ano |
| **Enterprise** | Ilimitado | Linhas Ilimitadas | R$ 799,00/mês | R$ 7.990,00/ano |

---

## 🛠️ Instalação e Configuração

### 1. Dependências do Sistema

Certifique-se de que o ambiente Odoo 18 possui as dependências Python instaladas:

```bash
pip install requests phonenumbers
```

### 2. Executando Localmente via Docker Compose

O repositório já inclui um ambiente pronto para desenvolvimento local com Odoo 18 e PostgreSQL 16:

```bash
# Iniciar o ambiente
docker compose up -d

# Acompanhar os logs
docker compose logs -f odoo
```

Acesse o Odoo em: `http://localhost:8069` (Usuário: `admin` / Senha: `admin`).

---

## ⚙️ Configuração da Meta Cloud API

1. Acesse o [Meta for Developers](https://developers.facebook.com/) e crie um App do tipo **Outro / Negócios**.
2. Adicione o produto **WhatsApp**.
3. No painel da API do WhatsApp:
   - Copie o **Phone Number ID**.
   - Copie o **WhatsApp Business Account ID (WABA ID)**.
4. No Meta Business Manager, em **Usuários do Sistema**, gere um **Token de Acesso Permanente** com permissões:
   - `whatsapp_business_management`
   - `whatsapp_business_messaging`
5. No Odoo, navegue até **Marketing WhatsApp > Configurações > Contas de WhatsApp (Meta)** e preencha os dados.
6. Clique em **Testar Conexão** para validar a integridade da comunicação e ler a classificação de qualidade do número.
7. Clique em **Sincronizar Templates da Meta** para baixar automaticamente todos os seus templates aprovados (incluindo Carrosséis e Mídia).

---

## 🔔 Configuração do Webhook

Configure o Webhook no painel da Meta para receber status de entrega e mensagens em tempo real:

* **URL de Retorno de Chamada:** `https://seu-dominio.com.br/whatsapp/webhook`
* **Token de Verificação:** `AIOS_MARKETING_WHATSAPP_TOKEN` (ou o valor definido nas Configurações Gerais do Odoo).
* **Campos da Assinatura:** Marque `messages` e `phone_number_quality_update`.

---

## 🧪 Execução de Testes Automatizados

Para rodar a suíte completa de testes unitários do módulo no Odoo 18:

```bash
python3 odoo-bin -c simplexo.conf -d simplexo --test-enable --stop-after-init -i marketing_whatsapp --test-tags=/marketing_whatsapp
```

---

## 🗺️ Roadmap de Evolução

- [x] **Fase 1 (Core):** Motor Meta Cloud API v20+, Anti-ban Pacing, Importador E.164, Dashboard OWL, Assinaturas SaaS e Opt-Out Automático.
- [x] **Fase 2 (Rich Media):** Templates em Carrossel (até 10 cards com botões e mídias), Botões de URL dinâmicos com UTM tracking.
- [ ] **Fase 3 (Interatividade Avançada):**
  - **WhatsApp Flows:** Formulários nativos no chat para orçamentos, agendamentos e pesquisas sem sair do app.
  - **Click-to-WhatsApp Ads (CTWA):** Rastreamento de conversão de anúncios do Instagram/Facebook Ads.

---

## 📄 Licença

Distribuído sob a licença **LGPL-3**. Desenvolvido pelo time **Simplexo / AIOS**.