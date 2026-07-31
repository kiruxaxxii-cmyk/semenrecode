from pathlib import Path

server_file = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear\server.py")
content = server_file.read_text(encoding="utf-8", errors="ignore")

old_block = '''                        if self.path == "/api/admin/settings/download-url":
                if not user or not user.get("is_admin"):
                    return self._send_json({"ok": False, "message": "Access forbidden"}, 403)
                new_url = payload.get("downloadUrl", "").strip()
                if new_url:
                    set_setting("download_url", new_url)
                    return self._send_json({"ok": True, "message": "Ссылка на скачивание успешно сохранена!", "downloadUrl": new_url})
                return self._send_json({"ok": False, "message": "Укажите правильную ссылку!"}, 400)'''

new_block = '''            if self.path == "/api/admin/settings/download-url":
                if not user or not user.get("is_admin"):
                    return self._send_json({"ok": False, "message": "Access forbidden"}, 403)
                new_url = payload.get("downloadUrl", "").strip()
                if new_url:
                    set_setting("download_url", new_url)
                    return self._send_json({"ok": True, "message": "Ссылка на скачивание успешно сохранена!", "downloadUrl": new_url})
                return self._send_json({"ok": False, "message": "Укажите правильную ссылку!"}, 400)'''

content = content.replace(old_block, new_block)
server_file.write_text(content, encoding="utf-8")
print("Fixed indentation in server.py!")
