import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, useRef, useState } from 'react';
import { loadState, saveState, SCHEMA_VERSION, validateImportedData } from './storage.js';
import { buildDemoData, DEMO_PROJECT_ID } from './demoData.js';
import { todayISO } from './utils/date.js';

const AppCtx = createContext(null);

function makeId(prefix) {
  const rnd = (typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return prefix ? `${prefix}-${rnd}` : rnd;
}

function emptyPost(overrides = {}) {
  const now = Date.now();
  return {
    id: makeId('post'),
    projectId: null,
    topic: '',
    date: null,
    time: '',
    platform: 'Instagram',
    format: 'Пост',
    status: 'Идея',
    text: '',
    materialsLink: '',
    notes: '',
    rubric: '',
    goal: '',
    audience: '',
    cta: '',
    script: '',
    coverText: '',
    checklist: [],
    linkedGroupId: null,
    isIdea: false,
    isArchived: false,
    isDemo: false,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

function defaultInitialState() {
  const { project, posts } = buildDemoData();
  return { schemaVersion: SCHEMA_VERSION, projects: [project], posts };
}

function domainReducer(state, action) {
  switch (action.type) {
    case 'REPLACE_ALL':
      return { schemaVersion: SCHEMA_VERSION, projects: action.projects, posts: action.posts };

    case 'ADD_PROJECT':
      return { ...state, projects: [...state.projects, action.project] };

    case 'UPDATE_PROJECT':
      return {
        ...state,
        projects: state.projects.map((p) => (p.id === action.id ? { ...p, ...action.patch } : p)),
      };

    case 'CLEAR_DEMO':
      return {
        ...state,
        projects: state.projects.filter((p) => !p.isDemo),
        posts: state.posts.filter((p) => !p.isDemo),
      };

    case 'ADD_POST':
      return { ...state, posts: [...state.posts, action.post] };

    case 'UPDATE_POST':
      return {
        ...state,
        posts: state.posts.map((p) => (p.id === action.id ? { ...p, ...action.patch, updatedAt: Date.now() } : p)),
      };

    case 'DELETE_POST':
      return { ...state, posts: state.posts.filter((p) => p.id !== action.id) };

    default:
      return state;
  }
}

// Обёртка над Artifact-возможностью `db`: при её доступности данные общие
// (несколько устройств, ссылка для просмотра); иначе всё работает как раньше — только в localStorage.
function useSharedDb() {
  const [ready, setReady] = useState(false);
  const [available, setAvailable] = useState(false);
  const [projects, setProjects] = useState([]);
  const [posts, setPosts] = useState([]);
  const dbRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    let unsubProjects = () => {};
    let unsubPosts = () => {};

    (async () => {
      if (typeof window === 'undefined' || typeof window.claude?.use !== 'function') {
        setReady(true);
        return;
      }
      let db = null;
      try {
        db = await window.claude.use('db');
      } catch {
        db = null;
      }
      if (cancelled) return;
      if (!db) {
        setReady(true);
        return;
      }
      dbRef.current = db;
      setAvailable(true);
      unsubProjects = db.collection('projects').onSnapshot(
        (snap) => {
          setProjects(snap.docs.map((d) => ({ id: d.id, ...d.data() })));
          setReady(true);
        },
        () => setReady(true),
      );
      unsubPosts = db.collection('posts').onSnapshot(
        (snap) => setPosts(snap.docs.map((d) => ({ id: d.id, ...d.data() }))),
        () => {},
      );
    })();

    return () => {
      cancelled = true;
      unsubProjects();
      unsubPosts();
    };
  }, []);

  return { ready, available, projects, posts, db: dbRef };
}

export function AppProvider({ children }) {
  const shared = useSharedDb();
  const mode = shared.available ? 'db' : 'local';

  const [domain, dispatch] = useReducer(domainReducer, undefined, () => {
    const loaded = loadState();
    if (loaded) return { schemaVersion: SCHEMA_VERSION, projects: loaded.projects, posts: loaded.posts };
    return defaultInitialState();
  });

  useEffect(() => {
    if (mode === 'local') saveState(domain);
  }, [domain, mode]);

  const projects = mode === 'db' ? shared.projects : domain.projects;
  const posts = mode === 'db' ? shared.posts : domain.posts;

  const [toasts, setToasts] = useState([]);

  const pushToast = useCallback((toast) => {
    const id = makeId('toast');
    setToasts((t) => [...t, { id, ...toast }]);
    return id;
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const reportWriteError = useCallback((text) => {
    pushToast({ text });
  }, [pushToast]);

  const writeNewPost = useCallback((post) => {
    if (mode === 'db' && shared.db.current) {
      shared.db.current.collection('posts').doc(post.id).set(post).catch(() => {
        reportWriteError('Не удалось сохранить публикацию. Проверьте соединение или доступ на редактирование.');
      });
    } else {
      dispatch({ type: 'ADD_POST', post });
    }
  }, [mode, shared.db, reportWriteError]);

  const writePostPatch = useCallback((id, patch) => {
    if (mode === 'db' && shared.db.current) {
      shared.db.current.collection('posts').doc(id).update({ ...patch, updatedAt: Date.now() }).catch(() => {
        reportWriteError('Изменения не сохранились. Проверьте соединение или доступ на редактирование.');
      });
    } else {
      dispatch({ type: 'UPDATE_POST', id, patch });
    }
  }, [mode, shared.db, reportWriteError]);

  const writeDeletePost = useCallback((id) => {
    if (mode === 'db' && shared.db.current) {
      shared.db.current.collection('posts').doc(id).delete().catch(() => {
        reportWriteError('Не удалось удалить публикацию. Проверьте соединение или доступ на редактирование.');
      });
    } else {
      dispatch({ type: 'DELETE_POST', id });
    }
  }, [mode, shared.db, reportWriteError]);

  const writeNewProject = useCallback((project) => {
    if (mode === 'db' && shared.db.current) {
      shared.db.current.collection('projects').doc(project.id).set(project).catch(() => {
        reportWriteError('Не удалось создать проект. Проверьте соединение или доступ на редактирование.');
      });
    } else {
      dispatch({ type: 'ADD_PROJECT', project });
    }
  }, [mode, shared.db, reportWriteError]);

  const writeProjectPatch = useCallback((id, patch) => {
    if (mode === 'db' && shared.db.current) {
      shared.db.current.collection('projects').doc(id).update(patch).catch(() => {
        reportWriteError('Не удалось сохранить проект. Проверьте соединение или доступ на редактирование.');
      });
    } else {
      dispatch({ type: 'UPDATE_PROJECT', id, patch });
    }
  }, [mode, shared.db, reportWriteError]);

  // --- UI-only state (всегда локальное, не общее между устройствами) ---
  const [view, setView] = useState('week'); // 'week' | 'month' | 'status'
  const [section, setSection] = useState('plan'); // 'plan' | 'ideas' | 'archive'
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [weekAnchor, setWeekAnchor] = useState(() => new Date());
  const [monthAnchor, setMonthAnchor] = useState(() => new Date());
  const [activeProjectId, setActiveProjectId] = useState('all');
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({ platforms: [], formats: [], statuses: [] });
  const [editorTarget, setEditorTarget] = useState(null); // { mode: 'edit'|'create', id?, isNew? }
  const pendingDeletesRef = useRef(new Map());
  const [pendingDeleteIds, setPendingDeleteIds] = useState(() => new Set());
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [projectManagerOpen, setProjectManagerOpen] = useState(false);
  const [dataPanelOpen, setDataPanelOpen] = useState(false);

  const addPost = useCallback((overrides) => {
    const post = emptyPost(overrides);
    writeNewPost(post);
    return post;
  }, [writeNewPost]);

  const updatePost = useCallback((id, patch) => {
    writePostPatch(id, patch);
  }, [writePostPatch]);

  const duplicatePost = useCallback((id) => {
    const src = posts.find((p) => p.id === id);
    if (!src) return;
    const now = Date.now();
    const clone = { ...src, id: makeId('post'), topic: `${src.topic} (копия)`, isDemo: false, createdAt: now, updatedAt: now };
    writeNewPost(clone);
  }, [posts, writeNewPost]);

  const requestDeletePost = useCallback((id, label) => {
    setPendingDeleteIds((s) => new Set(s).add(id));
    const timeoutId = setTimeout(() => {
      writeDeletePost(id);
      pendingDeletesRef.current.delete(id);
      setPendingDeleteIds((s) => {
        const next = new Set(s);
        next.delete(id);
        return next;
      });
    }, 6000);
    pendingDeletesRef.current.set(id, timeoutId);
    const toastId = pushToast({
      kind: 'undo',
      text: `Публикация «${label || 'без темы'}» удалена`,
      onUndo: () => {
        clearTimeout(pendingDeletesRef.current.get(id));
        pendingDeletesRef.current.delete(id);
        setPendingDeleteIds((s) => {
          const next = new Set(s);
          next.delete(id);
          return next;
        });
        dismissToast(toastId);
      },
    });
    setTimeout(() => dismissToast(toastId), 6200);
  }, [pushToast, dismissToast, writeDeletePost]);

  const hardDeletePost = useCallback((id) => {
    writeDeletePost(id);
  }, [writeDeletePost]);

  const archivePost = useCallback((id) => {
    writePostPatch(id, { isArchived: true });
  }, [writePostPatch]);

  const unarchivePost = useCallback((id) => {
    writePostPatch(id, { isArchived: false });
  }, [writePostPatch]);

  const createAdaptation = useCallback((sourceId, platform) => {
    const src = posts.find((p) => p.id === sourceId);
    if (!src) return null;
    const groupId = src.linkedGroupId || makeId('group');
    if (!src.linkedGroupId) {
      writePostPatch(src.id, { linkedGroupId: groupId });
    }
    const adaptation = emptyPost({
      projectId: src.projectId,
      topic: src.topic,
      materialsLink: src.materialsLink,
      platform,
      linkedGroupId: groupId,
      isIdea: false,
      status: 'Идея',
    });
    writeNewPost(adaptation);
    return adaptation;
  }, [posts, writePostPatch, writeNewPost]);

  const addProject = useCallback((name, color) => {
    const project = { id: makeId('project'), name, color, isDemo: false };
    writeNewProject(project);
    return project;
  }, [writeNewProject]);

  const updateProject = useCallback((id, patch) => {
    writeProjectPatch(id, patch);
  }, [writeProjectPatch]);

  const clearDemoData = useCallback(() => {
    if (mode === 'db' && shared.db.current) {
      const db = shared.db.current;
      projects.filter((p) => p.isDemo).forEach((p) => db.collection('projects').doc(p.id).delete().catch(() => {}));
      posts.filter((p) => p.isDemo).forEach((p) => db.collection('posts').doc(p.id).delete().catch(() => {}));
    } else {
      dispatch({ type: 'CLEAR_DEMO' });
    }
    if (activeProjectId === DEMO_PROJECT_ID) setActiveProjectId('all');
  }, [mode, shared.db, projects, posts, activeProjectId]);

  const importData = useCallback(async (data) => {
    const err = validateImportedData(data);
    if (err) return err;
    if (mode === 'db' && shared.db.current) {
      const db = shared.db.current;
      try {
        await Promise.all(projects.map((p) => db.collection('projects').doc(p.id).delete()));
        await Promise.all(posts.map((p) => db.collection('posts').doc(p.id).delete()));
        await Promise.all(data.projects.map((p) => db.collection('projects').doc(p.id).set(p)));
        await Promise.all(data.posts.map((p) => db.collection('posts').doc(p.id).set(p)));
      } catch {
        return 'Не удалось импортировать данные (нет соединения или доступа на редактирование).';
      }
    } else {
      dispatch({ type: 'REPLACE_ALL', projects: data.projects, posts: data.posts });
    }
    return null;
  }, [mode, shared.db, projects, posts]);

  const resetFilters = useCallback(() => {
    setFilters({ platforms: [], formats: [], statuses: [] });
    setActiveProjectId('all');
    setSearch('');
  }, []);

  const value = useMemo(() => ({
    projects,
    posts,
    mode,
    dataReady: shared.ready,
    addPost,
    updatePost,
    duplicatePost,
    requestDeletePost,
    hardDeletePost,
    pendingDeleteIds,
    archivePost,
    unarchivePost,
    createAdaptation,
    addProject,
    updateProject,
    clearDemoData,
    importData,
    view, setView,
    section, setSection,
    sidebarCollapsed, setSidebarCollapsed,
    weekAnchor, setWeekAnchor,
    monthAnchor, setMonthAnchor,
    activeProjectId, setActiveProjectId,
    search, setSearch,
    filters, setFilters,
    resetFilters,
    editorTarget, setEditorTarget,
    toasts, pushToast, dismissToast,
    confirmDialog, setConfirmDialog,
    projectManagerOpen, setProjectManagerOpen,
    dataPanelOpen, setDataPanelOpen,
    todayISO: todayISO(),
  }), [
    projects, posts, mode, shared.ready, addPost, updatePost, duplicatePost, requestDeletePost, hardDeletePost,
    pendingDeleteIds, archivePost, unarchivePost, createAdaptation, addProject, updateProject, clearDemoData,
    importData, view, section, sidebarCollapsed, weekAnchor, monthAnchor, activeProjectId,
    search, filters, resetFilters, editorTarget, toasts, pushToast, dismissToast,
    confirmDialog, projectManagerOpen, dataPanelOpen,
  ]);

  return <AppCtx.Provider value={value}>{children}</AppCtx.Provider>;
}

export function useApp() {
  const ctx = useContext(AppCtx);
  if (!ctx) throw new Error('useApp должен использоваться внутри AppProvider');
  return ctx;
}

export { emptyPost, makeId };
