import { Route, Routes } from 'react-router';
import { Shell } from './components/Shell';
import { CompareScreen } from './screens/CompareScreen';
import { EntryScreen } from './screens/EntryScreen';
import { MethodologyScreen } from './screens/MethodologyScreen';
import { ProjectScreen } from './screens/ProjectScreen';
import { ProjectsScreen } from './screens/ProjectsScreen';
import { ResultsScreen } from './screens/ResultsScreen';
import { WizardScreen } from './screens/WizardScreen';
import { messages } from './i18n/en';

/** Route table, mirroring the user journey (ARCHITECTURE §3). */
export function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<EntryScreen />} />
        <Route path="projects" element={<ProjectsScreen />} />
        <Route path="projects/:projectId" element={<ProjectScreen />} />
        <Route
          path="projects/:projectId/assessments/:assessmentId/edit"
          element={<WizardScreen />}
        />
        <Route
          path="projects/:projectId/assessments/:assessmentId/results"
          element={<ResultsScreen />}
        />
        <Route path="projects/:projectId/compare" element={<CompareScreen />} />
        <Route path="methodology" element={<MethodologyScreen />} />
        <Route path="*" element={<p className="notice">{messages.app.notFound}</p>} />
      </Route>
    </Routes>
  );
}
