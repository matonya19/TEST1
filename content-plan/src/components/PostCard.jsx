import { STATUS_STYLES } from '../constants.js';
import PlatformIcon from './PlatformIcon.jsx';
import CardMenu from './CardMenu.jsx';
import { useApp } from '../AppContext.jsx';
import { isPastDay, parseISODate } from '../utils/date.js';

export default function PostCard({ post, project, onOpen, draggable = true, compact = false }) {
  const { updatePost, duplicatePost, archivePost, requestDeletePost } = useApp();
  const style = STATUS_STYLES[post.status] || STATUS_STYLES['Идея'];
  const overdue = post.date && !post.isArchived && post.status !== 'Опубликовано' && isPastDay(parseISODate(post.date));

  function handleDragStart(e) {
    e.dataTransfer.setData('text/post-id', post.id);
    e.dataTransfer.effectAllowed = 'move';
  }

  return (
    <div
      className={`post-card ${compact ? 'post-card--compact' : ''}`}
      draggable={draggable}
      onDragStart={handleDragStart}
      onClick={onOpen}
      style={{ borderLeftColor: project?.color || 'var(--border)' }}
    >
      <div className="post-card__top">
        <span className="post-card__time">{post.time || '—:—'}</span>
        <span className="post-card__status" style={{ background: style.bg, color: style.text }}>
          <span className="post-card__dot" style={{ background: style.dot }} />
          {post.status}
        </span>
        <CardMenu
          post={post}
          onOpen={onOpen}
          onMoveDate={(date) => updatePost(post.id, { date })}
          onChangeStatus={(status) => updatePost(post.id, { status })}
          onDuplicate={() => duplicatePost(post.id)}
          onArchive={() => archivePost(post.id)}
          onDelete={() => requestDeletePost(post.id, post.topic)}
        />
      </div>
      <div className="post-card__topic">{post.topic || 'Без темы'}</div>
      <div className="post-card__meta">
        <span className="post-card__platform"><PlatformIcon platform={post.platform} /> {post.platform}</span>
        <span className="post-card__sep">·</span>
        <span className="post-card__format">{post.format}</span>
      </div>
      {project && <div className="post-card__project" style={{ color: project.color }}>{project.name}</div>}
      {overdue && <div className="post-card__overdue">Просрочено</div>}
    </div>
  );
}
