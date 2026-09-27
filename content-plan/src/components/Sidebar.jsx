import { useApp } from '../AppContext.jsx';

const ITEMS = [
  { key: 'plan', label: 'Контент-план', icon: '🗂' },
  { key: 'ideas', label: 'Идеи', icon: '💡' },
  { key: 'archive', label: 'Архив', icon: '🗄' },
];

export default function Sidebar() {
  const { section, setSection, sidebarCollapsed, setSidebarCollapsed, setDataPanelOpen } = useApp();

  return (
    <aside className={`sidebar ${sidebarCollapsed ? 'sidebar--collapsed' : ''}`}>
      <button
        type="button"
        className="sidebar__toggle"
        onClick={() => setSidebarCollapsed((v) => !v)}
        aria-label={sidebarCollapsed ? 'Развернуть панель' : 'Свернуть панель'}
        title={sidebarCollapsed ? 'Развернуть панель' : 'Свернуть панель'}
      >
        {sidebarCollapsed ? '»' : '«'}
      </button>
      <nav className="sidebar__nav">
        {ITEMS.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`sidebar__item ${section === item.key ? 'sidebar__item--active' : ''}`}
            onClick={() => setSection(item.key)}
            title={item.label}
          >
            <span className="sidebar__icon" aria-hidden="true">{item.icon}</span>
            {!sidebarCollapsed && <span className="sidebar__label">{item.label}</span>}
          </button>
        ))}
      </nav>
      <button
        type="button"
        className="sidebar__item sidebar__settings"
        onClick={() => setDataPanelOpen(true)}
        title="Хранение данных, экспорт и импорт"
      >
        <span className="sidebar__icon" aria-hidden="true">⚙</span>
        {!sidebarCollapsed && <span className="sidebar__label">Данные</span>}
      </button>
    </aside>
  );
}
