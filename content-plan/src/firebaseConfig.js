// Конфигурация Firebase-проекта (Firestore) — источник общих данных для версии,
// не зависящей от Claude (GitHub Pages). Вставьте сюда объект firebaseConfig
// из Firebase Console → Project settings → Your apps → Web app.
// Эти значения не секретные — безопасность настраивается правилами Firestore,
// а не ключом. Пока объект пуст/не заполнен — приложение просто не использует
// Firebase и работает в обычном локальном режиме (localStorage) или через
// Claude-артефакт, если он доступен.

export const firebaseConfig = {
  apiKey: '',
  authDomain: '',
  projectId: '',
  storageBucket: '',
  messagingSenderId: '',
  appId: '',
};

export function isFirebaseConfigured() {
  return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId && firebaseConfig.appId);
}
