# Черная пятница в SHKOLA — анимированный пост

Концепция «Дневник без оценок»: лаймовый маркер стирает двойки в дневнике,
затем две карточки: «Обучение в школе −50% на первый месяц» и «Репетиторство −20%*». Фирменный зелёный стиль.
Формат 1080×1350 (4:5), 11,5 сек, 30 fps, без звука.

- `shkola_black_friday_20nov_1080x1920.mp4` — видео 9:16 (слайд 1 карусели / сторис)
- `shkola_black_friday_slide2_1080x1920.png` — слайд 2: преимущества SHKOLA + сводка скидок
- `shkola_black_friday_20nov_1080x1350.mp4` — видео 4:5
- `shkola_black_friday_20nov_1080x1080.mp4` — та же, квадрат
- `old-pink/`, `old-green/` — предыдущие версии (не актуальны)

## Перерендер с другой датой

```bash
cd black-friday
npm install
H=1350 node render.js 20 shkola_black_friday_20nov_1080x1350.mp4   # число ноября, имя файла
```
Нужны Node, Playwright (Chromium) и ffmpeg.

Видео 9:16: `H=1920 node render.js 20 out.mp4`.
Слайд 2: собирается из `slide_src.html` (в `LOGO_SRC` подставляется логотип), `node shot.js 20 slide.png`.

## Версии с озвучкой (~19,6 сек)

- `shkola_black_friday_20nov_1080x1350_voice.mp4`, `shkola_black_friday_20nov_1080x1920_voice.mp4`
- Текст озвучки: `voice/lines.txt`, фразы: `voice/seg1..6.wav` (синтез Piper, голос ru-irinia-medium).
- Сборка: `SCENE=scene_voice.html node render_vo.js 20 out.mp4 1350 voice` — таймлайн растянут под фразы (см. WARP/VO в render_vo.js).
