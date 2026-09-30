import { initializeApp } from 'firebase/app';
import {
  initializeFirestore, collection, doc, setDoc, updateDoc, deleteDoc, getDocs, onSnapshot,
} from 'firebase/firestore';
import { firebaseConfig, isFirebaseConfigured } from './firebaseConfig.js';
import { getWorkspaceId } from './workspace.js';

// Тонкая обёртка над Firestore, повторяющая форму API Claude-артефактной базы
// (collection(path).doc(id).set/update/delete, collection(path).onSnapshot/get),
// чтобы остальной код приложения работал одинаково независимо от источника данных.
// Коллекции живут под workspaces/<id>/..., так что несколько клиентских планов
// могут делить один Firebase-проект, не смешивая данные.
export function createFirestoreDb() {
  if (!isFirebaseConfigured()) return null;
  const app = initializeApp(firebaseConfig);
  // Автоопределение long polling вместо потокового WebChannel — устойчивее за
  // строгими прокси/файрволами, но не форсирует его без необходимости.
  const firestore = initializeFirestore(app, { experimentalAutoDetectLongPolling: true });

  function wrapCollection(name) {
    const path = `workspaces/${getWorkspaceId()}/${name}`;
    const colRef = collection(firestore, path);
    return {
      doc(id) {
        const docRef = doc(firestore, path, id);
        return {
          set: (data) => setDoc(docRef, data),
          update: (data) => updateDoc(docRef, data),
          delete: () => deleteDoc(docRef),
        };
      },
      get: async () => {
        const snap = await getDocs(colRef);
        return { docs: snap.docs.map((d) => ({ id: d.id, data: () => d.data() })) };
      },
      onSnapshot(next, onError) {
        return onSnapshot(
          colRef,
          (snap) => next({ docs: snap.docs.map((d) => ({ id: d.id, data: () => d.data() })) }),
          onError,
        );
      },
    };
  }

  return { collection: wrapCollection };
}
