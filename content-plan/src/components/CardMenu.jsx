import { useEffect, useRef, useState } from 'react';
import { STATUSES } from '../constants.js';

export default function CardMenu({ post, onMoveDate, onChangeStatus, onDuplicate, onArchive, onDelete, onOpen }) {
  const [open, setOpen] = useState(false);
  const [sub, setSub] = useState(null); // 'date' | 'status' | null
  const rootRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    function onDocClick(e) {
      if (rootRef.current && !rootRef.current.contains(e.target)) {
        setOpen(false);
        setSub(null);
      }
    }
    function onEsc(e) {
      if (e.key === 'Escape') { setOpen(false); setSub(null); }
    }
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('keydown', onEsc);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('keydown', onEsc);
    };
  }, [open]);

  function close() {
    setOpen(false);
    setSub(null);
  }

  return (
    <div className="card-menu" ref={rootRef} onClick={(e) => e.stopPropagation()}>
      <button
        type="button"
        className="card-menu__trigger"
        aria-label="Действия с публикацией"
        onClick={() => { setOpen((o) => !o); setSub(null); }}
      >
        ⋮
      </button>
      {open && (
        <div className="card-menu__panel" role="menu">
          {sub === null && (
            <>
              <button type="button" className="card-menu__item" onClick={() => { onOpen(); close(); }}>Открыть</button>
              <button type="button" className="card-menu__item" onClick={() => setSub('date')}>Перенести на день…</button>
              <button type="button" className="card-menu__item" onClick={() => setSub('status')}>Сменить статус…</button>
              <button type="button" className="card-menu__item" onClick={() => { onDuplicate(); close(); }}>Дублировать</button>
              <button type="button" className="card-menu__item" onClick={() => { onArchive(); close(); }}>Архивировать</button>
              <button type="button" className="card-menu__item card-menu__item--danger" onClick={() => { onDelete(); close(); }}>Удалить</button>
            </>
          )}
          {sub === 'date' && (
            <div className="card-menu__sub">
              <label className="card-menu__label">Новая дата</label>
              <input
                type="date"
                defaultValue={post.date || ''}
                autoFocus
                onChange={(e) => { onMoveDate(e.target.value || null); close(); }}
                className="card-menu__date-input"
              />
              <button type="button" className="card-menu__item" onClick={() => { onMoveDate(null); close(); }}>Оставить без даты</button>
              <button type="button" className="card-menu__item card-menu__item--muted" onClick={() => setSub(null)}>← Назад</button>
            </div>
          )}
          {sub === 'status' && (
            <div className="card-menu__sub">
              {STATUSES.map((s) => (
                <button
                  key={s}
                  type="button"
                  className={`card-menu__item ${s === post.status ? 'card-menu__item--active' : ''}`}
                  onClick={() => { onChangeStatus(s); close(); }}
                >
                  {s}
                </button>
              ))}
              <button type="button" className="card-menu__item card-menu__item--muted" onClick={() => setSub(null)}>← Назад</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
