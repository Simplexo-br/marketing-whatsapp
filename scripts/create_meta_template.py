# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import requests
import psycopg2
import configparser

cfg = configparser.ConfigParser()
cfg.read('/opt/odoo/conf/simplexo.conf')
db_user = cfg.get('options', 'db_user', fallback='simplexo')
db_password = cfg.get('options', 'db_password', fallback='')
db_host = cfg.get('options', 'db_host', fallback=False)
db_port = cfg.get('options', 'db_port', fallback=False)

conn_args = {'dbname': 'simplexo', 'user': db_user}
if db_password: conn_args['password'] = db_password
if db_host: conn_args['host'] = db_host
if db_port: conn_args['port'] = db_port

conn = psycopg2.connect(**conn_args)
cr = conn.cursor()
cr.execute("SELECT id, name, waba_id, token, phone_number_id, app_id FROM whatsapp_account WHERE status = 'connected' LIMIT 1;")
row = cr.fetchone()
conn.close()

acc_id, name, waba_id, token, phone_number_id, app_id = row
token = token.strip()

# 1. Obter arquivo de imagem
img_path = '/opt/odoo/addons/marketing_whatsapp/static/src/img/simplexo_banner_marketing.png'
with open(img_path, 'rb') as f:
    img_data = f.read()

file_len = len(img_data)
print(f"Iniciando upload de exemplo para a Meta (App ID: {app_id}, Tamanho: {file_len} bytes)...")

# 2. Criar Sessão de Upload na Meta
session_url = f"https://graph.facebook.com/v21.0/app/uploads?file_length={file_len}&file_type=image/png&access_token={token}"
s_resp = requests.post(session_url, timeout=20)
print("Create upload session:", s_resp.status_code, s_resp.text)
s_data = s_resp.json()

upload_id = s_data.get('id')
if not upload_id:
    print("Falha ao criar sessao de upload:", s_data)
    exit(1)

# 3. Enviar os bytes do arquivo
headers = {
    "Authorization": f"OAuth {token}",
    "file_offset": "0",
}
up_url = f"https://graph.facebook.com/v21.0/{upload_id}"
up_resp = requests.post(up_url, headers=headers, data=img_data, timeout=30)
print("Upload data status:", up_resp.status_code, up_resp.text)
up_data = up_resp.json()
header_handle = up_data.get('h')

if not header_handle:
    print("Nenhum handle 'h' retornado.")
    exit(1)

print("Header Handle obtido com sucesso:", header_handle)

# 4. Criar o Template na Meta WABA
template_url = f"https://graph.facebook.com/v21.0/{waba_id}/message_templates"
tmpl_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

body_copy = (
    "você já imaginou gerenciar todas as vendas, notas fiscais e estoque da sua empresa em um único lugar?\\n\\n"
    "Com o Simplexo ERP, você reúne controle de estoque em tempo real, emissão automática de NF-e/NFC-e, "
    "frente de caixa PDV ágil e app Força de Vendas, com relatórios inteligentes para facilitar a sua rotina.\\n\\n"
    "Conheça o sistema e veja como funciona na prática:\\n\\n"
    "Para mais informações, clique no botão abaixo."
)

template_payload = {
    "name": "simplexo_gestao_completa_v1",
    "category": "MARKETING",
    "language": "pt_BR",
    "components": [
        {
            "type": "HEADER",
            "format": "IMAGE",
            "example": {
                "header_handle": [header_handle]
            }
        },
        {
            "type": "BODY",
            "text": body_copy
        },
        {
            "type": "BUTTONS",
            "buttons": [
                {
                    "type": "URL",
                    "text": "Clique aqui",
                    "url": "https://simplexo.com.br"
                },
                {
                    "type": "QUICK_REPLY",
                    "text": "Parar mensagens"
                }
            ]
        }
    ]
}

create_resp = requests.post(template_url, headers=tmpl_headers, json=template_payload, timeout=20)
print("Criacao de Template status:", create_resp.status_code)
print("Resposta da Meta:", create_resp.text)
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
