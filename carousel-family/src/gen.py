FONTS='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/'
S=[
 dict(img='p1.jpg',pos='top',col='navy',x=84,w=820,hl='жизнь',h='Как изменится ваша жизнь на онлайн-обучении?',s='Обычный день семьи в SHKOLA'),
 dict(img='p2.jpg',pos='bottom',col='navy',x=84,w=900,hl='не нужно',h='Утром больше не нужно ехать в школу',s='Вместо дороги — завтрак дома. К началу урока достаточно открыть ноутбук.'),
 dict(img='p3.jpg',pos='top',col='white',x=430,w=580,hl='есть время',h='На вопрос ребёнка есть время',s='В мини-классе до восьми учеников. Если тема сложная, учитель может объяснить её ещё раз.'),
 dict(img='p5.jpg',pos='top',col='navy',x=84,w=760,hl='сложной теме',h='После болезни можно вернуться к сложной теме',s='Ученик SHKOLA: «И меня никто не торопит».'),
 dict(quote='Благодаря ей я начала читать книги',who='Соня, ученица SHKOLA',pos='top',col='white',x=84,w=900,hl='книги',h='Книгу открывают и после урока',s=''),
 dict(img='p4.jpg',pos='bottom',col='navy',x=84,w=900,hl='3 бесплатных дня',h='Подойдёт ли это вашей семье?',s='Попробуйте 3 бесплатных дня в SHKOLA. Ребёнок познакомится с классом и побывает на уроках по расписанию.',cta='Запись по ссылке в профиле'),
]
def html(i,d):
    bg=f'<img class="bg" src="bg_{d["img"][:2]}.jpg">' if 'img' in d else '<div class="bg qbg"></div>'
    hl=lambda t:t.replace(d['hl'],f'<span class=hl>{d["hl"]}</span>') if d.get('hl') else t
    quote=''
    if 'quote' in d:
        quote=f'<div class=q><div class=qm>“</div><div class=qt>{hl(d["quote"])}</div><div class=qw>{d["who"]}</div></div>'
        h=d['h']; hh=h
    else: hh=hl(d['h'])
    cta=f'<div class="btn">{d["cta"]}</div>' if d.get('cta') else ''
    sub=f'<p>{d["s"]}</p>' if d['s'] else ''
    colr='#0d1b3d' if d['col']=='navy' else '#fff'
    shadow='none' if d['col']=='navy' else '0 2px 22px rgba(0,0,0,.5),0 1px 3px rgba(0,0,0,.35)'
    place='top:150px' if d['pos']=='top' else 'bottom:96px'
    return f'''<!doctype html><meta charset=utf-8><style>
@import url("{FONTS}cyrillic-500.css");@import url("{FONTS}cyrillic-600.css");@import url("{FONTS}cyrillic-700.css");@import url("{FONTS}cyrillic-800.css");@import url("{FONTS}latin-700.css");@import url("{FONTS}latin-800.css");@import url("{FONTS}latin-500.css");@import url("{FONTS}latin-600.css");
*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1350px;font-family:Manrope;position:relative;overflow:hidden;background:#2f6bd8}}
.bg{{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover}}.qbg{{background:linear-gradient(160deg,#3d7cf0,#2457c4)}}
.top{{position:absolute;left:72px;right:72px;top:62px;height:48px;display:flex;justify-content:space-between;align-items:center}}
.top img{{height:46px}}.top span{{font:600 26px Manrope;color:{'#0d1b3d' if (d['col']=='navy') else '#fff'};opacity:.7}}
.tx{{position:absolute;left:{d['x']}px;width:{d['w']}px;{place};color:{colr};text-shadow:{shadow}}}
h1{{font:800 {'46px/1.2' if 'quote' in d else '64px/1.16'} Manrope;letter-spacing:-.6px}}
p{{font:500 31px/1.4 Manrope;margin-top:26px;max-width:820px}}
.hl{{background:#ffd24a;color:#0d1b3d;text-shadow:none;padding:0 14px;margin:0 -4px;border-radius:14px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.btn{{display:inline-block;margin-top:36px;background:#2f6bd8;color:#fff;text-shadow:none;font:700 30px Manrope;padding:22px 46px;border-radius:50px}}
.q{{position:absolute;left:84px;right:84px;top:380px;color:#fff}}
.qm{{font:800 260px/0.7 Manrope;color:#ffd24a;height:130px}}.qt{{font:800 88px/1.18 Manrope;margin-top:30px;letter-spacing:-1px}}.qw{{font:600 32px Manrope;opacity:.85;margin-top:48px}}
</style>{bg}<div class=top><img src="{'logo.png' if d['col']=='navy' else 'logo_w.png'}"><span>{i}/6</span></div>{quote}
<div class=tx><h1>{hh}</h1>{sub}{cta}</div>'''
for i,d in enumerate(S,1): open(f'slide{i}.html','w').write(html(i,d))
