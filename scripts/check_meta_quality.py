# -*- coding: utf-8 -*-
import subprocess
import os
import base64

remote_script = """# -*- coding: utf-8 -*-
import requests
import json
import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Busca o token no canal 3 ou no ir.config_parameter
    ch = env['simplexo.aios.whatsapp.channel'].browse(3)
    token = getattr(ch, 'meta_token', False) or getattr(ch, 'access_token', False)
    if not token and hasattr(ch, '_get_meta_token'):
        token = ch._get_meta_token()
    if not token:
        token = env['ir.config_parameter'].sudo().get_param('whatsapp.meta_access_token') or env['ir.config_parameter'].sudo().get_param('simplexo_whatsapp_access_token')

    print("=== CONSULTA DIRETA NA API DA META (GRAPH API) ===")
    
    phone_id = "1037479776125011"
    waba_id = "852874847875747"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Status do número de telefone
    url_phone = f"https://graph.facebook.com/v20.0/{phone_id}?fields=display_phone_number,verified_name,quality_rating,messaging_limit_tier,status,code_verification_status"
    res_phone = requests.get(url_phone, headers=headers)
    print("Telefone Info:", res_phone.status_code, json.dumps(res_phone.json(), indent=2))
    
    # 2. Status da WABA
    url_waba = f"https://graph.facebook.com/v20.0/{waba_id}?fields=name,account_review_status,message_template_namespace"
    res_waba = requests.get(url_waba, headers=headers)
    print("WABA Info:", res_waba.status_code, json.dumps(res_waba.json(), indent=2))
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

b64 = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
remote_cmd = f"echo '{b64}' | base64 -d | sudo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/conf/simplexo.conf -d simplexo --no-http"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} \"{remote_cmd}\""
]

p = subprocess.run(cmd, capture_output=True, text=False)
stdout = p.stdout.decode('utf-8', errors='replace')
stderr = p.stderr.decode('utf-8', errors='replace')
print(stdout)
if stderr:
    print('STDERR:', stderr)
