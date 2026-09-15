# -*- coding: utf-8 -*-
import subprocess
import os

remote_script = """
import sys
sys.path.insert(0, '/opt/odoo/odoo')
import unittest
import odoo
odoo.addons.__path__.append('/opt/odoo/addons')
from odoo import api, SUPERUSER_ID
from odoo.addons.marketing_whatsapp.tests.test_whatsapp_campaign import TestWhatsAppCampaign

odoo.tools.config.parse_config(['-c', '/opt/odoo/conf/simplexo.conf', '-d', 'simplexo'])
registry = odoo.registry('simplexo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    test_methods = [
        'test_contact_phoneless_protection',
        'test_contact_deduplication_and_list_merge',
        'test_carousel_template_and_payload',
        'test_subscription_invoice_generation'
    ]
    for method in test_methods:
        case = TestWhatsAppCampaign(method)
        case.env = env
        case.cr = cr
        case.registry = registry
        case.setattrs = set()
        try:
            case.setUp()
            getattr(case, method)()
            print(f"PASS: {method}")
        except Exception as e:
            import traceback
            print(f"FAIL: {method} -> {e}")
            traceback.print_exc()
        finally:
            cr.rollback()

"""

ssh_key = os.path.expanduser("~/.ssh/simplexo_gpt_desktop")
bastion = "fellipe_ramalho@35.224.220.67"
internal_server = "fellipe_ramalho@34.45.88.55"

cmd = [
    "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
    "-i", ssh_key, bastion,
    f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i ~/.ssh/simplexo_aios_production {internal_server} 'sudo /opt/odoo/venv/bin/python3'"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
stdout, stderr = proc.communicate(input=remote_script, timeout=60)
print(stdout)
if stderr:
    print("STDERR:", stderr)
