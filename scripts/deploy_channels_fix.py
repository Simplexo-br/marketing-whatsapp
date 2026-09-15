# -*- coding: utf-8 -*-
import subprocess
import os
import base64
import json

default_keys = [
    os.environ.get('SIMPLEXO_SSH_KEY'),
    os.path.expanduser('~/.ssh/simplexo_vm'),
    os.path.expanduser('~/.ssh/simplexo_gpt_desktop'),
    r'C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm',
]
ssh_key = next((k for k in default_keys if k and os.path.exists(k)), default_keys[-1])
bastion = 'fellipe_ramalho@35.224.220.67'
internal_server = 'fellipe_ramalho@34.45.88.55'

local_module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'marketing_whatsapp'))

print(f"==> Coletando arquivos de {local_module_dir}...")
file_map = {}
for root, dirs, files in os.walk(local_module_dir):
    for f in files:
        if f.endswith(('.py', '.xml', '.csv', '.js', '.css', '.scss', '.png', '.svg', '.json')):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, local_module_dir).replace('\\', '/')
            with open(full, 'rb') as fp:
                file_map[rel] = base64.b64encode(fp.read()).decode('ascii')

print(f"==> Total de arquivos mapeados: {len(file_map)}")

remote_deploy_code = f'''# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('/opt/odoo/odoo')
import base64
import subprocess
import json
import odoo
from odoo import api, SUPERUSER_ID


file_map = {repr(file_map)}
target_dir = "/opt/odoo/addons/marketing_whatsapp"

print("1. Gravando arquivos em " + target_dir + "...")
for rel_path, b64_content in file_map.items():
    dest_path = os.path.join(target_dir, rel_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(base64.b64decode(b64_content))

print("2. Ajustando permissoes...")
subprocess.run(["chmod", "-R", "777", target_dir], check=False)

print("3. Parando servico odoo-simplexo e atualizando modulo marketing_whatsapp...")
subprocess.run(["systemctl", "stop", "odoo-simplexo"], check=True)

upg = subprocess.run([
    "/opt/odoo/venv/bin/python3",
    "/opt/odoo/odoo/odoo-bin",
    "-c", "/opt/odoo/conf/simplexo.conf",
    "-d", "simplexo",
    "-u", "marketing_whatsapp",
    "--stop-after-init",
    "--no-http"
], capture_output=True, text=True)

print("Codigo de retorno do upgrade:", upg.returncode)
if upg.returncode != 0:
    print("ERRO NO UPGRADE:")
    print(upg.stderr)

print("4. Testando action_open_channels_management e serializacao JSON:")
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, dict())
    res = env['whatsapp.account'].action_open_channels_management()
    dumped = json.dumps(res)
    print("JSON Serializado com Sucesso:", dumped[:200] + "...")

print("5. Reiniciando servico odoo-simplexo...")
subprocess.run(["systemctl", "start", "odoo-simplexo"], check=True)

print("6. Verificando status do servico...")
st = subprocess.run(["systemctl", "status", "odoo-simplexo"], capture_output=True, text=True)
print(st.stdout[:500])
'''

print("==> Conectando via Bastion e iniciando Deploy...")
cmd = [
    'ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15',
    '-i', ssh_key, bastion,
    f'ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} "sudo /opt/odoo/venv/bin/python3"'
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = proc.communicate(input=remote_deploy_code.encode('utf-8'))
out_str = stdout.decode('utf-8', errors='replace')
err_str = stderr.decode('utf-8', errors='replace')

print(out_str)
if err_str:
    print('STDERR:', err_str)
