import { useMemo, useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { STATUSES, STATUS_STYLES } from '../constants.js';
import { matchesFilters } from '../utils/filters.js';
import PostCard from './PostCard.jsx';

export default function StatusBoardView({ posts, projectsById }) {
  const { activeProjectId, search, filters, setEditorTarget, pendingDeleteIds, updatePost } = useApp();
  const [dragOverStatus, setDragOverStatus] = useState(null);

  const byStatus = useMemo(() => {
    const map = new Map(STATUSES.map((s) => [s, []]));
    for (const post of posts) {
      if (post.isIdea || post.isArchived || pendingDeleteIds.has(post.id)) continue;
      if (!matchesFilters(post, { activeProjectId, search, filters })) continue;
      if (map.has(post.status)) map.get(post.status).push(post);
    }
    for (const arr of map.values()) {
      arr.sort((a, b) => (a.date || '9999-99-99').localeCompare(b.date || '9999-99-99'));
    }
    return map;
  }, [posts, activeProjectId, search, filters, pendingDeleteIds]);

  function handleDrop(e, status) {
    e.preventDefault();
    setDragOverStatus(null);
    const id = e.dataTransfer.getData('text/post-id');
    if (id) {
      const post = posts.find((p) => p.id === id);
      if (post && post.status !== status) updatePost(id, { status });
    }
  }

  return (
    <div className="status-board">
      {STATUSES.map((status) => {
        const style = STATUS_STYLES[status];
        const items = byStatus.get(status) || [];
        return (
          <div
            key={status}
            className={`status-column ${dragOverStatus === status ? 'status-column--drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOverStatus(status); }}
            onDragLeave={() => setDragOverStatus((s) => (s === status ? null : s))}
            onDrop={(e) => handleDrop(e, status)}
          >
            <div className="status-column__header">
              <span className="status-column__dot" style={{ background: style.dot }} />
              <span className="status-column__title">{status}</span>
              <span className="status-column__count">{items.length}</span>
            </div>
            <div className="status-column__cards">
              {items.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  project={projectsById.get(post.projectId)}
                  onOpen={() => setEditorTarget({ mode: 'edit', id: post.id })}
                />
              ))}
              {items.length === 0 && <div className="status-column__empty">Пусто</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
