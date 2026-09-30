// Рабочее пространство отделяет данные разных клиентов внутри одного
// Firebase-проекта. Значение задаётся на этапе сборки (VITE_WORKSPACE_ID),
// отдельно для каждой опубликованной страницы (Room Bloom / Ульяна / Школа).
export function getWorkspaceId() {
  return import.meta.env.VITE_WORKSPACE_ID || 'default';
}
