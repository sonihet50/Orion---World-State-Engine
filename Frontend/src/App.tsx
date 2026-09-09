import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignIn } from './pages/SignIn';
import { Worlds } from './pages/Worlds';
import { NewWorld } from './pages/NewWorld';
import { ProcessingWorld } from './pages/ProcessingWorld';
import { WorldHome } from './pages/WorldHome';
import { Manuscripts } from './pages/Manuscripts';
import { WritingRoom } from './pages/WritingRoom';
import { EntityLedger } from './pages/EntityLedger';
import { WorldGraph } from './pages/WorldGraph';
import { WorldTimeline } from './pages/WorldTimeline';
import { Contradictions } from './pages/Contradictions';
import { WorldAssistant } from './pages/WorldAssistant';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth / Entry */}
        <Route path="/signin" element={<SignIn />} />
        
        {/* World Select and Forge */}
        <Route path="/worlds" element={<Worlds />} />
        <Route path="/worlds/new" element={<NewWorld />} />
        
        {/* World Dashboard & Sub-modules */}
        <Route path="/worlds/:worldId" element={<WorldHome />} />
        <Route path="/worlds/:worldId/processing" element={<ProcessingWorld />} />
        <Route path="/worlds/:worldId/manuscripts" element={<Manuscripts />} />
        <Route path="/worlds/:worldId/manuscripts/:manuscriptId" element={<WritingRoom />} />
        <Route path="/worlds/:worldId/world" element={<EntityLedger />} />
        <Route path="/worlds/:worldId/graph" element={<WorldGraph />} />
        <Route path="/worlds/:worldId/timeline" element={<WorldTimeline />} />
        <Route path="/worlds/:worldId/contradictions" element={<Contradictions />} />
        <Route path="/worlds/:worldId/assistant" element={<WorldAssistant />} />

        {/* Fallbacks */}
        <Route path="/" element={<Navigate to="/signin" replace />} />
        <Route path="*" element={<Navigate to="/signin" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
