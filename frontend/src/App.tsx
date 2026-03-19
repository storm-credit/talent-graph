import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./components/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { PeoplePage } from "./pages/PeoplePage";
import { OrgPage } from "./pages/OrgPage";
import { SimulationPage } from "./pages/SimulationPage";
import { ExplorerPage } from "./pages/ExplorerPage";
import { HowItWorksPage } from "./pages/HowItWorksPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { SetupPage } from "./pages/SetupPage";
import { GameModePage } from "./pages/GameModePage";
import { ProjectsPage } from "./pages/ProjectsPage";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/people" element={<PeoplePage />} />
            <Route path="/org" element={<OrgPage />} />
            <Route path="/simulation" element={<SimulationPage />} />
            <Route path="/game" element={<GameModePage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/setup" element={<SetupPage />} />
            <Route path="/explorer" element={<ExplorerPage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
