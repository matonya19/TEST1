# Черная пятница в SHKOLA — анимированный пост

Квадрат 1080×1080, 9 сек, 30 fps, без звука.

- `shkola_black_friday.mp4` — версия без даты («СТАРТОВАЛА! ВЫГОДА ДО 50%»)
- `shkola_black_friday_20nov.mp4` — с датой («ТОЛЬКО ДО 20 НОЯБРЯ»)

## Перерендер с другой датой

```bash
cd black-friday
npm install
node render.js 28 shkola_black_friday_28nov.mp4   # число ноября, имя файла
```
Нужны Node, Playwright (Chromium) и ffmpeg.
