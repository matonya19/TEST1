import { useMemo } from 'react';
import { useApp } from '../AppContext.jsx';
import { PLATFORMS, FORMATS, STATUSES } from '../constants.js';
import { matchesFilters } from '../utils/filters.js';
import { getWeekDays, startOfWeek, toISODate } from '../utils/date.js';
import MultiSelectDropdown from './MultiSelectDropdown.jsx';

export default function FiltersBar({ posts }) {
  const { filters, setFilters, resetFilters, activeProjectId, search, weekAnchor, pendingDeleteIds } = useApp();

  const hasActiveFilters = filters.platforms.length || filters.formats.length || filters.statuses.length
    || activeProjectId !== 'all' || (search && search.trim());

  const stats = useMemo(() => {
    const weekStart = startOfWeek(weekAnchor);
    const weekDates = new Set(getWeekDays(weekStart).map(toISODate));
    let planned = 0;
    let needsPrep = 0;
    let published = 0;
    for (const post of posts) {
      if (post.isIdea || post.isArchived || pendingDeleteIds.has(post.id)) continue;
      if (!post.date || !weekDates.has(post.date)) continue;
      if (!matchesFilters(post, { activeProjectId, search, filters })) continue;
      planned += 1;
      if (post.status === 'Опубликовано') published += 1;
      else if (post.status !== 'Готово') needsPrep += 1;
    }
    return { planned, needsPrep, published };
  }, [posts, weekAnchor, activeProjectId, search, filters, pendingDeleteIds]);

  return (
    <div className="filters-bar">
      <div className="filters-bar__filters">
        <MultiSelectDropdown label="Площадка" options={PLATFORMS} selected={filters.platforms} onChange={(v) => setFilters((f) => ({ ...f, platforms: v }))} />
        <MultiSelectDropdown label="Формат" options={FORMATS} selected={filters.formats} onChange={(v) => setFilters((f) => ({ ...f, formats: v }))} />
        <MultiSelectDropdown label="Статус" options={STATUSES} selected={filters.statuses} onChange={(v) => setFilters((f) => ({ ...f, statuses: v }))} />
        {hasActiveFilters && (
          <button type="button" className="filters-bar__reset" onClick={resetFilters}>Сбросить фильтры</button>
        )}
      </div>
      <div className="filters-bar__stats">
        <span className="stat-chip"><strong>{stats.planned}</strong> запланировано на неделю</span>
        <span className="stat-chip"><strong>{stats.needsPrep}</strong> требует подготовки</span>
        <span className="stat-chip stat-chip--done"><strong>{stats.published}</strong> опубликовано</span>
      </div>
    </div>
  );
}
