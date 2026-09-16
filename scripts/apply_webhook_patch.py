# -*- coding: utf-8 -*-
import subprocess
import os

patch_script = """# -*- coding: utf-8 -*-
import re
import shutil

# 1. Patch simplexo_aios_whatsapp_webhook_event.py
webhook_file = '/opt/odoo/addons/simplexo_aios_whatsapp/models/whatsapp_webhook_event.py'
shutil.copyfile(webhook_file, webhook_file + '.bak_sync')

with open(webhook_file, 'r', encoding='utf-8') as f:
    code = f.read()

# Add re import if needed
if 'import re' not in code:
    code = 'import re\\n' + code

# Patch _apply_meta_status
apply_patch = \"\"\"        if message:
            message._apply_delivery_status(
                target,
                failure_code=failure_code,
                failure_reason=failure_reason,
            )

        # Sincronizacao em tempo real com marketing_whatsapp (mailing.trace)
        if "mailing.trace" in self.env and external_id:
            try:
                trace = self.env["mailing.trace"].sudo().search([("whatsapp_message_id", "=", external_id)], limit=1)
                if trace:
                    vals = {}
                    if target in {"delivered", "read"} and trace.whatsapp_status not in {"delivered", "read"}:
                        vals["whatsapp_status"] = "delivered"
                        vals["whatsapp_delivered_date"] = fields.Datetime.now()
                    if target == "read" and trace.whatsapp_status != "read":
                        vals["whatsapp_status"] = "read"
                        vals["whatsapp_read_date"] = fields.Datetime.now()
                    elif target == "failed":
                        vals["whatsapp_status"] = "failed"
                        vals["whatsapp_error_code"] = failure_code
                        vals["whatsapp_error_message"] = failure_reason
                    if vals:
                        trace.write(vals)
            except Exception as e:
                _logger.warning("Falha ao sincronizar mailing.trace no webhook: %s", e)\"\"\"

if 'Falha ao sincronizar mailing.trace no webhook' not in code:
    target_block = \"\"\"        if message:
            message._apply_delivery_status(
                target,
                failure_code=failure_code,
                failure_reason=failure_reason,
            )\"\"\"
    code = code.replace(target_block, apply_patch)

# Patch _ingest_meta_message
ingest_marker = \"\"\"        occurred_at = fields.Datetime.now()
        if str(message.get("timestamp") or "").isdigit():
            occurred_at = datetime.utcfromtimestamp(int(message["timestamp"]))\"\"\"

ingest_patch = \"\"\"        occurred_at = fields.Datetime.now()
        if str(message.get("timestamp") or "").isdigit():
            occurred_at = datetime.utcfromtimestamp(int(message["timestamp"]))

        # Sincronizacao em tempo real com marketing_whatsapp (mailing.contact)
        if "mailing.contact" in self.env and phone:
            try:
                digits = re.sub(r'\\D', '', phone)
                if len(digits) >= 8:
                    suffix = digits[-8:]
                    matching_contacts = self.env["mailing.contact"].sudo().search([
                        "|", ("mobile_whatsapp", "like", suffix),
                        ("mobile", "like", suffix)
                    ])
                    for m_contact in matching_contacts:
                        c_vals = {
                            "wa_status_replied": True,
                            "wa_replied_date": occurred_at or fields.Datetime.now(),
                            "wa_last_response": (body or "Resposta recebida")[:200],
                            "wa_status": "replied"
                        }
                        lower_body = (body or "").strip().lower()
                        opt_out_kw = ["2", "2.", "opcao 2", "opção 2", "parar", "stop", "sair", "cancelar", "nao", "não", "remover", "descadastrar"]
                        if lower_body in opt_out_kw or lower_body.startswith("2"):
                            c_vals["wa_status_opt_out"] = True
                            c_vals["wa_opt_out_date"] = occurred_at or fields.Datetime.now()
                            c_vals["wa_status"] = "opt_out"
                            c_vals["wa_status_replied"] = False
                            if "phone.blacklist" in self.env:
                                p_num = m_contact.mobile_whatsapp or m_contact.mobile
                                if p_num:
                                    s_num = re.sub(r'[^0-9+]', '', p_num)
                                    if not self.env["phone.blacklist"].sudo().search([("number", "=", s_num)], limit=1):
                                        self.env["phone.blacklist"].sudo().create({"number": s_num})
                        m_contact.write(c_vals)
            except Exception as e:
                _logger.warning("Falha ao sincronizar mailing.contact no webhook: %s", e)\"\"\"

if 'Falha ao sincronizar mailing.contact no webhook' not in code:
    code = code.replace(ingest_marker, ingest_patch)

with open(webhook_file, 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch aplicado com sucesso em whatsapp_webhook_event.py!")
"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_bytes, stderr_bytes = proc.communicate(input=patch_script.encode('utf-8'), timeout=30)
print(stdout_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
if stderr_bytes:
    print("STDERR:", stderr_bytes.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii'))
