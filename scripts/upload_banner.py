# -*- coding: utf-8 -*-
import subprocess
import os
import base64

local_img_path = r"C:\Users\abera\.gemini\antigravity\brain\0b807a66-0e7b-43cd-b707-1c51cabd2d5c\simplexo_banner_marketing_1789500393641.png"
with open(local_img_path, 'rb') as f:
    b64_data = base64.b64encode(f.read()).decode('utf-8')

print("Tamanho do arquivo codificado em base64:", len(b64_data))

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

remote_script = f"""# -*- coding: utf-8 -*-
import base64
import os

target_dir = '/opt/odoo/addons/marketing_whatsapp/static/src/img'
os.makedirs(target_dir, exist_ok=True)
target_file = os.path.join(target_dir, 'simplexo_banner_marketing.png')

data = base64.b64decode({repr(b64_data)})
with open(target_file, 'wb') as f:
    f.write(data)

print("Imagem salva com sucesso em:", target_file, "Tamanho:", len(data))
"""

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
