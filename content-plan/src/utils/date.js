import { WEEKDAY_SHORT, MONTH_NAMES, MONTH_NAMES_GENITIVE } from '../constants.js';

export function toISODate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function parseISODate(str) {
  if (!str) return null;
  const [y, m, d] = str.split('-').map(Number);
  return new Date(y, m - 1, d);
}

export function todayISO() {
  return toISODate(new Date());
}

export function addDays(date, n) {
  const d = new Date(date);
  d.setDate(d.getDate() + n);
  return d;
}

export function startOfWeek(date) {
  const d = new Date(date);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

export function isToday(date) {
  return isSameDay(date, new Date());
}

export function isPastDay(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  const t = new Date();
  t.setHours(0, 0, 0, 0);
  return d.getTime() < t.getTime();
}

export function formatDayMonth(date) {
  return `${date.getDate()} ${MONTH_NAMES_GENITIVE[date.getMonth()].slice(0, 3)}`;
}

export function formatWeekRange(weekStart) {
  const end = addDays(weekStart, 6);
  const sameMonth = weekStart.getMonth() === end.getMonth();
  if (sameMonth) {
    return `${weekStart.getDate()}–${end.getDate()} ${MONTH_NAMES_GENITIVE[end.getMonth()]}`;
  }
  return `${weekStart.getDate()} ${MONTH_NAMES_GENITIVE[weekStart.getMonth()]} – ${end.getDate()} ${MONTH_NAMES_GENITIVE[end.getMonth()]}`;
}

export function formatMonthYear(date) {
  return `${MONTH_NAMES[date.getMonth()]} ${date.getFullYear()}`;
}

export function getWeekDays(weekStart) {
  return Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
}

export function weekdayLabel(date) {
  const day = date.getDay();
  const idx = day === 0 ? 6 : day - 1;
  return WEEKDAY_SHORT[idx];
}

export function getMonthGrid(monthDate) {
  const first = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
  const last = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0);
  const gridStart = startOfWeek(first);
  const gridEnd = startOfWeek(last);
  const weeks = [];
  let cursor = gridStart;
  while (cursor.getTime() <= gridEnd.getTime()) {
    weeks.push(getWeekDays(cursor));
    cursor = addDays(cursor, 7);
  }
  return weeks;
}

export function formatTime(time) {
  return time || '';
}
