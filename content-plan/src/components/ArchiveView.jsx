import { useMemo } from 'react';
import { useApp } from '../AppContext.jsx';
import { matchesFilters } from '../utils/filters.js';
import { STATUS_STYLES } from '../constants.js';
import PlatformIcon from './PlatformIcon.jsx';

export default function ArchiveView({ posts, projectsById }) {
  const { activeProjectId, search, filters, unarchivePost, requestDeletePost, setEditorTarget, pendingDeleteIds } = useApp();

  const archived = useMemo(() => {
    return posts
      .filter((p) => p.isArchived && !pendingDeleteIds.has(p.id))
      .filter((p) => matchesFilters(p, { activeProjectId, search, filters }))
      .sort((a, b) => b.updatedAt - a.updatedAt);
  }, [posts, activeProjectId, search, filters, pendingDeleteIds]);

  return (
    <div className="archive-view">
      <div className="ideas-view__intro">
        <h2>Архив</h2>
        <p>Публикации, которые больше не в активном плане. Их можно вернуть в план или удалить окончательно.</p>
      </div>
      <ul className="archive-list">
        {archived.map((post) => {
          const style = STATUS_STYLES[post.status] || STATUS_STYLES['Идея'];
          const project = projectsById.get(post.projectId);
          return (
            <li key={post.id} className="archive-row">
              <button type="button" className="archive-row__topic" onClick={() => setEditorTarget({ mode: 'edit', id: post.id })}>
                {post.topic || 'Без темы'}
              </button>
              <span className="archive-row__meta">
                <PlatformIcon platform={post.platform} /> {post.platform} · {post.format}
              </span>
              <span className="post-card__status" style={{ background: style.bg, color: style.text }}>
                <span className="post-card__dot" style={{ background: style.dot }} />
                {post.status}
              </span>
              {project && <span className="archive-row__project" style={{ color: project.color }}>{project.name}</span>}
              <div className="archive-row__actions">
                <button type="button" className="btn-muted btn-small" onClick={() => unarchivePost(post.id)}>Вернуть в план</button>
                <button type="button" className="btn-danger btn-small" onClick={() => requestDeletePost(post.id, post.topic)}>Удалить</button>
              </div>
            </li>
          );
        })}
        {archived.length === 0 && <li className="archive-list__empty">Архив пуст.</li>}
      </ul>
    </div>
  );
}
