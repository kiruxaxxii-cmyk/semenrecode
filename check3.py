d = open('assets/index-BgNmguIY.js', 'r', encoding='utf-8').read()
old = ('const N=io.trim().replace(/\\/+$/,""),'
       'f='+'${N?/^https?:\\/\\//i.test(N)?N:https://:""}/files/launcher.exe,')
print('pattern found:', old in d)
