import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "assets" / "index-BgNmguIY.js"
OUT = ROOT / "assets" / "local.bundle.js"

s = SRC.read_text(encoding="utf-8")

# Use same-origin API through local proxy
s = s.replace('io="skycoreclient.xyz"', 'io=""')

# Relax username/password charset checks for local use (allow cyrillic etc.)
s = s.replace(
    "const B=/^[a-zA-Z0-9_]+$/,V=O=>B.test(O)",
    "const B=/^[a-zA-Z0-9_]+$/,V=O=>typeof O==='string'&&O.trim().length>0",
)
captcha_block = (
    'ee=i.jsx("div",{className:"auth-captcha",children:i.jsx(Ti,{siteKey:lo,'
    'options:{theme:"light",size:"flexible"},onSuccess:O=>D(O),onError:()=>D(""),onExpire:()=>D("")})});'
)
if captcha_block in s:
    s = s.replace(captcha_block, "ee=null;")

# Remove captcha requirement checks (login / register / forgot / key activation)
s = re.sub(
    r'if\(!W\)\{s\("[^"]+","error"\);return\}',
    "",
    s,
)
s = re.sub(
    r'if\(!p\)\{r\("[^"]+","error"\);return\}',
    "",
    s,
)

# Remove Turnstile widgets outside auth modal
for captcha_widget in (
    'i.jsx("div",{className:"addons-captcha",children:i.jsx(Ti,{siteKey:lo,'
    'options:{theme:"light",size:"flexible"},onSuccess:c=>w(c),onError:()=>w(""),onExpire:()=>w("")})}),',
    'i.jsx("div",{className:"paysys-captcha",children:i.jsx(Ti,{siteKey:lo,'
    'options:{theme:"light",size:"flexible"},onSuccess:j=>P(j),onError:()=>P(""),onExpire:()=>P("")})}),',
):
    if captcha_widget in s:
        s = s.replace(captcha_widget, "")

# Ensure API calls still send a dummy captcha token
s = s.replace("X.auth.login(v.trim(),w,W)", 'X.auth.login(v.trim(),w,W||"local-bypass")')
s = s.replace("turnstileToken:W", 'turnstileToken:W||"local-bypass"')
s = s.replace("X.auth.forgotPassword(T.trim(),W)", 'X.auth.forgotPassword(T.trim(),W||"local-bypass")')

# Disable Cloudflare Turnstile remote script
s = s.replace(
    'const $v="https://challenges.cloudflare.com/turnstile/v0/api.js"',
    'const $v=""',
)

# Admin panel check should not block UI locally
s = s.replace(
    'await X.admin.check(n).catch(()=>{})',
    'await Promise.resolve({ok:true})',
)

# Auto-login after local registration (server returns token)
register_hook = (
    'await X.auth.register({username:N.trim(),email:f.trim(),password:h,turnstileToken:W}),'
    's("Аккаунт создан, теперь войдите","success"),m("login"),p(N.trim())'
)
register_patch = (
    'const S=await X.auth.register({username:N.trim(),email:f.trim(),password:h,turnstileToken:W||"local-bypass"}),'
    'M=(j=S.token)==null?void 0:j.trim();'
    'if(M){try{localStorage.setItem("velka_token",M),localStorage.setItem("token",M),'
    'sessionStorage.setItem("velka_token",M),sessionStorage.setItem("token",M)}catch{}'
    's("Аккаунт создан","success"),await(r==null?void 0:r(M))}'
    'else{s("Аккаунт создан, теперь войдите","success"),m("login"),p(N.trim())}'
)
if register_hook in s:
    s = s.replace(register_hook, register_patch)

# Open auth modal on /login and /register routes
route_auth_hook = '};return k==="launcher"?'
route_auth_patch = (
    '};y.useEffect(()=>{m==="/register"&&$("register"),m==="/login"&&$("login")},[m]);'
    'return k==="launcher"?'
)
if route_auth_hook in s:
    s = s.replace(route_auth_hook, route_auth_patch)

# Replace /admin URL with secret admin path (both routing and API calls)
_ADMIN_SECRET = "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret"
s = s.replace('"/admin"', f'"{_ADMIN_SECRET}"')
# Replace admin API paths (/admin/... -> /SECRET/...) inside double quotes OR backticks
s = re.sub(r'([`"])/admin/', rf'\g<1>{_ADMIN_SECRET}/', s)

# Replace branding, links and icon
s = s.replace("SkyCore", "SemenRecode")
s = s.replace("skycoredll", "semeyonrecode")
s = s.replace("HVpVsWgruS", "68qCmw27Rj")
s = s.replace("https://funpay.com/users/8170349/", "https://funpay.com/users/13291040/")
s = s.replace('{"30d":259,"90d":500,beta:500,lifetime:600,hwid:259}', '{"30d":159,"90d":259,beta:299,lifetime:399,hwid:199}')

