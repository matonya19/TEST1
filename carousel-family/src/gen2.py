FONTS='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/'
# bg, headline card (top,left,width), sub bubble (top,left,width)
S=[
 dict(bg='bg_p1.jpg',h='Как изменится ваша жизнь на онлайн-обучении?',hl='жизнь',card=(120,60,800),s='Обычный день семьи в SHKOLA',sub=(1150,300,720)),
 dict(bg='bg_p2.jpg',h='Утром больше не нужно ехать в школу',hl='не нужно',card=(860,60,800),s='Вместо дороги — завтрак дома. К началу урока достаточно открыть ноутбук.',sub=(1120,150,840)),
 dict(bg='bg_p3.jpg',h='На вопрос ребёнка есть время',hl='есть время',card=(120,360,660),s='В мини-классе до восьми учеников. Если тема сложная, учитель может объяснить её ещё раз.',sub=(1090,60,780)),
 dict(bg='bg_p5.jpg',h='После болезни можно вернуться к сложной теме',hl='сложной теме',card=(120,60,860),s='Ученик SHKOLA: «И меня никто не торопит».',sub=(1190,230,700)),
 dict(bg=None,h='Книгу открывают и после урока',hl='книги',quote='Благодаря ей я начала читать книги',who='Соня, ученица SHKOLA'),
 dict(bg='bg_p4.jpg',h='Подойдёт ли это вашей семье?',hl='3 бесплатных дня',card=(640,60,800),s='Попробуйте 3 бесплатных дня в SHKOLA. Ребёнок познакомится с классом и побывает на уроках по расписанию.',sub=(960,150,800),cta='Запись по ссылке в профиле'),
]
def hl(t,d): return t.replace(d['hl'],f'<span class=hl>{d["hl"]}</span>') if d.get('hl') and d['hl'] in t else t
def html(i,d):
    bg=f'<img class=bg src="{d["bg"]}">' if d['bg'] else '<div class="bg qbg"></div>'
    if 'quote' in d:
        body=f'''<div class=cap>{d["h"]}</div>
<div class="card" style="top:430px;left:60px;width:960px"><div class=hd><div class=av>С</div><div><b>Соня</b><small>ученица SHKOLA</small></div></div>
<div class=qb>{hl(d["quote"],d)}</div></div>'''
    else:
        t,l,w=d['card']; st,sl,sw=d['sub']
        btn=f'<div class=btn>{d["cta"]}</div>' if d.get('cta') else ''
        body=f'''<div class=card style="top:{t}px;left:{l}px;width:{w}px"><div class=hd><img src="logo.png"><small>сейчас</small></div><h1>{hl(d["h"],d)}</h1></div>
<div class=row style="top:{st}px;left:{sl}px;width:{sw}px"><div class=av>S</div><div class=bub>{d["s"]}{btn}</div></div>'''
    return f'''<!doctype html><meta charset=utf-8><style>
{''.join(f'@import url("{FONTS}{s}.css");' for s in ['cyrillic-500','cyrillic-600','cyrillic-700','cyrillic-800','latin-500','latin-600','latin-700','latin-800'])}
*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1350px;font-family:Manrope;position:relative;overflow:hidden;background:#2f6bd8;color:#0d1b3d}}
.bg{{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover}}.qbg{{background:linear-gradient(160deg,#3d7cf0,#2457c4)}}
.card{{position:absolute;background:rgba(255,255,255,.9);backdrop-filter:blur(22px);border-radius:38px;padding:30px 44px 38px;box-shadow:0 20px 56px rgba(8,20,50,.28)}}
.hd{{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}}.hd img{{height:32px}}.hd small{{font:600 22px Manrope;color:#8190a8}}
h1{{font:800 50px/1.17 Manrope;letter-spacing:-.6px}}
.row{{position:absolute;display:flex;gap:16px;align-items:flex-end}}
.av{{flex:none;width:60px;height:60px;border-radius:50%;background:#2f6bd8;color:#fff;font:800 28px/60px Manrope;text-align:center;box-shadow:0 0 0 4px rgba(255,255,255,.9)}}
.bub{{background:rgba(255,255,255,.94);border-radius:32px 32px 32px 8px;padding:26px 34px;font:500 31px/1.38 Manrope;box-shadow:0 14px 40px rgba(8,20,50,.25)}}
.btn{{display:inline-block;margin-top:22px;background:#2f6bd8;color:#fff;font:700 28px Manrope;padding:18px 40px;border-radius:50px}}
.hl{{background:#ffd24a;padding:0 12px;margin:0 -3px;border-radius:12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.cap{{position:absolute;left:84px;top:250px;font:700 44px Manrope;color:#fff}}
.hd b{{font:700 26px Manrope;display:block}}.hd div:not(.av){{margin-left:0}}
.card .hd{{justify-content:flex-start;gap:16px}}.card .hd small{{display:block;font:500 22px Manrope}}
.qb{{font:800 62px/1.18 Manrope;letter-spacing:-1px;margin-top:6px}}
</style>{bg}{body}'''
for i,d in enumerate(S,1): open(f'slide{i}.html','w').write(html(i,d))
