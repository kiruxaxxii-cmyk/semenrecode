import urllib.request
import json

url = "http://localhost:3000/api/auth/login"
payload = {"login": "admin", "password": "kX9#mP2$vL7!wQ4@Z9#Semen2026"}
data = json.dumps(payload).encode("utf-8")

req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    print(f"Status: {resp.status}")
    print("Response:", resp.read().decode())
