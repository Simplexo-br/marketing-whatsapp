# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """# -*- coding: utf-8 -*-
import psycopg2
import configparser

cfg = configparser.ConfigParser()
cfg.read('/opt/odoo/conf/simplexo.conf')
conn = psycopg2.connect(
    dbname='simplexo',
    user=cfg.get('options', 'db_user', fallback='simplexo'),
    password=cfg.get('options', 'db_password', fallback=''),
    host=cfg.get('options', 'db_host', fallback=False) or None,
    port=cfg.get('options', 'db_port', fallback=False) or None
)
cr = conn.cursor()

cr.execute(\"\"\"
    SELECT m.id, m.subject, m.state, m.whatsapp_template_id, wt.name as tmpl_name, count(t.id) as total_traces
    FROM mailing_mailing m
    LEFT JOIN whatsapp_template wt ON m.whatsapp_template_id = wt.id
    LEFT JOIN mailing_trace t ON t.mass_mailing_id = m.id
    WHERE m.mailing_type = 'whatsapp'
    GROUP BY m.id, m.subject, m.state, m.whatsapp_template_id, wt.name
    ORDER BY m.id DESC;
\"\"\")
mailings = cr.fetchall()
print("CAMPANHAS WHATSAPP:")
for m in mailings:
    print(f"ID={m[0]}, Nome='{m[1]}', Estado={m[2]}, TemplateID={m[3]} ({m[4]}), TotalTraces={m[5]}")

cr.execute(\"\"\"
    SELECT whatsapp_status, count(*) 
    FROM mailing_trace 
    GROUP BY whatsapp_status;
\"\"\")
print("\\nSTATUS DOS TRACES GERAIS:")
for row in cr.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
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
stdout_bytes, stderr_bytes = proc.communicate(input=remote_script.encode('utf-8'), timeout=30)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
