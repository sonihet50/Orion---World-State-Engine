import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../components/AppShell';
import { useWorldStore } from '../store/useWorldStore';

export const WritingRoom: React.FC = () => {
  const navigate = useNavigate();
  const { worldId, manuscriptId } = useParams<{ worldId: string; manuscriptId: string }>();
  
  const { 
    manuscripts, 
    activeManuscriptId,
    activeChapterId,
    setActiveChapter, 
    entities,
    setActiveEntity,
    updateChapterContent
  } = useWorldStore();

  const currentManuscriptId = manuscriptId || activeManuscriptId || 'ms-1';
  const manuscript = manuscripts.find((m) => m.id === currentManuscriptId);
  const activeChapter = manuscript?.chapters.find((ch) => ch.id === activeChapterId) || manuscript?.chapters[0];

  const [isEditing, setIsEditing] = useState(false);
  const [editorContent, setEditorContent] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);

  const handleStartEdit = () => {
    if (activeChapter) {
      setEditorContent(activeChapter.content);
      setIsEditing(true);
    }
  };

  const handleSaveEdit = () => {
    if (activeChapter && manuscript) {
      updateChapterContent(manuscript.id, activeChapter.id, editorContent);
      setIsEditing(false);
    }
  };

  const handleRerunExtraction = () => {
    setIsExtracting(true);
    // Simulate AI extraction loading
    setTimeout(() => {
      setIsExtracting(false);
      alert('Extraction complete! Found new references. Ledger sync updated.');
    }, 1500);
  };

  // Helper to split text by entity names and inject interactive highlight tags
  const renderTextWithHighlights = (text: string) => {
    if (!text) return null;

    // Filter entities that exist in this world
    const activeEntities = entities;

    if (activeEntities.length === 0) return <span>{text}</span>;

    // Sort by length desc to match longer phrases first (e.g. "Elara Vance" before "Elara")
    const sortedEntityNames = [...activeEntities]
      .map(e => e.name)
      .sort((a, b) => b.length - a.length);

    // Escape special regex chars
    const escapedNames = sortedEntityNames.map(name => 
      name.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')
    );

    // Form regex: word boundaries with options
    const regex = new RegExp(`\\b(${escapedNames.join('|')})\\b`, 'gi');

    // Split text into matches and non-matches
    const parts = text.split(regex);
    if (parts.length <= 1) return <span>{text}</span>;

    return (
      <span>
        {parts.map((part, index) => {
          // Check if this part matches an entity name (case insensitive)
          const matchedEntity = activeEntities.find(
            e => e.name.toLowerCase() === part.toLowerCase()
          );

          if (matchedEntity) {
            return (
              <span 
                key={index} 
                className="entity-highlight text-starlight-white font-medium"
                title={`${matchedEntity.type.toUpperCase()}: Click to view profile`}
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveEntity(matchedEntity.id);
                }}
              >
                {part}
              </span>
            );
          }
          return part;
        })}
      </span>
    );
  };

  return (
    <AppShell>
      {/* Editor Main Section */}
      <main className="flex-1 flex h-full bg-[#09090b] relative overflow-hidden select-text">
        
        {/* Left internal sidebar: Chapters List */}
        <aside className="w-72 border-r border-starlight-white/5 bg-surface-container-lowest flex flex-col shrink-0 select-none">
          <div className="p-4 border-b border-starlight-white/5 flex items-center justify-between bg-gradient-to-b from-surface-container-highest/20 to-transparent">
            <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest text-[10px]">Chapters</h2>
            <button 
              onClick={() => {
                const title = prompt('Enter new chapter title:');
                if (title && title.trim()) {
                  const nextNum = (manuscript?.chapters.length || 0) + 1;
                  const newChapter = {
                    id: `ch-${Date.now()}`,
                    number: nextNum,
                    title: title.trim(),
                    content: 'Start writing your new chapter here...',
                    wordCount: 5
                  };
                  if (manuscript) {
                    const updated = [...manuscript.chapters, newChapter];
                    const updatedManuscripts = manuscripts.map(m => 
                      m.id === manuscript.id ? { ...m, chapters: updated } : m
                    );
                    useWorldStore.setState({ manuscripts: updatedManuscripts, activeChapterId: newChapter.id });
                  }
                }
              }}
              className="text-on-surface-variant/65 hover:text-primary transition-colors p-1"
            >
              <span className="material-symbols-outlined text-sm font-light">add</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {manuscript?.chapters.map((ch) => {
              const isActive = ch.id === activeChapterId;
              return (
                <div 
                  key={ch.id}
                  onClick={() => {
                    setActiveChapter(ch.id);
                    setIsEditing(false); // Stop editing on select change
                  }}
                  className={`group px-4 py-3 rounded-lg relative overflow-hidden cursor-pointer transition-all duration-300 border ${
                    isActive 
                      ? 'bg-surface-container-low border-starlight-white/10 text-starlight-white' 
                      : 'border-transparent text-on-surface-variant/75 hover:bg-surface-container-lowest/50 hover:text-on-surface'
                  }`}
                >
                  {isActive && (
                    <>
                      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/5 via-transparent to-transparent opacity-50"></div>
                      <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary"></div>
                    </>
                  )}
                  <div className={`font-label-sm text-[10px] uppercase tracking-wider mb-1 ${isActive ? 'text-primary' : 'text-on-surface-variant/40'}`}>
                    Chapter {ch.number}
                  </div>
                  <div className="font-body-md text-sm font-medium">{ch.title}</div>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Right main panel: Editor Canvas */}
        <section className="flex-1 flex flex-col relative overflow-hidden">
          
          {/* Action Bar */}
          <div className="h-16 flex items-center justify-between px-8 border-b border-starlight-white/5 bg-surface-container-lowest/60 backdrop-blur-sm z-20 select-none">
            <div className="flex items-center gap-3">
              {isEditing ? (
                <button 
                  onClick={handleSaveEdit}
                  className="px-5 py-1.5 rounded-full bg-primary hover:bg-copper-glow text-void-black font-label-sm text-xs font-semibold uppercase tracking-widest transition-all duration-300 shadow-md"
                >
                  Save Changes
                </button>
              ) : (
                <button 
                  onClick={handleStartEdit}
                  className="px-5 py-1.5 rounded-full border border-copper-glow/50 text-copper-glow font-label-sm text-xs font-semibold uppercase tracking-widest hover:bg-copper-glow hover:text-void-black transition-all duration-300"
                >
                  Edit Text
                </button>
              )}

              <button 
                onClick={handleRerunExtraction}
                disabled={isExtracting}
                className="px-4 py-1.5 rounded-full text-on-surface-variant/80 font-label-sm text-xs uppercase tracking-wider hover:text-primary hover:bg-primary/5 transition-all flex items-center gap-2"
              >
                <span className={`material-symbols-outlined text-[16px] font-light ${isExtracting ? 'animate-spin' : ''}`}>
                  {isExtracting ? 'sync' : 'refresh'}
                </span>
                {isExtracting ? 'Extracting...' : 'Re-run Extraction'}
              </button>
            </div>

            <div className="flex items-center gap-4 text-on-surface-variant/40 font-label-sm text-[10px] uppercase tracking-wider">
              <span>Words: {activeChapter?.wordCount.toLocaleString()}</span>
              <span>•</span>
              <span>Synced</span>
            </div>
          </div>

          {/* Reading/Editing Area */}
          <div className="flex-1 overflow-y-auto px-8 md:px-24 py-16">
            <article className="max-w-3xl mx-auto pb-48">
              
              {/* Header Title */}
              <header className="mb-12 select-none">
                <span className="font-label-sm text-[10px] text-primary uppercase tracking-[0.2em] mb-3 block">
                  Chapter {activeChapter?.number}
                </span>
                <h1 className="font-display-lg text-display-lg text-starlight-white mb-6">
                  {activeChapter?.title}
                </h1>
                <div className="h-px w-24 bg-gradient-to-r from-copper-glow to-transparent opacity-50"></div>
              </header>

              {/* Editable Textbox or Formatted View */}
              {isEditing ? (
                <textarea 
                  value={editorContent}
                  onChange={(e) => setEditorContent(e.target.value)}
                  className="w-full bg-transparent border-0 text-body-lg text-on-surface-variant leading-relaxed focus:ring-0 focus:outline-none h-[400px] resize-none"
                  style={{ fontFamily: 'Source Serif 4, serif' }}
                />
              ) : (
                <div 
                  className="prose prose-invert prose-lg font-body-lg text-body-lg text-on-surface-variant leading-relaxed space-y-8 select-text"
                  style={{ fontFamily: 'Source Serif 4, serif', fontSize: '18px', lineHeight: '28px' }}
                >
                  {/* Paragraph splitter */}
                  {activeChapter?.content.split('\n\n').map((paragraph, index) => (
                    <p key={index}>
                      {renderTextWithHighlights(paragraph)}
                    </p>
                  ))}
                </div>
              )}

            </article>
          </div>

        </section>

      </main>
    </AppShell>
  );
};
