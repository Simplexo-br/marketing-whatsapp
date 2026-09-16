# -*- coding: utf-8 -*-
import subprocess
import os

files_to_sync = [
    'marketing_whatsapp/models/mailing_contact.py',
    'marketing_whatsapp/models/whatsapp_dashboard.py',
    'marketing_whatsapp/data/ir_cron_data.xml'
]

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

for fpath in files_to_sync:
    local_path = os.path.join(r"c:\Users\abera\OneDrive\Documentos\Simplexo\Simplexo Marketing Whatsapp", fpath)
    remote_path = f"/opt/odoo/addons/{fpath}"
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Uploading {fpath}...")
    upload_script = f"""# -*- coding: utf-8 -*-
import os
content = {repr(content)}
target = {repr(remote_path)}
with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Uploaded to", target)
"""
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
        "-i", ssh_key, bastion,
        f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo python3'"
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=upload_script.encode('utf-8'), timeout=30)
    print(" ", stdout.decode('utf-8', errors='replace').strip())
    if stderr:
        print("  STDERR:", stderr.decode('utf-8', errors='replace').strip())

print("Upload concluido!")
