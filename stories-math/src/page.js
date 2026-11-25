const B='/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/build/node_modules/@fontsource/manrope/';
const css=['cyrillic-500','cyrillic-700','cyrillic-800','latin-500','latin-700','latin-800'].map(s=>`@import url("${B}${s}.css");`).join('');
const base=`${css}*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Manrope;color:#0d1b3d}
.logo{position:absolute;top:96px;left:0;right:0;text-align:center}.logo img{height:54px}
.chip{position:absolute;top:220px;left:70px;display:inline-block;background:#fff;color:#0d1b3d;font:800 36px Manrope;padding:14px 34px;border-radius:50px;box-shadow:0 10px 26px rgba(0,0,0,.18)}
.abs{position:absolute}
.card{position:absolute;left:70px;right:70px;background:#fff;border-radius:44px;padding:44px 52px;box-shadow:0 22px 56px rgba(0,0,0,.22)}
.hl{background:#ffd23c;color:#0d1b3d;padding:0 14px;border-radius:14px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.bub{position:absolute;background:#fff;border-radius:44px;padding:34px 44px;font:700 52px/1.2 Manrope;box-shadow:0 16px 44px rgba(0,0,0,.25)}
.sh img{display:block;width:100%;filter:drop-shadow(0 26px 30px rgba(0,0,0,.25))}
@keyframes up{from{opacity:0;transform:translateY(90px) scale(.96)}to{opacity:1;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.3) rotate(-12deg)}60%{opacity:1;transform:scale(1.12) rotate(4deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
@keyframes fl{0%,100%{translate:0 0;rotate:-2deg}50%{translate:0 -26px;rotate:2deg}}
@keyframes slideL{from{opacity:0;transform:translateX(-300px)}to{opacity:1;transform:none}}
@keyframes slideR{from{opacity:0;transform:translateX(300px)}to{opacity:1;transform:none}}
@keyframes draw{from{stroke-dashoffset:var(--l)}to{stroke-dashoffset:0}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes wob{0%,100%{rotate:-6deg}50%{rotate:6deg}}
@keyframes blob{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(40px,-50px) scale(1.08)}}
.u{animation:up .7s cubic-bezier(.2,.8,.2,1) both}.p{animation:pop .75s cubic-bezier(.2,.9,.3,1.2) both}.sl{animation:slideL .7s cubic-bezier(.2,.8,.2,1) both}.sr{animation:slideR .7s cubic-bezier(.2,.8,.2,1) both}
.fl{animation:fl 3.6s ease-in-out infinite}
.bl{position:absolute;border-radius:50%;background:rgba(255,255,255,.14);animation:blob 6s ease-in-out infinite}
`;
const d=(t)=>`animation-delay:${t}s`;
const bgs=(c1,c2)=>`<div class=abs style="inset:0;background:linear-gradient(165deg,${c1},${c2})"></div><div class=bl style="width:520px;height:520px;left:-160px;top:1100px"></div><div class=bl style="width:380px;height:380px;right:-120px;top:380px;animation-delay:-2s"></div>`;
const S={
1:`${bgs('#4a8bff','#2457c4')}<div class="logo u" style="${d(0)}"><img src="logo_w.png"></div><div class="chip u" style="${d(.2)}">1 · Вызов</div>
<div class="bub sl" style="left:70px;right:200px;top:380px;border-radius:44px 44px 44px 10px;${d(.6)}">«В твоём возрасте я такие задачи <span class=hl>щёлкал</span>»</div>
<div class="bub sr" style="left:200px;right:70px;top:700px;border-radius:44px 44px 10px 44px;background:#ffd23c;${d(1.6)}">«Тогда ты <b>первый</b>»</div>
<div class="card u" style="top:1020px;padding:40px 48px;${d(2.8)}"><div style="font:800 50px/1.2 Manrope">Сегодня решаем три школьных задания</div><div style="font:500 38px/1.38 Manrope;margin-top:18px;color:#33425f">Родитель и ребёнок отвечают отдельно, а потом сравнивают, как считали</div></div>
<div class="abs p" style="left:70px;top:1450px;width:330px;${d(3.6)}"><div class="sh fl"><img src="trophy_cut.png"></div></div>`,
2:`${bgs('#ffe066','#ffb61e')}<div class="logo u"><img src="logo.png"></div><div class="chip u" style="${d(.2)};background:#0d1b3d;color:#fff">2 · Порядок действий</div>
<div class="abs p" style="left:70px;right:70px;top:410px;text-align:center;white-space:nowrap;font:800 168px/1 Manrope;letter-spacing:-4px;${d(.6)}">48 : 6 · 2 = <span style="color:#e5322d">?</span></div>
<div class="card u" style="top:790px;right:470px;${d(1.8)};padding:36px 40px"><div style="font:500 38px/1.38 Manrope;color:#33425f">Решите каждый сам. Потом спросите друг друга: <b style="color:#0d1b3d">«Какое действие ты сделал первым?»</b></div></div>
<div class="abs p" style="right:40px;top:740px;width:410px;${d(2.6)}"><div class="sh fl"><img src="calc_cut.png"></div></div>`,
3:`${bgs('#47dca0','#17a974')}<div class="logo u"><img src="logo_w.png"></div><div class="chip u" style="${d(.2)}">3 · Геометрия</div>
<div class="card u" style="top:350px;${d(.5)}"><div style="font:800 46px/1.25 Manrope">Периметр квадрата — <span class=hl>24 см</span>. Его разрезали пополам и получили два одинаковых прямоугольника.</div><div style="font:800 46px/1.25 Manrope;margin-top:14px">Какой периметр у одного из них?</div></div>
<svg class=abs style="left:70px;top:930px" width="520" height="420" viewBox="0 0 520 420"><rect x="60" y="30" width="300" height="300" rx="14" fill="rgba(255,255,255,.2)" stroke="#fff" stroke-width="10" style="--l:1300;stroke-dasharray:1300;animation:draw 1.3s ease-out both;${d(2)}"/>
<line x1="210" y1="30" x2="210" y2="330" stroke="#ffd23c" stroke-width="10" stroke-dasharray="22 18" style="animation:fade .5s both;${d(3.6)}"/>
<text x="210" y="385" text-anchor="middle" fill="#fff" font-family="Manrope" font-weight="800" font-size="34" style="animation:fade .5s both;${d(3.2)}">24 см</text></svg>
<div class="abs p" style="right:70px;top:910px;width:380px;${d(2.8)}"><div class="sh fl"><img src="geo_cut.png"></div></div>
<div class="abs u" style="left:70px;right:70px;top:1390px;font:700 42px/1.3 Manrope;color:#fff;${d(4)}">Можно нарисовать. Взрослым тоже</div>`,
4:`${bgs('#ff8a7a','#e9453a')}<div class="logo u"><img src="logo_w.png"></div><div class="chip u" style="${d(.2)}">4 · Проценты</div>
<div class="card u" style="top:340px;${d(.5)}"><div style="font:800 46px/1.25 Manrope">Рюкзак стоил <span class=hl>5 000 ₽</span>. Сначала его цена выросла на <b style="color:#e5322d">20%</b>, потом новую цену снизили на <b style="color:#e5322d">20%</b>.</div><div style="font:800 46px/1.25 Manrope;margin-top:14px">Сколько он стоит теперь?</div></div>
<div class="abs p" style="left:70px;top:900px;width:420px;${d(2)}"><div class="sh fl"><img src="bag_cut.png"></div></div>
<div class="abs u" style="left:540px;right:70px;top:960px;font:800 44px/1.3 Manrope;color:#fff;${d(3.2)}">Можно ли уже говорить:<div style="margin-top:14px;background:#fff;color:#0d1b3d;border-radius:30px;padding:24px 30px;font-size:42px;font-weight:700;box-shadow:0 14px 36px rgba(0,0,0,.2)">«Ну вот, вернули старую цену»?</div></div>`,
5:`${bgs('#9b7bff','#5b3fd6')}<div class="logo u"><img src="logo_w.png"></div><div class="chip u" style="${d(.2)}">5 · Сверяем ответы</div>
<div class="card sl" style="top:340px;padding:30px 44px;${d(.6)}"><div style="font:800 66px/1 Manrope;color:#5b3fd6">16</div><div style="font:500 36px/1.3 Manrope;margin-top:6px;color:#33425f">деление и умножение выполняем слева направо</div></div>
<div class="card sr" style="top:640px;padding:30px 44px;${d(1.6)}"><div style="font:800 66px/1 Manrope;color:#5b3fd6">18 см</div><div style="font:500 36px/1.3 Manrope;margin-top:6px;color:#33425f">сторона квадрата 6 см, а у половинки стороны 6 и 3 см</div></div>
<div class="card sl" style="top:940px;padding:30px 44px;${d(2.6)}"><div style="font:800 66px/1 Manrope;color:#5b3fd6">4 800 ₽</div><div style="font:500 36px/1.3 Manrope;margin-top:6px;color:#33425f">сначала прибавили 1 000 ₽, потом вычли 1 200 ₽</div></div>
<div class="abs u" style="left:70px;right:300px;top:1250px;font:800 46px/1.25 Manrope;color:#fff;${d(3.8)}"><span class=hl>На каком задании</span> ребёнок объяснил вам решение?</div>
<div class="abs p" style="right:40px;top:1230px;width:260px;${d(4.4)}"><div class="sh fl"><img src="check_cut.png"></div></div>`};
module.exports={base,S};
