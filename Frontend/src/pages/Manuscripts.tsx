import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AppShell } from '../components/AppShell';
import { useWorldStore } from '../store/useWorldStore';

export const Manuscripts: React.FC = () => {
  const navigate = useNavigate();
  const { worldId } = useParams<{ worldId: string }>();
  const { manuscripts, setActiveManuscript, setActiveChapter } = useWorldStore();

  const [expandedManuscriptId, setExpandedManuscriptId] = useState<string | null>('ms-1');

  const handleToggleManuscript = (id: string) => {
    setExpandedManuscriptId(expandedManuscriptId === id ? null : id);
  };

  const handleOpenChapter = (manuscriptId: string, chapterId: string) => {
    setActiveManuscript(manuscriptId);
    setActiveChapter(chapterId);
    navigate(`/worlds/${worldId}/manuscripts/${manuscriptId}`);
  };

  const handleAddChapter = (manuscriptId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    // For prototype, prompt for chapter name and append it to local state
    const title = prompt('Enter new chapter title:');
    if (title && title.trim()) {
      const store = useWorldStore.getState();
      const manuscript = store.manuscripts.find(m => m.id === manuscriptId);
      if (manuscript) {
        const nextNum = manuscript.chapters.length + 1;
        const newChapter = {
          id: `ch-${Date.now()}`,
          number: nextNum,
          title: title.trim(),
          content: 'Start writing your new chapter here...',
          wordCount: 5
        };
        const updatedChapters = [...manuscript.chapters, newChapter];
        // We can use updateManuscript or similar, let's update via direct store reference
        const updatedManuscripts = store.manuscripts.map(m => 
          m.id === manuscriptId ? { ...m, chapters: updatedChapters } : m
        );
        useWorldStore.setState({ manuscripts: updatedManuscripts });
      }
    }
  };

  const handleAddManuscript = async () => {
    // Create an invisible file input to trigger upload
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file && worldId) {
        const formData = new FormData();
        formData.append('file', file);
        try {
          const res = await fetch(`http://localhost:8000/worlds/${worldId}/manuscripts`, {
            method: 'POST',
            body: formData,
          });
          if (res.ok) {
            const data = await res.json();
            navigate(`/worlds/${worldId}/processing?jobId=${data.job_id}`);
          }
        } catch (err) {
          console.error("Upload failed", err);
        }
      }
    };
    input.click();
  };

  return (
    <AppShell>
      {/* Background elements */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-deep-charcoal/40 via-void-black to-void-black -z-10 pointer-events-none"></div>

      <main className="flex-1 min-h-screen overflow-y-auto px-8 md:px-12 py-10">
        <div className="max-w-5xl mx-auto flex flex-col gap-8 animate-fade-in-up">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-starlight-white/5 pb-6">
            <div>
              <span className="font-label-sm text-[10px] text-primary uppercase tracking-[0.2em] mb-1.5 block">Chronicle Library</span>
              <h2 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-starlight-white mb-2">Manuscripts Archive</h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant/80 max-w-2xl leading-relaxed">
                Organize your primary texts. Extract entities into the world ledger automatically.
              </p>
            </div>
            <div className="flex items-center gap-4 shrink-0">
              <button 
                onClick={handleAddManuscript}
                className="flex items-center gap-2 font-label-sm text-xs text-copper-glow border border-copper-glow/50 rounded px-5 py-2.5 hover:bg-copper-glow hover:text-void-black transition-all uppercase tracking-wider font-semibold shadow-lg hover:shadow-primary/10"
              >
                <span className="material-symbols-outlined text-sm font-light">add</span>
                New Manuscript
              </button>
            </div>
          </div>

          {/* Tree list */}
          <div className="flex flex-col gap-6 w-full">
            {manuscripts.map((ms) => {
              const isExpanded = expandedManuscriptId === ms.id;
              
              // Count words in manuscript
              const totalWords = ms.chapters.reduce((sum, ch) => sum + ch.wordCount, 0);

              return (
                <div 
                  key={ms.id}
                  className="bg-surface-container-low/50 border border-starlight-white/10 rounded-lg overflow-hidden hover-glow transition-all duration-300 shadow-md"
                >
                  {/* Folder Header */}
                  <div 
                    onClick={() => handleToggleManuscript(ms.id)}
                    className="flex items-center justify-between p-4 cursor-pointer group border-b border-starlight-white/5 bg-gradient-to-b from-surface-container-highest/20 to-transparent"
                  >
                    <div className="flex items-center gap-4">
                      <span className="material-symbols-outlined text-primary text-xl font-light">
                        {isExpanded ? 'folder_open' : 'folder'}
                      </span>
                      <div>
                        <h3 className="font-headline-md text-headline-md text-starlight-white group-hover:text-primary transition-colors text-lg">
                          {ms.title}
                        </h3>
                        <p className="font-label-sm text-[10px] text-on-surface-variant/40 uppercase tracking-widest mt-1">
                          {ms.chapters.length} {ms.chapters.length === 1 ? 'Chapter' : 'Chapters'} • {totalWords.toLocaleString()} words total
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={(e) => handleAddChapter(ms.id, e)} 
                        className="text-on-surface-variant hover:text-primary transition-colors p-1" 
                        title="Add Chapter"
                      >
                        <span className="material-symbols-outlined text-base font-light">add_box</span>
                      </button>
                    </div>
                  </div>

                  {/* Chapters List */}
                  {isExpanded && (
                    <div className="py-2 px-6 ml-6 relative">
                      {/* Tree line connector */}
                      <div className="absolute left-0 top-0 bottom-0 w-px bg-starlight-white/10" />

                      {ms.chapters.map((ch, idx) => (
                        <div 
                          key={ch.id} 
                          onClick={() => handleOpenChapter(ms.id, ch.id)}
                          className="flex items-center justify-between py-3 relative group cursor-pointer"
                        >
                          {/* Horizontal connector line */}
                          <div className="absolute -left-6 top-1/2 w-6 h-px bg-starlight-white/10" />
                          
                          <div className="flex items-center gap-4 pl-4">
                            <span className="material-symbols-outlined text-on-surface-variant/60 text-lg font-light">description</span>
                            <div>
                              <h4 className="font-body-md text-sm text-inverse-surface group-hover:text-primary transition-colors">
                                Chapter {ch.number}: {ch.title}
                              </h4>
                              <p className="font-label-sm text-[10px] text-on-surface-variant/50 uppercase tracking-wider mt-0.5">
                                {ch.wordCount.toLocaleString()} words • Last edited 2h ago
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-4">
                            {/* Sync Status Tag */}
                            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] uppercase font-label-sm ${
                              ch.number <= 2 
                                ? 'bg-emerald-500/5 text-emerald-400/80 border-emerald-500/20' 
                                : ch.number === 3 
                                  ? 'bg-amber-500/5 text-amber-400/80 border-amber-500/20'
                                  : 'bg-primary/5 text-primary/80 border-primary/20'
                            }`}>
                              <span className="w-1 h-1 rounded-full bg-current"></span>
                              {ch.number <= 2 ? 'Extracted' : ch.number === 3 ? 'Unsynced Facts' : 'Drafting'}
                            </div>
                            <span className="material-symbols-outlined text-sm text-on-surface-variant/30 group-hover:text-primary transition-colors">edit</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

        </div>
      </main>
    </AppShell>
  );
};
