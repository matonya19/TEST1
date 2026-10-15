import { useMemo, useRef, useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { matchesFilters } from '../utils/filters.js';
import { addDays, isToday, toISODate } from '../utils/date.js';
import { WEEKDAY_SHORT_FULL, MONTH_NAMES_GENITIVE, STATUS_STYLES } from '../constants.js';
import { SOURCE_WORKSPACES, splitMergedId } from '../workspace.js';
import { hexToRgba } from '../utils/color.js';
import PlatformIcon from './PlatformIcon.jsx';

const SWIPE_THRESHOLD = 50;

function formatLongDate(date) {
  const weekday = WEEKDAY_SHORT_FULL[date.getDay() === 0 ? 6 : date.getDay() - 1];
  return `${weekday}, ${date.getDate()} ${MONTH_NAMES_GENITIVE[date.getMonth()]}`;
}

export default function DailyFeedView({ posts, projectsById }) {
  const {
    dayAnchor, setDayAnchor, activeProjectId, search, filters,
    setEditorTarget, pendingDeleteIds, updatePost,
  } = useApp();
  const touchStartX = useRef(null);
  const [dragX, setDragX] = useState(0);

  const dateStr = toISODate(dayAnchor);

  const dayPosts = useMemo(() => {
    return posts
      .filter((p) => !p.isIdea && !p.isArchived && !pendingDeleteIds.has(p.id))
      .filter((p) => p.date === dateStr)
      .filter((p) => matchesFilters(p, { activeProjectId, search, filters }))
      .sort((a, b) => (a.time || '99:99').localeCompare(b.time || '99:99'));
  }, [posts, dateStr, activeProjectId, search, filters, pendingDeleteIds]);

  function goTo(delta) {
    setDayAnchor((d) => addDays(d, delta));
    setDragX(0);
  }

  function handleTouchStart(e) {
    touchStartX.current = e.touches[0].clientX;
  }
  function handleTouchMove(e) {
    if (touchStartX.current == null) return;
    setDragX(e.touches[0].clientX - touchStartX.current);
  }
  function handleTouchEnd() {
    if (dragX > SWIPE_THRESHOLD) goTo(-1);
    else if (dragX < -SWIPE_THRESHOLD) goTo(1);
    else setDragX(0);
    touchStartX.current = null;
  }

  function sourceWorkspace(post) {
    const workspaceId = splitMergedId(post.id).workspaceId;
    return SOURCE_WORKSPACES.find((w) => w.id === workspaceId);
  }

  return (
    <div className="daily-feed">
      <div className="daily-feed__header">
        <button type="button" className="daily-feed__nav-btn" onClick={() => goTo(-1)} aria-label="Предыдущий день">‹</button>
        <div className="daily-feed__date-block">
          <span className="daily-feed__date">{formatLongDate(dayAnchor)}</span>
          {!isToday(dayAnchor) && (
            <button type="button" className="daily-feed__today-btn" onClick={() => setDayAnchor(new Date())}>Сегодня</button>
          )}
        </div>
        <button type="button" className="daily-feed__nav-btn" onClick={() => goTo(1)} aria-label="Следующий день">›</button>
      </div>

      <div
        className="daily-feed__swipe-area"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <div className="daily-feed__list" style={{ transform: dragX ? `translateX(${dragX}px)` : undefined }}>
          {dayPosts.length === 0 && (
            <div className="daily-feed__empty">На этот день пока ничего не запланировано</div>
          )}
          {dayPosts.map((post) => {
            const project = projectsById.get(post.projectId);
            const style = STATUS_STYLES[post.status] || STATUS_STYLES['Идея'];
            const ws = sourceWorkspace(post);
            const color = project?.color || ws?.color;
            return (
              <div
                key={post.id}
                className="daily-feed__card"
                onClick={() => setEditorTarget({ mode: 'edit', id: post.id })}
                style={{
                  borderLeftColor: color || 'var(--border)',
                  backgroundColor: color ? hexToRgba(color, 0.08) : undefined,
                }}
              >
                <div className="daily-feed__card-top">
                  {ws && (
                    <span className="daily-feed__client-badge" style={{ background: ws.color }}>{ws.label}</span>
                  )}
                  <span className="daily-feed__time">{post.time || '—:—'}</span>
                  <span className="post-card__status" style={{ background: style.bg, color: style.text }}>
                    <span className="post-card__dot" style={{ background: style.dot }} />
                    {post.status}
                  </span>
                </div>
                <div className="daily-feed__card-topic">{post.topic || 'Без темы'}</div>
                <div className="daily-feed__card-meta">
                  <span className="post-card__platform"><PlatformIcon platform={post.platform} /> {post.platform}</span>
                  <span className="post-card__sep">·</span>
                  <span className="post-card__format">{post.format}</span>
                </div>
                {post.status !== 'Опубликовано' && (
                  <button
                    type="button"
                    className="daily-feed__quick-done"
                    onClick={(e) => { e.stopPropagation(); updatePost(post.id, { status: 'Опубликовано' }); }}
                  >
                    Отметить опубликованным
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
