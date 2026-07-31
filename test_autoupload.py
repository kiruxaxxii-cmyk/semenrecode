import sqlite3
import urllib.request
import json

# Check DB admin pass
conn = sqlite3.connect('database.db')
c = conn.cursor()
row = c.execute("SELECT username, password FROM users WHERE username='admin'").fetchone()
admin_pass = row[1]
print("Admin pass in DB:", admin_pass)

# Login
admin_payload = json.dumps({'login': 'admin', 'password': admin_pass, 'hcaptchaToken': '0.test'}).encode()
req_admin_login = urllib.request.Request('http://localhost:3000/api/auth/login', data=admin_payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req_admin_login) as resp:
    admin_cookies = resp.headers.get('Set-Cookie')
    print("Logged in successfully!")

# Set URL in Admin settings
set_url_payload = json.dumps({'downloadUrl': 'https://workupload.com/file/semenclient1165'}).encode()
req_set_url = urllib.request.Request('http://localhost:3000/api/admin/settings/download-url', data=set_url_payload, headers={'Content-Type': 'application/json', 'Cookie': admin_cookies})
with urllib.request.urlopen(req_set_url) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print('[ADMIN SETTING UPDATED]:', res.get('message'))

# Download redirect test
class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirectHandler)
req_dl = urllib.request.Request('http://localhost:3000/api/profile/download-launcher', headers={'Cookie': admin_cookies})
try:
    with opener.open(req_dl) as resp:
        print('Status:', resp.status)
except urllib.error.HTTPError as e:
    if e.code == 302:
        print('[DOWNLOAD REDIRECT TEST PASSED 302] Target Location:', e.headers.get('Location'))
