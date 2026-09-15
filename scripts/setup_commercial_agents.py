# -*- coding: utf-8 -*-
import subprocess
import os
import base64

default_keys = [
    os.environ.get('SIMPLEXO_SSH_KEY'),
    os.path.expanduser('~/.ssh/simplexo_vm'),
    os.path.expanduser('~/.ssh/simplexo_gpt_desktop'),
    r'C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm',
]
ssh_key = next((k for k in default_keys if k and os.path.exists(k)), default_keys[-1])
bastion = 'fellipe_ramalho@35.224.220.67'
internal_server = 'fellipe_ramalho@34.45.88.55'

remote_script = '''# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    Agent = env['simplexo.ai.agent']
    
    # Prompt de Alto Desempenho para o Atendente Comercial SDR de Campanhas WhatsApp
    system_prompt_sdr = """Você é o Consultor Comercial Especialista & SDR da Simplexo Tecnologia (simplexo.com.br).
Sua missão é realizar o primeiro atendimento consultivo e acolhedor a clientes e empresários que responderam às nossas campanhas de WhatsApp.

OBJETIVOS PRINCIPAIS:
1. Acolher o contato com simpatia, naturalidade e energia positiva.
2. Entender o cenário atual e a real necessidade da empresa (se já emite NF-e/NFS-e/NFC-e, controle financeiro, PDV, gestão de vendas, etc.).
3. Apresentar de forma clara e irresistível as soluções da Simplexo.
4. Qualificar o lead e conduzi-lo para um teste prático, demonstração guiada ou fechamento.

REGRAS CRÍTICAS DE DETECÇÃO ANTI-BOT (NÃO RESPONDER ROBÔS):
- Se a mensagem recebida for uma resposta automática de WhatsApp Business (Exemplos: "Olá! Agradecemos sua mensagem. No momento estamos ausentes...", "Nosso horário de atendimento é de...", "Mensagem automática", "Selecione uma opção no menu:", "Obrigado pelo contato, logo responderemos"), você NÃO DEVE responder nada (retorne [SILENCE_BOT_DETECTED]) para evitar loop entre robôs.

COMO CONDUZIR A CONVERSA COM HUMANOS:
- Fale em Português do Brasil com tom profissional, acessível, seguro e prestativo.
- Responda mensagens curtas e objetivas (1 a 3 parágrafos breves), ideais para leitura rápida no WhatsApp.
- Se o cliente responder "1", "Sim", "Quero saber mais", "Como funciona?", "Qual o valor?":
  - Agradeça o interesse com entusiasmo.
  - Explique que o Simplexo ERP reúne Emissão Ilimitada de Notas Fiscais (NF-e, NFS-e, NFC-e), Frente de Caixa PDV, Gestão Financeira, Controle de Estoque e Automação de WhatsApp sem complicação.
  - Pergunte qual o segmento da empresa dele e qual a prioridade no momento (ex: "Qual o ramo da sua empresa? Vocês já utilizam algum sistema para emitir notas hoje?").
- Se o cliente pedir valores/preços:
  - Explique que temos planos acessíveis sob medida para o porte do negócio, sem taxa de adesão abusiva e com suporte humanizado.
  - Ofereça demonstrar o sistema ou enviar uma proposta personalizada.
- Se o cliente responder "2" ou pedir para cancelar/sair:
  - Seja educado e confirme: "Perfeito, já removemos seu contato da nossa lista de novidades. Desejamos muito sucesso ao seu negócio!"
"""

    # Provedor de IA padrão
    provider = env['simplexo.ai.provider'].search([('active', '=', True)], limit=1) or env['simplexo.ai.provider'].search([], limit=1)
    if not provider:
        provider = env['simplexo.ai.provider'].create({
            'name': 'Google Gemini (Oficial Simplexo)',
            'provider_type': 'gemini',
            'active': True
        })

    # Cria ou Atualiza o Agente Comercial SDR de Campanhas
    agent_vals = {
        'name': 'Atendente Comercial SDR — Inbound WhatsApp',
        'system_prompt': system_prompt_sdr,
        'temperature': 0.3,
        'active': True,
        'provider_id': provider.id,
    }

    
    # Verifica campos opcionais do modelo
    for f in ['agent_type', 'role', 'model_provider', 'model_name', 'is_active', 'description']:
        if f in Agent._fields:
            if f == 'agent_type' or f == 'role':
                agent_vals[f] = 'commercial'
            elif f == 'model_name':
                agent_vals[f] = 'gemini-2.5-flash'
            elif f == 'model_provider':
                agent_vals[f] = 'google_gemini'
            elif f == 'is_active':
                agent_vals[f] = True
            elif f == 'description':
                agent_vals[f] = 'Atendente Comercial SDR focado em qualificar e atender respostas de campanhas de WhatsApp, com filtro anti-bot.'

    existing = Agent.search([('name', '=', 'Atendente Comercial SDR — Inbound WhatsApp')], limit=1)
    if existing:
        existing.write(agent_vals)
        agent_id = existing.id
        print(f"Atualizado Agente ID {agent_id}: {existing.name}")
    else:
        new_agent = Agent.create(agent_vals)
        agent_id = new_agent.id
        print(f"Criado novo Agente ID {agent_id}: {new_agent.name}")

    # Também atualiza os agentes comerciais existentes no sistema (ID 3, 9, 18) para conterem a instrução Anti-Bot e foco em campanhas
    comm_agents = Agent.search([('id', 'in', [3, 9, 18])])
    for ca in comm_agents:
        ca.write({
            'system_prompt': system_prompt_sdr,
            'active': True
        })
        print(f"Atualizado Prompt Comercial com Anti-Bot para Agente ID {ca.id} ({ca.name})")

    cr.commit()
    print("Sucesso! Agentes comerciais criados e configurados no banco de dados.")
'''

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15',
    '-i', ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "{remote_cmd}"'
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
print(stdout)
if stderr:
    print('STDERR:', stderr)
