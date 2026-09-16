# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import odoo
from odoo.tools import config
config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf'])
import psycopg2

conn_params = {
    'dbname': 'simplexo',
    'user': config['db_user'],
    'password': config['db_password'],
    'host': config['db_host'] or 'localhost',
    'port': config['db_port'] or 5432
}
conn = psycopg2.connect(**conn_params)
cr = conn.cursor()

numbers = [
    '981232838', # Recanto do vovo (+55 17 98123-2838)
    '99155996',  # Costela no bafo (+55 35 9915-5996)
    '88917576',  # Giggio Spaghetti (+55 35 8891-7576)
    '84265680',  # Restaurante Gordeichuk (+55 47 8426-5680)
]

for num in numbers:
    cr.execute(\"\"\"
        SELECT id, name, mobile, mobile_whatsapp, wa_status_replied, wa_last_response
        FROM mailing_contact
        WHERE mobile LIKE %s OR mobile_whatsapp LIKE %s;
    \"\"\", (f'%{num}%', f'%{num}%'))
    rows = cr.fetchall()
    print(f"Busca por {num}: {rows}")

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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=30)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
