d = open('assets/index-BgNmguIY.js', 'r', encoding='utf-8').read()
idx = d.find('const N=io.trim()')
if idx >= 0:
    snippet = d[idx:idx+300]
    print(repr(snippet[:250]))
