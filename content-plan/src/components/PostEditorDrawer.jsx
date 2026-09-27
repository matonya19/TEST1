import { useMemo, useState } from 'react';
import { useApp } from '../AppContext.jsx';
import { PLATFORMS, FORMATS, STATUSES } from '../constants.js';
import { makeId } from '../AppContext.jsx';

export default function PostEditorDrawer() {
  const {
    posts, projects, editorTarget, setEditorTarget, updatePost, dispatch,
    duplicatePost, archivePost, unarchivePost, requestDeletePost, createAdaptation, pushToast,
  } = useApp();
  const [adaptPlatform, setAdaptPlatform] = useState('');
  const [checklistInput, setChecklistInput] = useState('');

  const post = editorTarget ? posts.find((p) => p.id === editorTarget.id) : null;

  const linkedVersions = useMemo(() => {
    if (!post?.linkedGroupId) return [];
    return posts.filter((p) => p.linkedGroupId === post.linkedGroupId && p.id !== post.id);
  }, [posts, post]);

  if (!editorTarget || !post) return null;

  function close() {
    if (editorTarget.isNew && !post.topic.trim()) {
      dispatch({ type: 'DELETE_POST', id: post.id });
    }
    setEditorTarget(null);
  }

  function set(patch) {
    updatePost(post.id, patch);
  }

  function handleCopyText() {
    const text = post.text || '';
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(
        () => pushToast({ text: 'Текст скопирован в буфер обмена' }),
        () => pushToast({ text: 'Не удалось скопировать текст' }),
      );
    }
  }

  function handleDelete() {
    requestDeletePost(post.id, post.topic);
    setEditorTarget(null);
  }

  function handleCreateAdaptation() {
    if (!adaptPlatform) return;
    const adapted = createAdaptation(post.id, adaptPlatform);
    if (adapted) {
      setAdaptPlatform('');
      setEditorTarget({ mode: 'edit', id: adapted.id });
    }
  }

  function addChecklistItem() {
    const text = checklistInput.trim();
    if (!text) return;
    set({ checklist: [...post.checklist, { id: makeId('chk'), text, done: false }] });
    setChecklistInput('');
  }

  function toggleChecklistItem(id) {
    set({ checklist: post.checklist.map((c) => (c.id === id ? { ...c, done: !c.done } : c)) });
  }

  function removeChecklistItem(id) {
    set({ checklist: post.checklist.filter((c) => c.id !== id) });
  }

  return (
    <div className="drawer-overlay" onClick={close}>
      <aside className="drawer" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Редактирование публикации">
        <div className="drawer__header">
          <input
            type="text"
            className="drawer__topic-input"
            placeholder="Тема публикации"
            value={post.topic}
            onChange={(e) => set({ topic: e.target.value })}
            autoFocus={editorTarget.isNew}
          />
          <button type="button" className="drawer__close" onClick={close} aria-label="Закрыть панель">×</button>
        </div>

        {post.isArchived && <div className="drawer__archived-flag">Публикация в архиве</div>}

        <div className="drawer__body">
          <div className="drawer__grid">
            <label className="field">
              <span className="field__label">Проект</span>
              <select value={post.projectId || ''} onChange={(e) => set({ projectId: e.target.value || null })}>
                <option value="">Без проекта</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </label>

            <label className="field">
              <span className="field__label">Статус</span>
              <select value={post.status} onChange={(e) => set({ status: e.target.value })}>
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </label>

            <label className="field">
              <span className="field__label">Площадка</span>
              <select value={post.platform} onChange={(e) => set({ platform: e.target.value })}>
                {PLATFORMS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>

            <label className="field">
              <span className="field__label">Формат</span>
              <select value={post.format} onChange={(e) => set({ format: e.target.value })}>
                {FORMATS.map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </label>

            <label className="field">
              <span className="field__label">Дата</span>
              <input type="date" value={post.date || ''} onChange={(e) => set({ date: e.target.value || null })} />
            </label>

            <label className="field">
              <span className="field__label">Время</span>
              <input type="time" value={post.time || ''} onChange={(e) => set({ time: e.target.value })} disabled={!post.date} />
            </label>
          </div>
          {post.date && (
            <button type="button" className="link-btn" onClick={() => set({ date: null, time: '' })}>Оставить без даты</button>
          )}

          <label className="field field--block">
            <span className="field__label">Текст публикации</span>
            <textarea
              className="drawer__text"
              rows={8}
              placeholder="Текст публикации…"
              value={post.text}
              onChange={(e) => set({ text: e.target.value })}
            />
          </label>
          <button type="button" className="btn-muted btn-small" onClick={handleCopyText}>Скопировать текст</button>

          <label className="field field--block">
            <span className="field__label">Ссылка на материалы</span>
            <input
              type="text"
              placeholder="Ссылка на фото/видео/документ"
              value={post.materialsLink}
              onChange={(e) => set({ materialsLink: e.target.value })}
            />
          </label>

          <label className="field field--block">
            <span className="field__label">Заметки</span>
            <textarea
              rows={3}
              placeholder="Внутренние заметки"
              value={post.notes}
              onChange={(e) => set({ notes: e.target.value })}
            />
          </label>

          <details className="drawer__extra">
            <summary>Дополнительные поля</summary>
            <div className="drawer__extra-body">
              <label className="field field--block">
                <span className="field__label">Рубрика</span>
                <input type="text" value={post.rubric} onChange={(e) => set({ rubric: e.target.value })} />
              </label>
              <label className="field field--block">
                <span className="field__label">Цель публикации</span>
                <input type="text" value={post.goal} onChange={(e) => set({ goal: e.target.value })} />
              </label>
              <label className="field field--block">
                <span className="field__label">Аудитория</span>
                <input type="text" value={post.audience} onChange={(e) => set({ audience: e.target.value })} />
              </label>
              <label className="field field--block">
                <span className="field__label">CTA (призыв к действию)</span>
                <input type="text" value={post.cta} onChange={(e) => set({ cta: e.target.value })} />
              </label>
              <label className="field field--block">
                <span className="field__label">Сценарий</span>
                <textarea rows={4} value={post.script} onChange={(e) => set({ script: e.target.value })} />
              </label>
              <label className="field field--block">
                <span className="field__label">Текст на обложку</span>
                <input type="text" value={post.coverText} onChange={(e) => set({ coverText: e.target.value })} />
              </label>
              <div className="field field--block">
                <span className="field__label">Чек-лист подготовки</span>
                <ul className="checklist">
                  {post.checklist.map((item) => (
                    <li key={item.id} className="checklist__item">
                      <label>
                        <input type="checkbox" checked={item.done} onChange={() => toggleChecklistItem(item.id)} />
                        <span className={item.done ? 'checklist__text--done' : ''}>{item.text}</span>
                      </label>
                      <button type="button" className="checklist__remove" onClick={() => removeChecklistItem(item.id)} aria-label="Удалить пункт">×</button>
                    </li>
                  ))}
                </ul>
                <div className="checklist__add">
                  <input
                    type="text"
                    placeholder="Новый пункт чек-листа"
                    value={checklistInput}
                    onChange={(e) => setChecklistInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') addChecklistItem(); }}
                  />
                  <button type="button" onClick={addChecklistItem}>Добавить</button>
                </div>
              </div>
            </div>
          </details>

          <div className="drawer__versions">
            <h3>Версии для других площадок</h3>
            {linkedVersions.length > 0 && (
              <ul className="versions-list">
                {linkedVersions.map((v) => (
                  <li key={v.id}>
                    <button type="button" className="versions-list__chip" onClick={() => setEditorTarget({ mode: 'edit', id: v.id })}>
                      {v.platform} · {v.status}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="drawer__adapt-row">
              <select value={adaptPlatform} onChange={(e) => setAdaptPlatform(e.target.value)}>
                <option value="">Выбрать площадку…</option>
                {PLATFORMS.filter((p) => p !== post.platform).map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
              <button type="button" className="btn-muted btn-small" disabled={!adaptPlatform} onClick={handleCreateAdaptation}>
                Создать адаптацию
              </button>
            </div>
            <p className="drawer__hint">Тема и ссылка на материалы переносятся, текст, дата, формат и статус — независимые для каждой версии.</p>
          </div>
        </div>

        <div className="drawer__footer">
          <button type="button" className="btn-muted" onClick={() => duplicatePost(post.id)}>Дублировать</button>
          {post.isArchived ? (
            <button type="button" className="btn-muted" onClick={() => unarchivePost(post.id)}>Восстановить из архива</button>
          ) : (
            <button type="button" className="btn-muted" onClick={() => archivePost(post.id)}>Архивировать</button>
          )}
          <button type="button" className="btn-danger" onClick={handleDelete}>Удалить</button>
        </div>
      </aside>
    </div>
  );
}
