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

    case 'DUPLICATE_POST': {
      const src = state.posts.find((p) => p.id === action.id);
      if (!src) return state;
      const now = Date.now();
      const clone = { ...src, id: makeId('post'), topic: `${src.topic} (копия)`, isDemo: false, createdAt: now, updatedAt: now };
      return { ...state, posts: [...state.posts, clone] };
    }

    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [domain, dispatch] = useReducer(domainReducer, undefined, () => {
    const loaded = loadState();
    if (loaded) return { schemaVersion: SCHEMA_VERSION, projects: loaded.projects, posts: loaded.posts };
    return defaultInitialState();
  });

  useEffect(() => {
    saveState(domain);
  }, [domain]);

  // --- UI-only state ---
  const [view, setView] = useState('week'); // 'week' | 'month' | 'status'
  const [section, setSection] = useState('plan'); // 'plan' | 'ideas' | 'archive'
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [weekAnchor, setWeekAnchor] = useState(() => new Date());
  const [monthAnchor, setMonthAnchor] = useState(() => new Date());
  const [activeProjectId, setActiveProjectId] = useState('all');
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({ platforms: [], formats: [], statuses: [] });
  const [editorTarget, setEditorTarget] = useState(null); // { mode: 'edit'|'create', id?, initial? }
  const [toasts, setToasts] = useState([]);
  const pendingDeletesRef = useRef(new Map());
  const [pendingDeleteIds, setPendingDeleteIds] = useState(() => new Set());
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [projectManagerOpen, setProjectManagerOpen] = useState(false);
  const [dataPanelOpen, setDataPanelOpen] = useState(false);

  const addPost = useCallback((overrides) => {
    const post = emptyPost(overrides);
    dispatch({ type: 'ADD_POST', post });
    return post;
  }, []);

  const updatePost = useCallback((id, patch) => {
    dispatch({ type: 'UPDATE_POST', id, patch });
  }, []);

  const duplicatePost = useCallback((id) => {
    dispatch({ type: 'DUPLICATE_POST', id });
  }, []);

  const pushToast = useCallback((toast) => {
    const id = makeId('toast');
    setToasts((t) => [...t, { id, ...toast }]);
    return id;
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const requestDeletePost = useCallback((id, label) => {
    setPendingDeleteIds((s) => new Set(s).add(id));
    const timeoutId = setTimeout(() => {
      dispatch({ type: 'DELETE_POST', id });
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
  }, [pushToast, dismissToast]);

  const archivePost = useCallback((id) => {
    dispatch({ type: 'UPDATE_POST', id, patch: { isArchived: true } });
  }, []);

  const unarchivePost = useCallback((id) => {
    dispatch({ type: 'UPDATE_POST', id, patch: { isArchived: false } });
  }, []);

  const createAdaptation = useCallback((sourceId, platform) => {
    const src = domain.posts.find((p) => p.id === sourceId);
    if (!src) return null;
    const groupId = src.linkedGroupId || makeId('group');
    if (!src.linkedGroupId) {
      dispatch({ type: 'UPDATE_POST', id: src.id, patch: { linkedGroupId: groupId } });
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
    dispatch({ type: 'ADD_POST', post: adaptation });
    return adaptation;
  }, [domain.posts]);

  const addProject = useCallback((name, color) => {
    const project = { id: makeId('project'), name, color, isDemo: false };
    dispatch({ type: 'ADD_PROJECT', project });
    return project;
  }, []);

  const updateProject = useCallback((id, patch) => {
    dispatch({ type: 'UPDATE_PROJECT', id, patch });
  }, []);

  const clearDemoData = useCallback(() => {
    dispatch({ type: 'CLEAR_DEMO' });
    if (activeProjectId === DEMO_PROJECT_ID) setActiveProjectId('all');
  }, [activeProjectId]);

  const importData = useCallback((data) => {
    const err = validateImportedData(data);
    if (err) return err;
    dispatch({ type: 'REPLACE_ALL', projects: data.projects, posts: data.posts });
    return null;
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({ platforms: [], formats: [], statuses: [] });
    setActiveProjectId('all');
    setSearch('');
  }, []);

  const value = useMemo(() => ({
    projects: domain.projects,
    posts: domain.posts,
    dispatch,
    addPost,
    updatePost,
    duplicatePost,
    requestDeletePost,
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
    domain, addPost, updatePost, duplicatePost, requestDeletePost, pendingDeleteIds,
    archivePost, unarchivePost, createAdaptation, addProject, updateProject, clearDemoData,
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
