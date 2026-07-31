import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

def clean_admin_bundle():
    admin_js = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
    content = admin_js.read_text(encoding="utf-8", errors="ignore")

    # Remove the broken injected div inside D === "logs"
    broken_div = 'e.jsxs("div",{style:{padding:"18px 22px",margin:"0 0 20px 0",borderRadius:"16px",background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.12)",display:"flex",flexDirection:"column",gap:"12px"},children:[e.jsx("div",{style:{fontWeight:"700",fontSize:16,color:"#fff"},children:"📥 Авто-Аплоуд / Ссылка для скачивания клиента:"}),e.jsxs("div",{style:{display:"flex",gap:"12px",flexWrap:"wrap"},children:[e.jsx("input",{type:"text",value:autouploadUrl,onChange:evt=>setAutouploadUrl(evt.target.value),placeholder:"https://workupload.com/file/...",style:{flex:1,minWidth:"280px",padding:"12px 16px",borderRadius:"12px",background:"rgba(0,0,0,0.5)",border:"1px solid rgba(255,255,255,0.18)",color:"#fff",fontSize:"14px"}}),e.jsx("button",{type:"button",onClick:handleSaveAutoupload,style:{padding:"12px 24px",borderRadius:"12px",background:"#a855f7",color:"#fff",fontWeight:"600",border:"none",cursor:"pointer"},children:"Сохранить ссылку"})]}),autouploadMsg?e.jsx("div",{style:{color:"#4ade80",fontSize:"14px",fontWeight:"600"},children:autouploadMsg}):null]}),'

    content = content.replace(broken_div, '')

    # Fix initial loading state to `false` (`o.useState(!1)`) so page renders immediately
    content = content.replace('[k,w]=o.useState(!s)', '[k,w]=o.useState(!1)')

    admin_js.write_text(content, encoding="utf-8")
    print("[ADMIN BUNDLE 100% CLEANED] Removed broken injected div from logs section in AdminPage-zjEM4fPO.js!")

if __name__ == "__main__":
    clean_admin_bundle()
