import { useRef, useState } from 'react';

export default function QuickAddInput({ placeholder = 'Тема публикации…', alwaysOpen = false, onSubmit, buttonLabel = '+', buttonTitle = 'Добавить' }) {
  const [open, setOpen] = useState(alwaysOpen);
  const [value, setValue] = useState('');
  const inputRef = useRef(null);

  function submit() {
    const topic = value.trim();
    if (!topic) {
      if (!alwaysOpen) setOpen(false);
      return;
    }
    onSubmit(topic);
    setValue('');
    if (!alwaysOpen) {
      setOpen(false);
    } else {
      inputRef.current?.focus();
    }
  }

  if (!open) {
    return (
      <button type="button" className="quick-add__trigger" title={buttonTitle} onClick={() => setOpen(true)}>
        {buttonLabel}
      </button>
    );
  }

  return (
    <div className="quick-add">
      <input
        ref={inputRef}
        type="text"
        className="quick-add__input"
        placeholder={placeholder}
        value={value}
        autoFocus
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') submit();
          if (e.key === 'Escape') { setValue(''); if (!alwaysOpen) setOpen(false); }
        }}
        onBlur={() => { if (!alwaysOpen) submit(); }}
      />
      {alwaysOpen && (
        <button type="button" className="quick-add__submit" onClick={submit}>Добавить</button>
      )}
    </div>
  );
}
