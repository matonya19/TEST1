import { useMemo, useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { matchesFilters } from '../utils/filters.js';
import PostCard from './PostCard.jsx';

export default function NoDateShelf({ posts, projectsById }) {
  const { activeProjectId, search, filters, setEditorTarget, pendingDeleteIds } = useApp();
  const [collapsed, setCollapsed] = useState(false);

  const items = useMemo(() => {
    return posts.filter((p) => !p.isIdea && !p.isArchived && !p.date && !pendingDeleteIds.has(p.id))
      .filter((p) => matchesFilters(p, { activeProjectId, search, filters }));
  }, [posts, activeProjectId, search, filters, pendingDeleteIds]);

  if (items.length === 0) return null;

  return (
    <div className="no-date-shelf">
      <button type="button" className="no-date-shelf__toggle" onClick={() => setCollapsed((c) => !c)}>
        {collapsed ? '▸' : '▾'} Без даты ({items.length})
      </button>
      {!collapsed && (
        <div className="no-date-shelf__items">
          {items.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              project={projectsById.get(post.projectId)}
              onOpen={() => setEditorTarget({ mode: 'edit', id: post.id })}
              compact
            />
          ))}
        </div>
      )}
    </div>
  );
}
