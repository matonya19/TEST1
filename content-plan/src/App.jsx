import { useMemo } from 'react';
import { AppProvider, useApp } from './AppContext.jsx';
import Sidebar from './components/Sidebar.jsx';
import TopBar from './components/TopBar.jsx';
import FiltersBar from './components/FiltersBar.jsx';
import NoDateShelf from './components/NoDateShelf.jsx';
import WeekView from './components/WeekView.jsx';
import MonthView from './components/MonthView.jsx';
import StatusBoardView from './components/StatusBoardView.jsx';
import DailyFeedView from './components/DailyFeedView.jsx';
import IdeasView from './components/IdeasView.jsx';
import ArchiveView from './components/ArchiveView.jsx';
import PostEditorDrawer from './components/PostEditorDrawer.jsx';
import ProjectManagerModal from './components/ProjectManagerModal.jsx';
import DataPanel from './components/DataPanel.jsx';
import ConfirmDialog from './components/ConfirmDialog.jsx';
import Toasts from './components/Toasts.jsx';

function AppShell() {
  const { projects, posts, section, view, dataReady, isCombined } = useApp();
  const projectsById = useMemo(() => new Map(projects.map((p) => [p.id, p])), [projects]);

  if (!dataReady) {
    return <div className="app-loading">Загрузка контент-плана…</div>;
  }

  return (
    <div className={`app-shell ${isCombined ? 'app-shell--combined' : ''}`}>
      <Sidebar />
      <div className="app-main">
        <TopBar />
        {section === 'plan' && !isCombined && <FiltersBar posts={posts} />}
        <div className="app-content">
          {section === 'plan' && (
            <>
              {isCombined && <DailyFeedView posts={posts} projectsById={projectsById} />}
              {!isCombined && view !== 'status' && <NoDateShelf posts={posts} projectsById={projectsById} />}
              {!isCombined && view === 'week' && <WeekView posts={posts} projectsById={projectsById} />}
              {!isCombined && view === 'month' && <MonthView posts={posts} projectsById={projectsById} />}
              {!isCombined && view === 'status' && <StatusBoardView posts={posts} projectsById={projectsById} />}
            </>
          )}
          {section === 'ideas' && <IdeasView posts={posts} projectsById={projectsById} />}
          {section === 'archive' && <ArchiveView posts={posts} projectsById={projectsById} />}
        </div>
      </div>
      <PostEditorDrawer />
      <ProjectManagerModal />
      <DataPanel />
      <ConfirmDialog />
      <Toasts />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppShell />
    </AppProvider>
  );
}
