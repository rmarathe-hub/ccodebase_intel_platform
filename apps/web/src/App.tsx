import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { AskPage } from "./pages/AskPage";
import { DashboardPage } from "./pages/DashboardPage";
import { FilesPage } from "./pages/FilesPage";
import { FileViewPage } from "./pages/FileViewPage";
import { GraphPage } from "./pages/GraphPage";
import { JobsPage } from "./pages/JobsPage";
import { RepositoryOverviewPage } from "./pages/RepositoryOverviewPage";
import { SearchPage } from "./pages/SearchPage";
import { SymbolsPage } from "./pages/SymbolsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="repositories" element={<RepositoryOverviewPage />} />
          <Route path="repositories/:id" element={<RepositoryOverviewPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="ask" element={<AskPage />} />
          <Route path="symbols" element={<SymbolsPage />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="files" element={<FilesPage />} />
          <Route path="files/view" element={<FileViewPage />} />
          <Route path="jobs" element={<JobsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
