import { useMemo } from 'react';
import { useApp } from '../AppContext.jsx';
import { matchesFilters } from '../utils/filters.js';
import QuickAddInput from './QuickAddInput.jsx';

export default function IdeasView({ posts, projectsById }) {
  const { activeProjectId, search, filters, addPost, updatePost, requestDeletePost, setEditorTarget, pendingDeleteIds } = useApp();

  const ideas = useMemo(() => {
    return posts
      .filter((p) => p.isIdea && !p.isArchived && !pendingDeleteIds.has(p.id))
      .filter((p) => matchesFilters(p, { activeProjectId, search, filters }))
      .sort((a, b) => b.createdAt - a.createdAt);
  }, [posts, activeProjectId, search, filters, pendingDeleteIds]);

  return (
    <div className="ideas-view">
      <div className="ideas-view__intro">
        <h2>Идеи</h2>
        <p>Сохраняйте мысли одной строкой без даты. Когда идея созреет — назначьте дату или перенесите её в план.</p>
      </div>
      <QuickAddInput
        alwaysOpen
        placeholder="Новая идея одной строкой…"
        buttonLabel="+ Добавить идею"
        onSubmit={(topic) => addPost({ topic, isIdea: true, projectId: activeProjectId !== 'all' ? activeProjectId : null })}
      />
      <ul className="ideas-list">
        {ideas.map((idea) => {
          const project = projectsById.get(idea.projectId);
          return (
            <li key={idea.id} className="idea-row">
              <button type="button" className="idea-row__topic" onClick={() => setEditorTarget({ mode: 'edit', id: idea.id })}>
                {idea.topic}
              </button>
              {project && <span className="idea-row__project" style={{ color: project.color }}>{project.name}</span>}
              <div className="idea-row__actions">
                <input
                  type="date"
                  className="idea-row__date-input"
                  title="Назначить дату"
                  onChange={(e) => { if (e.target.value) updatePost(idea.id, { isIdea: false, date: e.target.value }); }}
                />
                <button type="button" className="btn-muted btn-small" onClick={() => updatePost(idea.id, { isIdea: false })}>
                  Перенести в план
                </button>
                <button
                  type="button"
                  className="idea-row__delete"
                  aria-label="Удалить идею"
                  onClick={() => requestDeletePost(idea.id, idea.topic)}
                >
                  ×
                </button>
              </div>
            </li>
          );
        })}
        {ideas.length === 0 && <li className="ideas-list__empty">Идей пока нет — добавьте первую мысль выше.</li>}
      </ul>
    </div>
  );
}
