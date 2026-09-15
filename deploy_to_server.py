# -*- coding: utf-8 -*-
import subprocess
import os
import json
import base64

local_module_dir = r"c:\Users\user\Documents\antigravity\Marketing Whatsapp\marketing_whatsapp"
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

remote_script = f"""
import json, os, subprocess, base64

payload = json.loads({repr(payload_json)})
target_base = "/opt/odoo/addons/{module_name}"

print("1. Gravando arquivos do modulo em " + target_base + "...")
for rel_path, b64_content in payload.items():
    target_file = os.path.join(target_base, rel_path)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "wb") as f:
        f.write(base64.b64decode(b64_content))

print("2. Ajustando permissoes...")
subprocess.run("sudo chown -R simplexo:simplexo " + target_base, shell=True)
subprocess.run("sudo chmod -R 755 " + target_base, shell=True)

print("3. Verificando dependencias Python no venv...")
subprocess.run("sudo /opt/odoo/venv/bin/pip install phonenumbers requests", shell=True)

print("4. Parando servico odoo-simplexo...")
subprocess.run("sudo systemctl stop odoo-simplexo", shell=True)

print("5. Instalando/Atualizando modulo {module_name} no banco de dados simplexo...")
up_cmd = "/opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /opt/odoo/conf/simplexo.conf -d simplexo -i {module_name} --stop-after-init"
p = subprocess.run(up_cmd, shell=True, capture_output=True, text=True)
print("Codigo de retorno do comando Odoo:", p.returncode)
if p.stderr:
    print("Log/Stderr Odoo (ultimas 30 linhas):\\n", "\\n".join(p.stderr.strip().splitlines()[-30:]))
if p.stdout:
    print("Stdout Odoo (ultimas 30 linhas):\\n", "\\n".join(p.stdout.strip().splitlines()[-30:]))

print("6. Reiniciando servico odoo-simplexo...")
subprocess.run("sudo systemctl start odoo-simplexo", shell=True)

print("7. Status final do servico odoo-simplexo:")
stat = subprocess.run("sudo systemctl status odoo-simplexo --no-pager", shell=True, capture_output=True, text=True)
print(stat.stdout[:600])
"""

ssh_key = r"C:\Users\user\Documents\Codex\2026-09-05\files-pasted-by-the-user-usr\work\ssh\simplexo_vm"
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

print("==> Conectando via Bastion e iniciando Deploy no Servidor de Producao...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=300)

print("--- RESULTADO DO SERVIDOR ---")
if stdout:
    print(stdout.encode("ascii", errors="replace").decode("ascii"))
if stderr:
    print("--- STDERR ---")
    print(stderr.encode("ascii", errors="replace").decode("ascii"))
