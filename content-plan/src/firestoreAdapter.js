import { initializeApp } from 'firebase/app';
import {
  initializeFirestore, collection, doc, setDoc, updateDoc, deleteDoc, getDocs, onSnapshot,
} from 'firebase/firestore';
import { firebaseConfig, isFirebaseConfigured } from './firebaseConfig.js';
import {
  getWorkspaceId, isCombinedWorkspace, SOURCE_WORKSPACES, makeMergedId, splitMergedId,
} from './workspace.js';

// Тонкая обёртка над Firestore, повторяющая форму API Claude-артефактной базы
// (collection(path).doc(id).set/update/delete, collection(path).onSnapshot/get),
// чтобы остальной код приложения работал одинаково независимо от источника данных.
// Коллекции живут под workspaces/<id>/..., так что несколько клиентских планов
// могут делить один Firebase-проект, не смешивая данные.
function createSingleWorkspaceDb(firestore) {
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

// Сводная версия: читает и пишет сразу в несколько реальных рабочих
// пространств (SOURCE_WORKSPACES), подсвечивая каждый источник своим цветом.
// Идентификаторы документов снаружи выглядят как "workspaceId::originalId",
// чтобы вызывающий код (AppContext) мог однозначно определить, откуда
// документ и куда направить запись, не зная о нескольких пространствах.
function createCombinedFirestoreDb(firestore) {
  function wrapDoc(ws, rawId, data, collectionName) {
    const fields = { ...data };
    if (collectionName === 'projects') {
      fields.color = ws.color; // цвет всегда по источнику, а не по самому проекту
    }
    if (collectionName === 'posts' && fields.projectId) {
      fields.projectId = makeMergedId(ws.id, fields.projectId);
    }
    return { id: makeMergedId(ws.id, rawId), data: () => fields };
  }

  function wrapCombinedCollection(name) {
    const perWorkspaceDocs = new Map(SOURCE_WORKSPACES.map((w) => [w.id, []]));
    const listeners = new Set();
    let started = false;

    function emit() {
      const merged = SOURCE_WORKSPACES.flatMap((ws) => perWorkspaceDocs.get(ws.id));
      listeners.forEach((fn) => fn({ docs: merged }));
    }

    function start() {
      if (started) return;
      started = true;
      SOURCE_WORKSPACES.forEach((ws) => {
        const path = `workspaces/${ws.id}/${name}`;
        onSnapshot(
          collection(firestore, path),
          (snap) => {
            perWorkspaceDocs.set(ws.id, snap.docs.map((d) => wrapDoc(ws, d.id, d.data(), name)));
            emit();
          },
          () => {},
        );
      });
    }

    return {
      doc(mergedId) {
        const { workspaceId, originalId } = splitMergedId(mergedId);
        return {
          set: (data) => {
            // Новый документ: id ещё без префикса (создан через makeId()).
            // Пространство берём из data.projectId — он уже merged-id, потому
            // что при создании публикации на сводной странице проект выбирается
            // из объединённого списка.
            const payload = { ...data };
            let targetWs = workspaceId;
            if (!targetWs) {
              const pid = splitMergedId(payload.projectId || '');
              if (!pid.workspaceId) {
                return Promise.reject(new Error('Выберите конкретный проект — иначе непонятно, в какую базу сохранить запись.'));
              }
              targetWs = pid.workspaceId;
            }
            if (payload.projectId) {
              payload.projectId = splitMergedId(payload.projectId).originalId;
            }
            const plainId = originalId || data.id;
            return setDoc(doc(firestore, `workspaces/${targetWs}/${name}`, plainId), payload);
          },
          update: (patch) => {
            if (!workspaceId) return Promise.reject(new Error('Запись не найдена.'));
            const payload = { ...patch };
            if (payload.projectId) {
              const pid = splitMergedId(payload.projectId);
              if (pid.workspaceId && pid.workspaceId !== workspaceId) {
                return Promise.reject(new Error('Нельзя перенести публикацию к другому клиенту со сводной страницы — создайте её заново на нужной страничке.'));
              }
              payload.projectId = pid.originalId;
            }
            return updateDoc(doc(firestore, `workspaces/${workspaceId}/${name}`, originalId), payload);
          },
          delete: () => {
            if (!workspaceId) return Promise.resolve();
            return deleteDoc(doc(firestore, `workspaces/${workspaceId}/${name}`, originalId));
          },
        };
      },
      get: async () => {
        const results = await Promise.all(SOURCE_WORKSPACES.map(async (ws) => {
          const snap = await getDocs(collection(firestore, `workspaces/${ws.id}/${name}`));
          return snap.docs.map((d) => wrapDoc(ws, d.id, d.data(), name));
        }));
        return { docs: results.flat() };
      },
      onSnapshot(next, onError) {
        start();
        listeners.add(next);
        emit();
        return () => listeners.delete(next);
      },
    };
  }

  return { collection: wrapCombinedCollection };
}

export function createFirestoreDb() {
  // Firebase включается только для сборок с явно заданным VITE_WORKSPACE_ID
  // (страницы GitHub Pages). Обычная локальная сборка и версии для Claude
  // Artifact не задают его и всегда остаются на своём обычном хранилище —
  // иначе все сборки с одними и теми же ключами слились бы в одно пространство.
  if (!isFirebaseConfigured() || !import.meta.env.VITE_WORKSPACE_ID) return null;
  const app = initializeApp(firebaseConfig);
  // Автоопределение long polling вместо потокового WebChannel — устойчивее за
  // строгими прокси/файрволами, но не форсирует его без необходимости.
  const firestore = initializeFirestore(app, { experimentalAutoDetectLongPolling: true });

  return isCombinedWorkspace() ? createCombinedFirestoreDb(firestore) : createSingleWorkspaceDb(firestore);
}
