import { useApp } from '../AppContext.jsx';

export default function Toasts() {
  const { toasts, dismissToast } = useApp();
  if (!toasts.length) return null;
  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className="toast">
          <span>{t.text}</span>
          {t.kind === 'undo' && (
            <button type="button" className="toast__undo" onClick={t.onUndo}>Отменить</button>
          )}
          <button type="button" className="toast__close" onClick={() => dismissToast(t.id)} aria-label="Закрыть уведомление">×</button>
        </div>
      ))}
    </div>
  );
}
