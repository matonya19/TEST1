import { useApp } from '../AppContext.jsx';

const VIEWS = [
  { key: 'week', label: 'Неделя' },
  { key: 'month', label: 'Месяц' },
  { key: 'status', label: 'По статусам' },
];

export default function TopBar() {
  const {
    projects, activeProjectId, setActiveProjectId,
    view, setView, search, setSearch, section,
    setEditorTarget, setProjectManagerOpen, addPost,
    mobileNavOpen, setMobileNavOpen,
  } = useApp();

  function handleAddPost() {
    const created = addPost({ projectId: activeProjectId !== 'all' ? activeProjectId : null });
    setEditorTarget({ mode: 'edit', id: created.id, isNew: true });
  }

  return (
    <header className="topbar">
      <div className="topbar__row">
        <button
          type="button"
          className="topbar__hamburger"
          onClick={() => setMobileNavOpen((v) => !v)}
          aria-label={mobileNavOpen ? 'Закрыть меню' : 'Открыть меню'}
        >
          ☰
        </button>
        <select
          className="topbar__project-select"
          value={activeProjectId}
          onChange={(e) => setActiveProjectId(e.target.value)}
          aria-label="Проект"
        >
          <option value="all">Все проекты</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <button type="button" className="topbar__manage-link" onClick={() => setProjectManagerOpen(true)}>
          Проекты…
        </button>

        {section === 'plan' && (
          <div className="topbar__view-switch" role="tablist" aria-label="Режим отображения">
            {VIEWS.map((v) => (
              <button
                key={v.key}
                type="button"
                role="tab"
                aria-selected={view === v.key}
                className={`topbar__view-btn ${view === v.key ? 'topbar__view-btn--active' : ''}`}
                onClick={() => setView(v.key)}
              >
                {v.label}
              </button>
            ))}
          </div>
        )}

        <div className="topbar__search">
          <span className="topbar__search-icon" aria-hidden="true">⌕</span>
          <input
            type="search"
            placeholder="Поиск по теме и тексту…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Поиск публикаций"
          />
        </div>

        <button
          type="button"
          className="topbar__add-btn"
          onClick={handleAddPost}
        >
          + Добавить публикацию
        </button>
      </div>
    </header>
  );
}
