import { useMemo, useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { addDays, formatDayMonth, formatWeekRange, getWeekDays, isToday, startOfWeek, toISODate, weekdayLabel } from '../utils/date.js';
import PostCard from './PostCard.jsx';
import QuickAddInput from './QuickAddInput.jsx';
import { matchesFilters } from '../utils/filters.js';

export default function WeekView({ posts, projectsById }) {
  const { weekAnchor, setWeekAnchor, activeProjectId, search, filters, addPost, setEditorTarget, pendingDeleteIds, updatePost } = useApp();
  const [dragOverDay, setDragOverDay] = useState(null);
  const weekStart = startOfWeek(weekAnchor);
  const days = useMemo(() => getWeekDays(weekStart), [weekStart]);

  const byDay = useMemo(() => {
    const map = new Map();
    for (const d of days) map.set(toISODate(d), []);
    for (const post of posts) {
      if (post.isIdea || post.isArchived || pendingDeleteIds.has(post.id)) continue;
      if (!matchesFilters(post, { activeProjectId, search, filters })) continue;
      if (post.date && map.has(post.date)) map.get(post.date).push(post);
    }
    for (const arr of map.values()) arr.sort((a, b) => (a.time || '99:99').localeCompare(b.time || '99:99'));
    return map;
  }, [posts, days, activeProjectId, search, filters, pendingDeleteIds]);

  function handleDrop(e, dateStr) {
    e.preventDefault();
    setDragOverDay(null);
    const id = e.dataTransfer.getData('text/post-id');
    if (id) {
      const post = posts.find((p) => p.id === id);
      if (post && post.date !== dateStr) {
        updatePost(id, { date: dateStr });
      }
    }
  }

  return (
    <div className="week-view">
      <div className="period-nav">
        <button type="button" className="period-nav__btn" onClick={() => setWeekAnchor((d) => addDays(d, -7))} aria-label="Предыдущая неделя">‹</button>
        <button type="button" className="period-nav__today" onClick={() => setWeekAnchor(new Date())}>Сегодня</button>
        <button type="button" className="period-nav__btn" onClick={() => setWeekAnchor((d) => addDays(d, 7))} aria-label="Следующая неделя">›</button>
        <span className="period-nav__label">{formatWeekRange(weekStart)}</span>
      </div>
      <div className="week-grid">
        {days.map((day) => {
          const dateStr = toISODate(day);
          const today = isToday(day);
          const dayPosts = byDay.get(dateStr) || [];
          return (
            <div
              key={dateStr}
              className={`week-day ${today ? 'week-day--today' : ''} ${dragOverDay === dateStr ? 'week-day--drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOverDay(dateStr); }}
              onDragLeave={() => setDragOverDay((d) => (d === dateStr ? null : d))}
              onDrop={(e) => handleDrop(e, dateStr)}
            >
              <div className="week-day__header">
                <span className="week-day__weekday">{weekdayLabel(day)}</span>
                <span className="week-day__date">{formatDayMonth(day)}</span>
              </div>
              <div className="week-day__cards">
                {dayPosts.map((post) => (
                  <PostCard
                    key={post.id}
                    post={post}
                    project={projectsById.get(post.projectId)}
                    onOpen={() => setEditorTarget({ mode: 'edit', id: post.id })}
                  />
                ))}
              </div>
              <QuickAddInput
                buttonTitle="Добавить публикацию в этот день"
                onSubmit={(topic) => {
                  const created = addPost({
                    topic,
                    date: dateStr,
                    projectId: activeProjectId !== 'all' ? activeProjectId : null,
                  });
                  setEditorTarget({ mode: 'edit', id: created.id });
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
