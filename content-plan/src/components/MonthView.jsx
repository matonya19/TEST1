import { useMemo, useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { formatMonthYear, getMonthGrid, isToday, toISODate } from '../utils/date.js';
import { matchesFilters } from '../utils/filters.js';
import { STATUS_STYLES } from '../constants.js';
import QuickAddInput from './QuickAddInput.jsx';

export default function MonthView({ posts, projectsById }) {
  const { monthAnchor, setMonthAnchor, activeProjectId, search, filters, addPost, setEditorTarget, pendingDeleteIds, updatePost } = useApp();
  const [dragOverDay, setDragOverDay] = useState(null);
  const weeks = useMemo(() => getMonthGrid(monthAnchor), [monthAnchor]);

  const byDay = useMemo(() => {
    const map = new Map();
    for (const post of posts) {
      if (post.isIdea || post.isArchived || pendingDeleteIds.has(post.id)) continue;
      if (!matchesFilters(post, { activeProjectId, search, filters })) continue;
      if (!post.date) continue;
      if (!map.has(post.date)) map.set(post.date, []);
      map.get(post.date).push(post);
    }
    for (const arr of map.values()) arr.sort((a, b) => (a.time || '99:99').localeCompare(b.time || '99:99'));
    return map;
  }, [posts, activeProjectId, search, filters, pendingDeleteIds]);

  function shiftMonth(n) {
    setMonthAnchor((d) => new Date(d.getFullYear(), d.getMonth() + n, 1));
  }

  function handleDrop(e, dateStr) {
    e.preventDefault();
    setDragOverDay(null);
    const id = e.dataTransfer.getData('text/post-id');
    if (id) {
      const post = posts.find((p) => p.id === id);
      if (post && post.date !== dateStr) updatePost(id, { date: dateStr });
    }
  }

  return (
    <div className="month-view">
      <div className="period-nav">
        <button type="button" className="period-nav__btn" onClick={() => shiftMonth(-1)} aria-label="Предыдущий месяц">‹</button>
        <button type="button" className="period-nav__today" onClick={() => setMonthAnchor(new Date())}>Сегодня</button>
        <button type="button" className="period-nav__btn" onClick={() => shiftMonth(1)} aria-label="Следующий месяц">›</button>
        <span className="period-nav__label">{formatMonthYear(monthAnchor)}</span>
      </div>
      <div className="month-grid">
        {weeks.flat().map((day) => {
          const dateStr = toISODate(day);
          const inMonth = day.getMonth() === monthAnchor.getMonth();
          const today = isToday(day);
          const dayPosts = byDay.get(dateStr) || [];
          return (
            <div
              key={dateStr}
              className={`month-day ${!inMonth ? 'month-day--outside' : ''} ${today ? 'month-day--today' : ''} ${dragOverDay === dateStr ? 'month-day--drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOverDay(dateStr); }}
              onDragLeave={() => setDragOverDay((d) => (d === dateStr ? null : d))}
              onDrop={(e) => handleDrop(e, dateStr)}
            >
              <div className="month-day__num">{day.getDate()}</div>
              <div className="month-day__items">
                {dayPosts.slice(0, 4).map((post) => {
                  const style = STATUS_STYLES[post.status] || STATUS_STYLES['Идея'];
                  return (
                    <button
                      type="button"
                      key={post.id}
                      className="month-item"
                      draggable
                      onDragStart={(e) => { e.dataTransfer.setData('text/post-id', post.id); }}
                      onClick={() => setEditorTarget({ mode: 'edit', id: post.id })}
                      style={{ borderLeftColor: projectsById.get(post.projectId)?.color || style.dot }}
                      title={post.topic}
                    >
                      <span className="month-item__dot" style={{ background: style.dot }} />
                      {post.time && <span className="month-item__time">{post.time}</span>}
                      <span className="month-item__topic">{post.topic || 'Без темы'}</span>
                    </button>
                  );
                })}
                {dayPosts.length > 4 && (
                  <div className="month-item__more">ещё {dayPosts.length - 4}</div>
                )}
              </div>
              <QuickAddInput
                buttonTitle="Добавить публикацию"
                onSubmit={(topic) => {
                  const created = addPost({ topic, date: dateStr, projectId: activeProjectId !== 'all' ? activeProjectId : null });
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
