import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AppShell } from '../components/AppShell';
import { useWorldStore } from '../store/useWorldStore';
import { apiFetch } from '../api/client';
import type { Manuscript } from '../data/mockData';

export const Manuscripts: React.FC = () => {
  const navigate = useNavigate();
  const { worldId } = useParams<{ worldId: string }>();
  const { manuscripts, setActiveManuscript, setActiveChapter } = useWorldStore();

  const [expandedManuscriptId, setExpandedManuscriptId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [localManuscripts, setLocalManuscripts] = useState<Manuscript[]>([]);

  const fetchManuscripts = async () => {
    if (!worldId) return;
    setLoading(true);
    try {
      const data = await apiFetch<any[]>(`/worlds/${worldId}/manuscripts`);
      const mapped: Manuscript[] = await Promise.all(
        data.map(async (m: any) => {
          // Fetch chapters detail for each manuscript
          let chapters = [];
          try {
            const detail = await apiFetch<any>(`/worlds/${worldId}/manuscripts/${m.id}`);
            chapters = (detail.chapters || []).map((ch: any) => ({
              id: ch.id,
              number: ch.chapter_number,
              title: ch.title,
              content: ch.content || '',
              wordCount: ch.word_count || 1200
            }));
          } catch (_) {}

          return {
            id: m.id,
            title: m.title,
            chapters
          };
        })
      );

      if (mapped.length > 0) {
        setLocalManuscripts(mapped);
        setExpandedManuscriptId(mapped[0].id);
      } else {
        setLocalManuscripts(manuscripts); // fallback mock if empty
        if (manuscripts.length > 0) {
          setExpandedManuscriptId(manuscripts[0].id);
        }
      }
    } catch (err) {
      console.warn("Failed to fetch manuscripts via API, using fallback store", err);
      setLocalManuscripts(manuscripts);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchManuscripts();
  }, [worldId]);

  const handleToggleManuscript = (id: string) => {
    setExpandedManuscriptId(expandedManuscriptId === id ? null : id);
  };

  const handleOpenChapter = (manuscriptId: string, chapterId: string) => {
    setActiveManuscript(manuscriptId);
    setActiveChapter(chapterId);
    navigate(`/worlds/${worldId}/manuscripts/${manuscriptId}`);
  };

  const handleAddManuscript = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt,.pdf,.docx,.epub';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file && worldId) {
        const formData = new FormData();
        formData.append('file', file);
        try {
          const res = await apiFetch<any>(`/worlds/${worldId}/manuscripts`, {
            method: 'POST',
            body: formData,
          });
          if (res.job_id) {
            navigate(`/worlds/${worldId}/processing?jobId=${res.job_id}`);
          }
        } catch (err: any) {
          alert(err.message || "Upload failed");
        }
      }
    };
    input.click();
  };

  const displayedList = localManuscripts.length > 0 ? localManuscripts : manuscripts;

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
                Upload Manuscript
              </button>
            </div>
          </div>

          {loading ? (
            <div className="py-20 text-center text-sm text-copper-glow flex items-center justify-center gap-2">
              <span className="material-symbols-outlined animate-spin">refresh</span>
              <span>Loading manuscripts archive...</span>
            </div>
          ) : (
            /* Tree list */
            <div className="flex flex-col gap-6 w-full">
              {displayedList.map((ms) => {
                const isExpanded = expandedManuscriptId === ms.id;
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
                    </div>

                    {/* Chapters List */}
                    {isExpanded && (
                      <div className="py-2 px-6 ml-6 relative">
                        <div className="absolute left-0 top-0 bottom-0 w-px bg-starlight-white/10" />

                        {ms.chapters.map((ch) => (
                          <div 
                            key={ch.id} 
                            onClick={() => handleOpenChapter(ms.id, ch.id)}
                            className="flex items-center justify-between py-3 relative group cursor-pointer"
                          >
                            <div className="absolute -left-6 top-1/2 w-6 h-px bg-starlight-white/10" />
                            
                            <div className="flex items-center gap-4 pl-4">
                              <span className="material-symbols-outlined text-on-surface-variant/60 text-lg font-light">description</span>
                              <div>
                                <h4 className="font-body-md text-sm text-inverse-surface group-hover:text-primary transition-colors">
                                  Chapter {ch.number}: {ch.title}
                                </h4>
                                <p className="font-label-sm text-[10px] text-on-surface-variant/50 uppercase tracking-wider mt-0.5">
                                  {ch.wordCount.toLocaleString()} words
                                </p>
                              </div>
                            </div>

                            <div className="flex items-center gap-4">
                              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] uppercase font-label-sm bg-emerald-500/5 text-emerald-400/80 border-emerald-500/20">
                                <span className="w-1 h-1 rounded-full bg-current"></span>
                                Extracted
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
          )}

        </div>
      </main>
    </AppShell>
  );
};
