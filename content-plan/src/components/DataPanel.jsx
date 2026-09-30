import { useRef } from 'react';
import { useApp } from '../AppContext.jsx';
import { SCHEMA_VERSION } from '../storage.js';

export default function DataPanel() {
  const { dataPanelOpen, setDataPanelOpen, projects, posts, importData, setConfirmDialog, pushToast, mode, dataSource } = useApp();
  const fileInputRef = useRef(null);

  if (!dataPanelOpen) return null;

  async function handleExport() {
    const data = { schemaVersion: SCHEMA_VERSION, exportedAt: new Date().toISOString(), projects, posts };
    const json = JSON.stringify(data, null, 2);
    const stamp = new Date().toISOString().slice(0, 10);
    const filename = `content-plan-${stamp}.json`;

    // На странице, открытой как Artifact, обычная ссылка-скачивание не работает —
    // там файл предлагается через отдельный runtime-API.
    if (typeof window !== 'undefined' && window.claude && typeof window.claude.use === 'function') {
      try {
        const downloads = await window.claude.use('downloads');
        if (downloads) {
          await downloads.save({ filename, data: json });
          pushToast({ text: 'Файл сохранён.' });
          return;
        }
      } catch (err) {
        if (err?.code === 'declined') return;
        pushToast({ text: 'Не удалось сохранить файл. Попробуйте ещё раз.' });
        return;
      }
    }

    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function handleFileChosen(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      let parsed;
      try {
        parsed = JSON.parse(reader.result);
      } catch {
        pushToast({ text: 'Не удалось прочитать файл: он повреждён или это не JSON. Текущий план не изменён.' });
        return;
      }
      setConfirmDialog({
        title: 'Заменить текущие данные?',
        message: `Импорт заменит весь текущий контент-план на данные из файла «${file.name}». Это действие нельзя отменить. Рекомендуем сначала сделать экспорт текущих данных.`,
        confirmLabel: 'Заменить данные',
        onConfirm: async () => {
          const err = await importData(parsed);
          if (err) pushToast({ text: err });
          else pushToast({ text: 'Данные импортированы.' });
        },
      });
    };
    reader.onerror = () => {
      pushToast({ text: 'Не удалось прочитать файл. Текущий план не изменён.' });
    };
    reader.readAsText(file);
  }

  return (
    <div className="modal-overlay" onClick={() => setDataPanelOpen(false)}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2>Хранение данных</h2>
          <button type="button" className="modal__close" onClick={() => setDataPanelOpen(false)} aria-label="Закрыть">×</button>
        </div>
        <div className="modal__body">
          <p className="data-panel__notice">
            {dataSource === 'firebase' ? (
              <>
                Эта страница хранит данные централизованно (через Firebase): они одинаковы на всех устройствах
                и видны всем, у кого есть эта ссылка — без входа куда-либо. Всё равно делайте резервную копию
                через экспорт на случай технических неполадок.
              </>
            ) : mode === 'db' ? (
              <>
                Эта ссылка хранит данные централизованно: они одинаковы на всех ваших устройствах (телефон, компьютер)
                и видны всем, с кем вы поделились ссылкой. Открыть план могут только те, у кого есть доступ к ссылке
                (настраивается через «Share» на самой странице) — по умолчанию они видят план, но не могут его менять.
                Всё равно делайте резервную копию через экспорт на случай, если ссылка станет недоступна.
              </>
            ) : (
              <>
                Все данные сохраняются только в этом браузере на этом устройстве (в localStorage) и не синхронизируются
                между устройствами и браузерами. Очистка данных браузера или другой браузер/устройство — план будет пуст.
                Делайте резервную копию через экспорт, если план для вас важен.
              </>
            )}
          </p>
          <div className="data-panel__actions">
            <button type="button" className="btn-primary" onClick={handleExport}>Экспортировать данные (JSON)</button>
            <button type="button" className="btn-muted" onClick={() => fileInputRef.current?.click()}>Импортировать данные из JSON…</button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/json,.json"
              style={{ display: 'none' }}
              onChange={handleFileChosen}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
