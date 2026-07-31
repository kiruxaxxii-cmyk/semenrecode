with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        # Static files & SPA Routing
        if target_path.is_file():
            return super().do_GET()'''

replacement = '''        # Static files & SPA Routing
        if target_path.suffix in ['.db', '.sqlite', '.py', '.env']:
            self.send_response(403)
            self.end_headers()
            return
            
        if target_path.is_file():
            return super().do_GET()'''

if target in content:
    content = content.replace(target, replacement)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Target not found")
