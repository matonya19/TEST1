// Конфигурация Firebase-проекта (Firestore) — источник общих данных для версии,
// не зависящей от Claude (GitHub Pages). Вставьте сюда объект firebaseConfig
// из Firebase Console → Project settings → Your apps → Web app.
// Эти значения не секретные — безопасность настраивается правилами Firestore,
// а не ключом. Пока объект пуст/не заполнен — приложение просто не использует
// Firebase и работает в обычном локальном режиме (localStorage) или через
// Claude-артефакт, если он доступен.

export const firebaseConfig = {
  apiKey: 'AIzaSyAgsPkZ1SWrPv3Ev_an8PQgd_nRb2gZjbE',
  authDomain: 'smm-contentplan.firebaseapp.com',
  projectId: 'smm-contentplan',
  storageBucket: 'smm-contentplan.firebasestorage.app',
  messagingSenderId: '271073901529',
  appId: '1:271073901529:web:f65ba2639bdc2bb087f7c8',
};

export function isFirebaseConfigured() {
  return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId && firebaseConfig.appId);
}
