import { useMemo } from 'react';
import { useApp } from '../AppContext.jsx';
import { matchesFilters } from '../utils/filters.js';
import QuickAddInput from './QuickAddInput.jsx';
import { SOURCE_WORKSPACES, splitMergedId } from '../workspace.js';
import { STATUS_STYLES } from '../constants.js';

export default function IdeasView({ posts, projectsById }) {
  const { activeProjectId, search, filters, addPost, updatePost, requestDeletePost, setEditorTarget, pendingDeleteIds, isCombined } = useApp();
  const needsProjectFirst = isCombined && activeProjectId === 'all';

  // На сводной странице поле "идея без даты" никто не использует — там статус
  // "Идея" стоит на уже датированных публикациях. Поэтому здесь вкладка
  // показывает не isIdea-записи, а весь неопубликованный бэклог по всем
  // клиентам ("идеи и планы, которые нужно осуществить"), а не только
  // дневной список текущего дня.
  const ideas = useMemo(() => {
    const matches = isCombined
      ? (p) => !p.isIdea && !p.isArchived && p.status !== 'Опубликовано'
      : (p) => p.isIdea && !p.isArchived;
    return posts
      .filter((p) => matches(p) && !pendingDeleteIds.has(p.id))
      .filter((p) => matchesFilters(p, { activeProjectId, search, filters }))
      .sort((a, b) => {
        if (isCombined) {
          if (a.date && b.date) return a.date.localeCompare(b.date);
          if (a.date) return -1;
          if (b.date) return 1;
        }
        return b.createdAt - a.createdAt;
      });
  }, [posts, activeProjectId, search, filters, pendingDeleteIds, isCombined]);

  return (
    <div className="ideas-view">
      <div className="ideas-view__intro">
        <h2>{isCombined ? 'Идеи и планы' : 'Идеи'}</h2>
        <p>
          {isCombined
            ? 'Всё, что ещё не опубликовано, сразу со всех клиентов — помечено цветом источника. Клик по публикации откроет редактор.'
            : 'Сохраняйте мысли одной строкой без даты. Когда идея созреет — назначьте дату или перенесите её в план.'}
        </p>
      </div>
      {!isCombined && (
        <QuickAddInput
          alwaysOpen
          placeholder="Новая идея одной строкой…"
          buttonLabel="+ Добавить идею"
          disabled={needsProjectFirst}
          disabledTitle="Выберите конкретный проект сверху — так понятно, куда сохранить идею"
          onSubmit={(topic) => addPost({ topic, isIdea: true, projectId: activeProjectId !== 'all' ? activeProjectId : null })}
        />
      )}
      <ul className="ideas-list">
        {ideas.map((idea) => {
          const project = projectsById.get(idea.projectId);
          const ws = isCombined ? SOURCE_WORKSPACES.find((w) => w.id === splitMergedId(idea.id).workspaceId) : null;
          const style = STATUS_STYLES[idea.status] || STATUS_STYLES['Идея'];
          return (
            <li key={idea.id} className="idea-row">
              {ws && <span className="idea-row__badge" style={{ background: ws.color }}>{ws.label}</span>}
              <button type="button" className="idea-row__topic" onClick={() => setEditorTarget({ mode: 'edit', id: idea.id })}>
                {idea.topic}
              </button>
              {project && !isCombined && <span className="idea-row__project" style={{ color: project.color }}>{project.name}</span>}
              {isCombined && (
                <span className="post-card__status" style={{ background: style.bg, color: style.text }}>
                  <span className="post-card__dot" style={{ background: style.dot }} />
                  {idea.status}
                </span>
              )}
              {isCombined && idea.date && <span className="idea-row__date">{idea.date.slice(8, 10)}.{idea.date.slice(5, 7)}</span>}
              <div className="idea-row__actions">
                {!isCombined && (
                  <>
                    <input
                      type="date"
                      className="idea-row__date-input"
                      title="Назначить дату"
                      onChange={(e) => { if (e.target.value) updatePost(idea.id, { isIdea: false, date: e.target.value }); }}
                    />
                    <button type="button" className="btn-muted btn-small" onClick={() => updatePost(idea.id, { isIdea: false })}>
                      Перенести в план
                    </button>
                  </>
                )}
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
        {ideas.length === 0 && (
          <li className="ideas-list__empty">
            {isCombined ? 'Всё опубликовано — непубликованных планов нет.' : 'Идей пока нет — добавьте первую мысль выше.'}
          </li>
        )}
      </ul>
    </div>
  );
}
