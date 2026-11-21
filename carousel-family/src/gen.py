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
    ph=d.get('ph',720)
    media=(f'<div class="ph" style="height:{ph}px"><img src="{d["img"]}" style="object-position:{d["pos"]}"></div>' if 'img' in d else
      f'<div class="ph q" style="height:{ph}px"><div class="qm">“</div><div class="qt">{d["quote"]}</div><div class="qw">{d["who"]}</div></div>')
    cta=f'<div class="btn">{d["cta"]}</div>' if d.get('cta') else ''
    return f'''<!doctype html><meta charset=utf-8><style>
@import url("{FONTS}cyrillic-500.css");@import url("{FONTS}cyrillic-600.css");@import url("{FONTS}cyrillic-700.css");@import url("{FONTS}latin-500.css");@import url("{FONTS}latin-600.css");@import url("{FONTS}latin-700.css");
*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1350px;background:#EAF3FD;font-family:Manrope;position:relative;overflow:hidden}}
.top{{position:absolute;left:72px;right:72px;top:62px;height:48px;display:flex;justify-content:space-between;align-items:center}}
.top img{{height:44px}}.top span{{font:600 26px Manrope;color:#7f90ab}}
.ph{{position:absolute;left:72px;top:150px;width:936px;border-radius:32px;overflow:hidden}}
.ph img{{width:100%;height:100%;object-fit:cover;display:block}}
.q{{background:#2f6bd8;color:#fff;padding:90px 80px;display:flex;flex-direction:column;justify-content:center}}
.qm{{font:700 220px/0.7 Manrope;color:#ffd24a;height:110px}}.qt{{font:700 66px/1.2 Manrope;margin-top:20px}}.qw{{font:600 30px Manrope;opacity:.85;margin-top:40px}}
.tx{{position:absolute;left:72px;width:936px;top:{150+ph+56}px}}
.bar{{width:56px;height:8px;border-radius:4px;background:#ffc93c;margin-bottom:28px}}
h1{{font:700 58px/1.15 Manrope;color:#0d1b3d;letter-spacing:-.5px;max-width:900px}}
p{{font:500 30px/1.4 Manrope;color:#4a5b78;margin-top:22px;max-width:840px}}
.btn{{display:inline-block;margin-top:34px;background:#2f6bd8;color:#fff;font:700 30px Manrope;padding:22px 44px;border-radius:50px}}
</style><div class=top><img src="logo.png"><span>{i}/6</span></div>{media}
<div class=tx><div class=bar></div><h1>{d["h"]}</h1>{"<p>"+d["s"]+"</p>" if d["s"] else ""}{cta}</div>'''
for i,d in enumerate(S,1): open(f'slide{i}.html','w').write(html(i,d))
