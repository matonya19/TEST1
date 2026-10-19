// Каждая опубликованная страница (Room Bloom / Школа / Ульяна / Наталья / "Мой"
// / сводная "Все") получает свою иконку и заголовок вкладки — чтобы на рабочем
// столе/панели задач они отличались друг от друга, а не только текстом.
// Запускается автоматически перед vite build (см. package.json → "prebuild"),
// подставляя нужный favicon.svg/apple-touch-icon.png и <title> под текущий
// VITE_WORKSPACE_ID. Без VITE_WORKSPACE_ID (локальная сборка, версия для
// Claude Artifact) ничего не меняет — остаётся исходная общая иконка.
import { readFileSync, writeFileSync, copyFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const assetsDir = path.join(root, 'assets-icons');
const publicDir = path.join(root, 'public');
const indexHtmlPath = path.join(root, 'index.html');

const WORKSPACE_META = {
  roombloom: { title: 'Room Bloom — контент-план' },
  shkola: { title: 'Школа — контент-план' },
  ulyana: { title: 'Ульяна — контент-план' },
  natalia: { title: 'Наталья — контент-план' },
  interview: { title: 'Курс интервью — контент-план' },
  my: { title: 'Мой контент-план' },
  combined: { title: 'Все клиенты — сводный план' },
};

const workspaceId = process.env.VITE_WORKSPACE_ID;
const meta = workspaceId && WORKSPACE_META[workspaceId];

if (!meta) {
  console.log('[set-workspace-icon] VITE_WORKSPACE_ID не задан или не распознан — иконка не меняется.');
  process.exit(0);
}

const svgSrc = path.join(assetsDir, `${workspaceId}.svg`);
const pngSrc = path.join(assetsDir, `${workspaceId}-180.png`);

if (!existsSync(svgSrc)) {
  console.error(`[set-workspace-icon] Не найдена иконка ${svgSrc}`);
  process.exit(1);
}

copyFileSync(svgSrc, path.join(publicDir, 'favicon.svg'));
if (existsSync(pngSrc)) {
  copyFileSync(pngSrc, path.join(publicDir, 'apple-touch-icon.png'));
}

let html = readFileSync(indexHtmlPath, 'utf8');
html = html.replace(/<title>.*<\/title>/, `<title>${meta.title}</title>`);
if (!html.includes('apple-touch-icon')) {
  html = html.replace(
    '<link rel="icon" type="image/svg+xml" href="/favicon.svg" />',
    '<link rel="icon" type="image/svg+xml" href="/favicon.svg" />\n    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />',
  );
}
writeFileSync(indexHtmlPath, html);

console.log(`[set-workspace-icon] ${workspaceId}: иконка и заголовок «${meta.title}» применены.`);
