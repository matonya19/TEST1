const STORAGE_KEY = 'smm-content-plan-v1';
export const SCHEMA_VERSION = 1;

export function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object') return null;
    if (!Array.isArray(parsed.projects) || !Array.isArray(parsed.posts)) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // хранилище недоступно (например, приватный режим) — молча пропускаем
  }
}

export function validateImportedData(data) {
  if (!data || typeof data !== 'object') return 'Файл повреждён: неверный формат.';
  if (!Array.isArray(data.projects)) return 'Файл повреждён: отсутствует список проектов.';
  if (!Array.isArray(data.posts)) return 'Файл повреждён: отсутствует список публикаций.';
  return null;
}
