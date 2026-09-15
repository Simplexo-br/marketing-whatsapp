# -*- coding: utf-8 -*-
import subprocess
import os
import json
import base64

local_module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "marketing_whatsapp")
module_name = "marketing_whatsapp"

print(f"==> Coletando arquivos de {local_module_dir}...")
payload = {}
for root, dirs, files in os.walk(local_module_dir):
    for f in files:
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(full_path, local_module_dir).replace("\\", "/")
        with open(full_path, "rb") as fp:
            payload[rel_path] = base64.b64encode(fp.read()).decode("utf-8")

print(f"==> Total de arquivos mapeados: {len(payload)}")
payload_json = json.dumps(payload)

remote_script = """# -*- coding: utf-8 -*-
import json, os, subprocess, base64

payload = json.loads(__PAYLOAD_JSON__)
target_base = "/opt/odoo/addons/marketing_whatsapp"

print("1. Gravando arquivos do modulo em " + target_base + "...")
for rel_path, b64_content in payload.items():
    target_file = os.path.join(target_base, rel_path)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "wb") as f:
        f.write(base64.b64decode(b64_content))

print("2. Ajustando permissoes...")
subprocess.run("sudo chown -R simplexo:simplexo " + target_base, shell=True)
subprocess.run("sudo chmod -R 755 " + target_base, shell=True)

print("3. Parando servico odoo-simplexo e atualizando modulo marketing_whatsapp...")
subprocess.run("sudo systemctl stop odoo-simplexo", shell=True)
up_cmd = "sudo -u simplexo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /opt/odoo/conf/simplexo.conf -d simplexo -u marketing_whatsapp --stop-after-init --no-http"
p = subprocess.run(up_cmd, shell=True, capture_output=True, text=True)
print("Codigo de retorno do upgrade:", p.returncode)
if p.stderr:
    print("Stderr Odoo:", "\\n".join(p.stderr.strip().splitlines()[-15:]))


print("4. Configurando janela comercial (08:00 as 17:00) e pausando execucao noturna...")
config_code = '''# -*- coding: utf-8 -*-
import odoo
from odoo import api, SUPERUSER_ID, fields
import pytz
from datetime import datetime

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    ICP = env['ir.config_parameter'].sudo()
    ICP.set_param('marketing_whatsapp.dispatch_window_enabled', 'True')
    ICP.set_param('marketing_whatsapp.dispatch_window_start', '8')
    ICP.set_param('marketing_whatsapp.dispatch_window_end', '17')
    ICP.set_param('marketing_whatsapp.dispatch_timezone', 'America/Sao_Paulo')
    
    tz = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz)
    print("HORA ATUAL BRASILIA:", now_br.strftime('%Y-%m-%d %H:%M:%S'))
    
    mailings = env['mailing.mailing'].search([('mailing_type', '=', 'whatsapp'), ('state', 'in', ['in_queue', 'sending'])])
    for m in mailings:
        m.write({'state': 'in_queue', 'is_paused': False})
        print(f"Campanha ID {m.id} ({m.subject or m.name}): Colocada em Fila Programada (In_Queue) - Janela: 08:00 as 17:00 BRT")
'''
conf_b64 = base64.b64encode(config_code.encode('utf-8')).decode('ascii')
subprocess.run(f"echo '{conf_b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http", shell=True)

print("5. Reiniciando servico odoo-simplexo...")
subprocess.run("sudo systemctl restart odoo-simplexo", shell=True)

print("6. Verificando status do servico...")
stat = subprocess.run("sudo systemctl status odoo-simplexo --no-pager", shell=True, capture_output=True, text=True)
print(stat.stdout[:500])
""".replace("__PAYLOAD_JSON__", repr(payload_json))

default_keys = [
    os.environ.get("SIMPLEXO_SSH_KEY"),
    os.path.expanduser("~/.ssh/simplexo_vm"),
    os.path.expanduser("~/.ssh/simplexo_gpt_desktop"),
    r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm",
]
ssh_key = next((k for k in default_keys if k and os.path.exists(k)), default_keys[-1])
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

print("==> Conectando via Bastion e iniciando Deploy + Programação da Janela...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=300)

print("--- RESULTADO DO SERVIDOR ---")
if stdout:
    print(stdout.encode("ascii", errors="replace").decode("ascii"))
if stderr:
    print("--- STDERR ---")
    print(stderr.encode("ascii", errors="replace").decode("ascii"))
