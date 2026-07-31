from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
server_py = ROOT_DIR / "server.py"

content = server_py.read_text(encoding="utf-8", errors="ignore")

idx_reg = content.find("/api/auth/register")
if idx_reg != -1:
    print("Register endpoint snippet:")
    print(content[max(0, idx_reg-50):min(len(content), idx_reg+450)])

idx_db = content.find("def get_db")
if idx_db != -1:
    print("Get_db snippet:")
    print(content[max(0, idx_db-50):min(len(content), idx_db+350)])
