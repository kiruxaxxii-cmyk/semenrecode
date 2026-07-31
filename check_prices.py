import urllib.request
import json

req = urllib.request.Request("http://localhost:3000/api/public/bootstrap")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    products = data.get("data", {}).get("products", [])
    for p in products:
        print(f"{p['name']}: {p['display_price']} (Numeric: {p['price']})")
