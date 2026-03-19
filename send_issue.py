import os
import sys
from pathlib import Path

import httpx

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ.setdefault(key, value)

BREVO_API_KEY = os.environ['BREVO_API_KEY']
BREVO_LIST_ID = int(os.environ.get('BREVO_LIST_ID', '17'))
SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL', 'adrienlaine91@gmail.com')
SENDER_NAME = os.environ.get('BREVO_SENDER_NAME', 'Atelier Operators')

if len(sys.argv) < 3:
    print('Usage: python send_issue.py <subject> <markdown_file>')
    raise SystemExit(1)

subject = sys.argv[1]
markdown_file = Path(sys.argv[2])
text = markdown_file.read_text(encoding='utf-8')
html = '<pre style="white-space:pre-wrap;font-family:Inter,Arial,sans-serif;line-height:1.6">' + text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + '</pre>'

payload = {
    'sender': {'name': SENDER_NAME, 'email': SENDER_EMAIL},
    'subject': subject,
    'htmlContent': html,
    'textContent': text,
    'replyTo': {'email': 'atelieroperators@agentmail.to', 'name': 'Atelier Operators'},
    'recipients': {'listIds': [BREVO_LIST_ID]},
}
headers = {
    'api-key': BREVO_API_KEY,
    'accept': 'application/json',
    'content-type': 'application/json',
}
resp = httpx.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=payload, timeout=30)
print(resp.status_code)
print(resp.text)
