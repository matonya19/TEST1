import { useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { PROJECT_COLORS } from '../constants.js';

export default function ProjectManagerModal() {
  const { projects, projectManagerOpen, setProjectManagerOpen, addProject, updateProject, clearDemoData, posts } = useApp();
  const [newName, setNewName] = useState('');

  if (!projectManagerOpen) return null;

  const hasDemo = projects.some((p) => p.isDemo) || posts.some((p) => p.isDemo);

  function handleCreate() {
    const name = newName.trim();
    if (!name) return;
    const usedColors = new Set(projects.map((p) => p.color));
    const color = PROJECT_COLORS.find((c) => !usedColors.has(c)) || PROJECT_COLORS[projects.length % PROJECT_COLORS.length];
    addProject(name, color);
    setNewName('');
  }

  return (
    <div className="modal-overlay" onClick={() => setProjectManagerOpen(false)}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2>Проекты</h2>
          <button type="button" className="modal__close" onClick={() => setProjectManagerOpen(false)} aria-label="Закрыть">×</button>
        </div>
        <div className="modal__body">
          <ul className="project-list">
            {projects.map((project) => (
              <li key={project.id} className="project-list__item">
                <span className="project-list__color-dot" style={{ background: project.color }} />
                <input
                  type="text"
                  className="project-list__name-input"
                  value={project.name}
                  onChange={(e) => updateProject(project.id, { name: e.target.value })}
                />
                {project.isDemo && <span className="project-list__demo-badge">пример</span>}
                <div className="project-list__colors">
                  {PROJECT_COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      className={`color-swatch ${project.color === color ? 'color-swatch--active' : ''}`}
                      style={{ background: color }}
                      aria-label={`Цвет проекта ${color}`}
                      onClick={() => updateProject(project.id, { color })}
                    />
                  ))}
                </div>
              </li>
            ))}
          </ul>
          <div className="project-list__add">
            <input
              type="text"
              placeholder="Название нового проекта"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleCreate(); }}
            />
            <button type="button" onClick={handleCreate}>Добавить проект</button>
          </div>
          {hasDemo && (
            <div className="project-list__demo-cleanup">
              <p>В плане есть демонстрационный проект «Room Bloom» с примерами публикаций.</p>
              <button type="button" className="btn-muted" onClick={clearDemoData}>Очистить примеры</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
