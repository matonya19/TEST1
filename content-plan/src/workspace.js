// Рабочее пространство отделяет данные разных клиентов внутри одного
// Firebase-проекта. Значение задаётся на этапе сборки (VITE_WORKSPACE_ID),
// отдельно для каждой опубликованной страницы (Room Bloom / Ульяна / Школа).
export function getWorkspaceId() {
  return import.meta.env.VITE_WORKSPACE_ID || 'default';
}

export const COMBINED_WORKSPACE_ID = 'combined';

// Источники для сводной странички: какие реальные пространства объединять
// и каким цветом подсвечивать публикации каждого из них.
export const SOURCE_WORKSPACES = [
  { id: 'roombloom', label: 'Room Bloom', color: '#4A9990' },
  { id: 'shkola', label: 'Школа', color: '#6D8FBD' },
  { id: 'ulyana', label: 'Ульяна', color: '#C77A93' },
  { id: 'natalia', label: 'Наталья', color: '#8A7CB0' },
];

export function isCombinedWorkspace() {
  return getWorkspaceId() === COMBINED_WORKSPACE_ID;
}

export function makeMergedId(workspaceId, originalId) {
  return `${workspaceId}::${originalId}`;
}

export function splitMergedId(mergedId) {
  const idx = (mergedId || '').indexOf('::');
  if (idx === -1) return { workspaceId: null, originalId: mergedId };
  return { workspaceId: mergedId.slice(0, idx), originalId: mergedId.slice(idx + 2) };
}