# Replace launcher download with simple redirect to /files/launcher.exe
old_download1 = (
    'const N=io.trim().replace(/\\/+$/,""),'
    'f=`${N?/^https?:\\/\\//i.test(N)?N:`https://${N}`:""}/files/launcher.exe`,'
    'c=`${de.replace(/[\\\\/:*?"<>|]/g,"").trim()||"Client"}Loader.exe`,'
    'h=document.createElement("a");'
    'h.href=f,h.download=c,document.body.appendChild(h),h.click(),h.remove()'
)
old_download2 = (
    '(async()=>{'
    'try{var t=function(){return localStorage.getItem("velka_token")||sessionStorage.getItem("velka_token")||localStorage.getItem("token")||sessionStorage.getItem("token")||""}();'
    'var r=await fetch("/api/zaliv/launcher-url",{headers:{"Authorization":"Bearer "+t}});'
    'if(r.ok){var d=await r.json();'
    'if(d&&d.url){'
    'var c=`${de.replace(/[\\\\/:*?"<>|]/g,"").trim()||"Client"}Loader.exe",'
    'h=document.createElement("a");'
    'h.href=d.url,h.download=c,'
    'document.body.appendChild(h),h.click(),h.remove()'
    '}}}catch{}})()'
)
simple_redirect = 'window.open("/files/launcher.exe","_blank")'
api_fetch_redirect = (
    '(async()=>{'
    'try{var r=await fetch("/api/zaliv/launcher-url");'
    'if(r.ok){var d=await r.json();'
    'if(d&&d.url)window.open(d.url,"_blank")'
    '}}catch{}})()'
)
if old_download1 in s:
    s = s.replace(old_download1, api_fetch_redirect)
    print("Download patched (v1 -> api redirect)")
elif old_download2 in s:
    s = s.replace(old_download2, api_fetch_redirect)
    print("Download patched (v2 -> api redirect)")
s = s.replace('children:g.key}', 'children:g.key.replace(/SKY/g,"SEMEN")}')
s = s.replace('onClick:()=>us(g.key)', 'onClick:()=>us(g.key.replace(/SKY/g,"SEMEN"))')

# Replace YouTube video links
s = s.replace("https://www.youtube.com/watch?v=CczYRQve-mA", "https://www.youtube.com/watch?v=WIiFiCHgVDQ")
s = s.replace("https://www.youtube.com/watch?v=nSKcNmpudew", "https://www.youtube.com/watch?v=ZXnqp5G1JOQ")

# Replace key prefix in admin panel display/copy
s = s.replace('children:g.key}', 'children:g.key.replace(/SKY/g,"SEMEN")}')
s = s.replace('onClick:()=>us(g.key)', 'onClick:()=>us(g.key.replace(/SKY/g,"SEMEN"))')

# Replace icon SVG (plain S letter, no square)
vh_start = s.index("vh=")
vh_end = s.index(",Tv=", vh_start)
new_svg = (
    'vh=`<svg width="264" height="264" viewBox="0 0 264 264" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<text x="132" y="180" text-anchor="middle" fill="white" font-family="system-ui,sans-serif" font-weight="700" font-size="180">S</text>'
    '</svg>`'
)
s = s[:vh_start] + new_svg + s[vh_end:]

# Also patch CSS icon (replace old distorted SVG data URI with clean S icon)
css_path = ROOT / "assets" / "index-h4STkTJJ.css"
if css_path.exists():
    css = css_path.read_text(encoding="utf-8")
    new_svg_url = (
        "data:image/svg+xml,"
        "%3Csvg%20width%3D%27264%27%20height%3D%27264%27%20viewBox%3D%270%200%20264%20264%27"
        "%20fill%3D%27none%27%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%3E"
        "%3Ctext%20x%3D%27132%27%20y%3D%27180%27%20text-anchor%3D%27middle%27%20fill%3D%27white%27"
        "%20font-family%3D%27system-ui%2Csans-serif%27%20font-weight%3D%27700%27%20font-size%3D%27180%27%3ES%3C%2Ftext%3E"
        "%3C%2Fsvg%3E"
    )
    # Replace all 264 SVG data URLs (old distorted paths) with clean S-only version
    # CSS uses lowercase %3c, literal single quotes, literal / in closing tag
    css = re.sub(
        r"data:image/svg\+xml,%3[cC]svg%20width[=]?'?264'?[^)]+?%3[cC]/svg%3[eE]",
        new_svg_url,
        css,
        flags=re.IGNORECASE,
    )
    new_count = css.count("M25.2976")
    
    # NUKE THE MOON: Replace the original background image with svitik1.png
    css = css.replace("background-C3nNrJQw.jpg", "svitik1.png")
    
    css_path.write_text(css, encoding="utf-8")
    print(f"CSS icon patched: old paths {new_count} remaining")
    print("CSS background patched: replaced background-C3nNrJQw.jpg with svitik1.png")

OUT.write_text(s, encoding="utf-8")
print(f"Patched bundle written to {OUT}")
print("Replacements:")

print(" - API host -> relative /api")
print(" - Cloudflare Turnstile removed")
print(" - Captcha guards bypassed")
print(" - Admin pre-check bypassed")

# Keep patched bundle reference after fresh downloads
index = (ROOT / "index.html").read_text(encoding="utf-8")
index = index.replace("/assets/index-BgNmguIY.js", "/assets/local.bundle.js")
index = index.replace("/assets/index-BgNmguIY.patched.js", "/assets/local.bundle.js")

if "custom-theme.css" not in index:
    index = index.replace('</head>', '  <link rel="stylesheet" crossorigin href="/assets/custom-theme.css?v=999">\n  </head>')

(ROOT / "index.html").write_text(index, encoding="utf-8")
print("index.html updated (with custom-theme.css protection)")
