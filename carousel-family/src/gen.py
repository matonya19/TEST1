FONTS='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/'
S=[
 dict(img='p1.jpg',pos='50% 34%',h='Как изменится ваша жизнь на онлайн-обучении?',s='Обычный день семьи в SHKOLA'),
 dict(img='p2.jpg',pos='50% 33%',h='Утром больше не нужно ехать в школу',s='Вместо дороги — завтрак дома. К началу урока достаточно открыть ноутбук.'),
 dict(img='p3.jpg',pos='50% 20%',h='На вопрос ребёнка есть время',s='В мини-классе до восьми учеников. Если тема сложная, учитель может объяснить её ещё раз.'),
 dict(img='p5.jpg',pos='50% 35%',h='После болезни можно вернуться к сложной теме',s='Ученик SHKOLA: «И меня никто не торопит».'),
 dict(quote='Благодаря ей я начала читать книги',who='Соня, ученица SHKOLA',h='Книгу открывают и после урока',s=''),
 dict(img='p4.jpg',pos='50% 50%',ph=620,h='Подойдёт ли это вашей семье?',s='Попробуйте 3 бесплатных дня в SHKOLA. Ребёнок познакомится с классом и побывает на уроках по расписанию.',cta='Запись по ссылке в профиле'),
]
def html(i,d):
    bg=f'<img class="bg" src="bg_{d["img"][:2]}.jpg">' if 'img' in d else '<div class="bg qbg"></div>'
    q=f'<div class="qm">“</div><div class="qt">{d["quote"]}</div><div class="qw">{d["who"]}</div>' if 'quote' in d else ''
    cta=f'<div class="btn">{d["cta"]}</div>' if d.get('cta') else ''
    sub=f'<p>{d["s"]}</p>' if d['s'] else ''
    return f'''<!doctype html><meta charset=utf-8><style>
@import url("{FONTS}cyrillic-500.css");@import url("{FONTS}cyrillic-600.css");@import url("{FONTS}cyrillic-700.css");@import url("{FONTS}latin-500.css");@import url("{FONTS}latin-600.css");@import url("{FONTS}latin-700.css");
*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1350px;font-family:Manrope;position:relative;overflow:hidden;background:#2f6bd8}}
.bg{{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover}}.qbg{{background:linear-gradient(160deg,#3d7cf0,#2457c4)}}
.sh{{position:absolute;left:0;right:0;bottom:0;height:820px;background:linear-gradient(to top,rgba(6,14,38,.92) 0%,rgba(6,14,38,.78) 38%,rgba(6,14,38,0) 100%)}}
.shT{{position:absolute;left:0;right:0;top:0;height:260px;background:linear-gradient(to bottom,rgba(6,14,38,.45),rgba(6,14,38,0))}}
.top{{position:absolute;left:72px;right:72px;top:62px;height:48px;display:flex;justify-content:space-between;align-items:center}}
.top img{{height:46px}}.top span{{font:600 26px Manrope;color:#fff;opacity:.85}}
.q{{position:absolute;left:84px;right:84px;top:300px}}
.qm{{font:700 260px/0.7 Manrope;color:#ffd24a;height:130px}}.qt{{font:700 78px/1.15 Manrope;color:#fff;margin-top:26px}}.qw{{font:600 32px Manrope;color:#fff;opacity:.85;margin-top:44px}}
.tx{{position:absolute;left:84px;right:84px;bottom:{'96' if True else ''}px;color:#fff}}
h1{{font:700 62px/1.13 Manrope;letter-spacing:-.5px}}
p{{font:500 31px/1.4 Manrope;margin-top:24px;opacity:.92;max-width:860px}}
.btn{{display:inline-block;margin-top:36px;background:#fff;color:#0d1b3d;font:700 30px Manrope;padding:22px 46px;border-radius:50px}}
</style>{bg}{'' if 'quote' in d else '<div class=shT></div><div class=sh></div>'}
<div class=top><img src="logo_w.png"><span>{i}/6</span></div><div class=q>{q}</div>
<div class=tx><h1>{d["h"]}</h1>{sub}{cta}</div>'''
for i,d in enumerate(S,1): open(f'slide{i}.html','w').write(html(i,d))
