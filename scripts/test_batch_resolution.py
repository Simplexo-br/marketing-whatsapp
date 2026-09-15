# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
import re
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo.tools import config
config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf'])
import psycopg2

VALID_DDDS = {
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 24, 27, 28,
    31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48, 49,
    51, 53, 54, 55,
    61, 62, 63, 64, 65, 66, 67, 68, 69,
    71, 73, 74, 75, 77, 79,
    81, 82, 83, 84, 85, 86, 87, 88, 89,
    91, 92, 93, 94, 95, 96, 97, 98, 99
}

def extract_valid_phone(raw):
    digits = re.sub(r'[^0-9]', '', str(raw))
    if digits.startswith('55') and len(digits) in [12, 13]:
        ddd = int(digits[2:4])
        if ddd in VALID_DDDS:
            return f"+{digits}"
    if len(digits) in [10, 11]:
        ddd = int(digits[:2])
        if ddd in VALID_DDDS:
            return f"+55{digits}"
            
    # Tentar extrair celular (11 dígitos começando com DDD válido e 9)
    for m in re.finditer(r'(?:55)?([1-9][0-9]9[0-9]{8})', digits):
        candidate = m.group(1)
        ddd = int(candidate[:2])
        if ddd in VALID_DDDS:
            return f"+55{candidate}"
            
    # Tentar extrair fixo (10 dígitos começando com DDD válido e [2-5])
    for m in re.finditer(r'(?:55)?([1-9][0-9][2-5][0-9]{7})', digits):
        candidate = m.group(1)
        ddd = int(candidate[:2])
        if ddd in VALID_DDDS:
            return f"+55{candidate}"
            
    return None

conn_params = {
    'dbname': 'simplexo',
    'user': config['db_user'],
    'password': config['db_password'],
    'host': config['db_host'] or 'localhost',
    'port': config['db_port'] or 5432
}
conn = psycopg2.connect(**conn_params)
cr = conn.cursor()

cr.execute(\"\"\"
    SELECT id, whatsapp_recipient_number 
    FROM mailing_trace 
    WHERE mass_mailing_id = 134 
      AND LENGTH(regexp_replace(whatsapp_recipient_number, '[^0-9]', '', 'g')) > 13;
\"\"\")
rows = cr.fetchall()
resolved = 0
unresolved = 0
for tid, num in rows:
    clean = extract_valid_phone(num)
    if clean:
        resolved += 1
    else:
        unresolved += 1
        
print(f"Total analisados: {len(rows)} | Resolvidos com sucesso: {resolved} | Não resolvidos: {unresolved}")
conn.close()
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo -E /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=60)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
