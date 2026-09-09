import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorldStore } from '../store/useWorldStore';
import type { World } from '../data/mockData';

export const NewWorld: React.FC = () => {
  const navigate = useNavigate();
  const { addWorld, setActiveWorld } = useWorldStore();

  const handleStartImport = async (mode: string) => {
    let newId = `world-${Date.now()}`;
    
    const name = mode === 'scratch' ? 'New Chronicle' : 'Extracted World';
    const description = mode === 'scratch' 
        ? 'A blank canvas initialized in the archives. Add characters, locations, and facts manually.'
        : 'A world extracted from uploaded manuscript sources. Entities and timeline markers discovered by AI analysis.';

    try {
      const response = await fetch('http://localhost:8000/worlds', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, description })
      });
      if (response.ok) {
        const data = await response.json();
        newId = data.id;
      }
    } catch (e) {
      console.error("Failed to create world via API", e);
    }
    
    // Create new world object in state
    const newWorld: World = {
      id: newId,
      name: mode === 'scratch' ? 'New Chronicle' : 'Extracted World',
      description: mode === 'scratch' 
        ? 'A blank canvas initialized in the archives. Add characters, locations, and facts manually.'
        : 'A world extracted from uploaded manuscript sources. Entities and timeline markers discovered by AI analysis.',
      status: 'active',
      coverImage: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAuBUQknn_uISnwdR-0unHTT5VRn-yce6HhfPUnOIG_Ony7WbXISoUWuWh5wyVeqSOLTYFIiAP74lHr0RUBulB0dCbAuA9H3-tAAOjJyR81Mq8O6R3RvmKn59tBm-9l7GCG4SfTilfGXtrFZCYZB8exnTe1_mAXZFow2X7Xc6mLFUmxt3pgQ06mqEa2md5K7Pjv_DD0xt27x6wjj1JqQ9A-zVBTwdoBwbbKRPLuYWojrHy2j6YDRs9kHg',
      entryCount: mode === 'scratch' ? 0 : 5,
      entityCount: mode === 'scratch' ? 0 : 12,
      manuscriptCount: mode === 'scratch' ? 0 : 1,
      characterCount: 0,
      locationCount: 0,
      objectCount: 0,
      eventCount: 0
    };

    addWorld(newWorld);
    setActiveWorld(newId);
    
    // Direct to processing page or manuscripts depending on flow
    if (mode === 'manuscript') {
        navigate(`/worlds/${newId}/manuscripts`);
    } else {
        navigate(`/worlds/${newId}/processing`);
    }
  };

  return (
    <div className="bg-void-black text-on-background min-h-screen w-full font-body-md selection:bg-primary/30 selection:text-primary-fixed flex flex-col items-center justify-center overflow-x-hidden select-none relative">
      
      {/* Background Noise Texture */}
      <div className="fixed inset-0 pointer-events-none opacity-5 mix-blend-overlay z-0" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E')" }}></div>
      
      <main className="relative z-10 w-full max-w-4xl px-gutter py-12 flex flex-col items-center animate-fade-in-up">
        
        {/* Header */}
        <header className="text-center mb-stack-lg max-w-2xl mx-auto flex flex-col gap-2">
          <h1 className="font-headline-lg text-headline-lg md:font-display-lg md:text-display-lg text-starlight-white tracking-tight">Create World</h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant/80 max-w-lg mx-auto">
            Bring what you already have. You don't have to build your world from zero.
          </p>
        </header>

        {/* Options Grid */}
        <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          
          {/* Option 1: Import Manuscript */}
          <button 
            onClick={() => handleStartImport('manuscript')}
            className="group flex flex-col items-center text-center p-8 rounded-xl bg-surface-container-low border border-outline-variant/30 hover:border-primary/50 transition-all duration-300 relative overflow-hidden focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="w-16 h-16 rounded-full bg-surface-container-high flex items-center justify-center mb-6 group-hover:bg-primary/10 transition-colors duration-300 border border-outline-variant/50 group-hover:border-primary/30">
              <span className="material-symbols-outlined text-3xl text-on-surface group-hover:text-primary transition-colors font-light">menu_book</span>
            </div>
            <h3 className="font-headline-md text-headline-md text-starlight-white mb-2">Import a Manuscript</h3>
            <p className="font-body-md text-body-md text-on-surface-variant/70 text-sm">
              Start by extracting lore and entities directly from your text.
            </p>
          </button>

          {/* Option 2: Import World Material */}
          <button 
            onClick={() => handleStartImport('notes')}
            className="group flex flex-col items-center text-center p-8 rounded-xl bg-surface-container-low border border-primary/30 shadow-[0_0_40px_rgba(254,182,141,0.03)] hover:border-primary transition-all duration-300 relative overflow-hidden md:-translate-y-4 focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent opacity-100 transition-opacity duration-500"></div>
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/3 h-px bg-gradient-to-r from-transparent via-primary to-transparent opacity-50"></div>
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6 border border-primary/30 group-hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined text-3xl text-primary font-light">folder_zip</span>
            </div>
            <h3 className="font-headline-md text-headline-md text-starlight-white mb-2">Import World Material</h3>
            <p className="font-body-md text-body-md text-on-surface-variant/70 text-sm">
              Bring in your notes, maps, and existing encyclopedias.
            </p>
            <div className="mt-6 flex gap-3 text-on-surface-variant/50 text-[10px] font-label-sm">
              <span className="border border-outline-variant/30 px-2 py-0.5 rounded bg-surface-container">TXT</span>
              <span className="border border-outline-variant/30 px-2 py-0.5 rounded bg-surface-container">PDF</span>
              <span className="border border-outline-variant/30 px-2 py-0.5 rounded bg-surface-container">EPUB</span>
              <span className="material-symbols-outlined text-base font-light self-center">image</span>
            </div>
          </button>

          {/* Option 3: Scratch */}
          <button 
            onClick={() => handleStartImport('scratch')}
            className="group flex flex-col items-center text-center p-8 rounded-xl bg-surface-container-low border border-outline-variant/30 hover:border-outline transition-all duration-300 relative overflow-hidden focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <div className="w-16 h-16 rounded-full bg-surface-container-high flex items-center justify-center mb-6 group-hover:bg-surface-container-highest transition-colors duration-300 border border-outline-variant/50">
              <span className="material-symbols-outlined text-3xl text-on-surface-variant font-light">add</span>
            </div>
            <h3 className="font-headline-md text-headline-md text-starlight-white mb-2">Start from Scratch</h3>
            <p className="font-body-md text-body-md text-on-surface-variant/70 text-sm">
              Begin with a blank canvas and build entity by entity.
            </p>
          </button>

        </div>

        {/* Drag and Drop Area */}
        <div 
          onClick={() => handleStartImport('manuscript')}
          className="w-full mt-12 p-12 border border-dashed border-outline-variant/50 rounded-xl bg-surface-container-lowest/50 flex flex-col items-center justify-center transition-colors hover:bg-surface-container-low/50 hover:border-primary/50 group cursor-pointer relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
          <span className="material-symbols-outlined text-4xl text-outline mb-4 group-hover:text-primary transition-colors font-light">upload_file</span>
          <p className="font-body-lg text-body-lg text-starlight-white mb-1">Drag and drop your files here</p>
          <p className="font-body-md text-body-md text-on-surface-variant/60 text-sm">or click to browse from your computer</p>
        </div>

        {/* Cancel Button */}
        <button 
          onClick={() => navigate('/worlds')} 
          className="mt-8 text-on-surface-variant/60 hover:text-primary transition-colors flex items-center gap-1 font-label-sm text-xs uppercase tracking-wider"
        >
          <span className="material-symbols-outlined text-sm font-light">arrow_back</span>
          Back to Archives
        </button>

      </main>
    </div>
  );
};
