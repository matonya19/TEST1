import { useApp } from '../AppContext.jsx';

export default function ConfirmDialog() {
  const { confirmDialog, setConfirmDialog } = useApp();
  if (!confirmDialog) return null;

  function close() {
    setConfirmDialog(null);
  }

  return (
    <div className="modal-overlay" onClick={close}>
      <div className="modal modal--small" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2>{confirmDialog.title}</h2>
        </div>
        <div className="modal__body">
          <p>{confirmDialog.message}</p>
        </div>
        <div className="modal__footer">
          <button type="button" className="btn-muted" onClick={close}>Отмена</button>
          <button
            type="button"
            className="btn-danger"
            onClick={() => { confirmDialog.onConfirm(); close(); }}
          >
            {confirmDialog.confirmLabel || 'Подтвердить'}
          </button>
        </div>
      </div>
    </div>
  );
}
