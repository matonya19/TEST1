import { useEffect, useRef, useState } from 'react';

export default function MultiSelectDropdown({ label, options, selected, onChange }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    function onDocClick(e) {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, [open]);

  function toggle(option) {
    if (selected.includes(option)) onChange(selected.filter((o) => o !== option));
    else onChange([...selected, option]);
  }

  const activeLabel = selected.length ? `${label} · ${selected.length}` : label;

  return (
    <div className="multiselect" ref={rootRef}>
      <button
        type="button"
        className={`multiselect__trigger ${selected.length ? 'multiselect__trigger--active' : ''}`}
        onClick={() => setOpen((o) => !o)}
      >
        {activeLabel}
        <span className="multiselect__caret">▾</span>
      </button>
      {open && (
        <div className="multiselect__panel" role="menu">
          {options.map((option) => (
            <label key={option} className="multiselect__option">
              <input
                type="checkbox"
                checked={selected.includes(option)}
                onChange={() => toggle(option)}
              />
              {option}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
