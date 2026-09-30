import { initializeApp } from 'firebase/app';
import {
  getFirestore, collection, doc, setDoc, updateDoc, deleteDoc, getDocs, onSnapshot,
} from 'firebase/firestore';
import { firebaseConfig, isFirebaseConfigured } from './firebaseConfig.js';

// Тонкая обёртка над Firestore, повторяющая форму API Claude-артефактной базы
// (collection(path).doc(id).set/update/delete, collection(path).onSnapshot/get),
// чтобы остальной код приложения работал одинаково независимо от источника данных.
export function createFirestoreDb() {
  if (!isFirebaseConfigured()) return null;
  const app = initializeApp(firebaseConfig);
  const firestore = getFirestore(app);

  function wrapCollection(path) {
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
