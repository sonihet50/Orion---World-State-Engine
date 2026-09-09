import React, { useState } from 'react';
import { AppShell } from '../components/AppShell';
import { useWorldStore } from '../store/useWorldStore';
import type { Entity } from '../data/mockData';

export const EntityLedger: React.FC = () => {
  const { entities, setActiveEntity, addEntity } = useWorldStore();
  
  const [activeTab, setActiveTab] = useState<'all' | 'character' | 'location' | 'object' | 'event'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Forge Entity Form Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'character' | 'location' | 'object' | 'event'>('character');
  const [entityName, setEntityName] = useState('');
  const [entitySubtype, setEntitySubtype] = useState('');
  const [entityDesc, setEntityDesc] = useState('');

  const filteredEntities = entities.filter((e) => {
    const matchesTab = activeTab === 'all' || e.type === activeTab;
    const matchesSearch = e.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          e.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          e.subtype?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTab && matchesSearch;
  });

  const handleOpenModal = (type: typeof modalType) => {
    setModalType(type);
    setEntityName('');
    setEntitySubtype('');
    setEntityDesc('');
    setIsModalOpen(true);
  };

  const handleForgeEntity = (e: React.FormEvent) => {
    e.preventDefault();
    if (entityName.trim() && entityDesc.trim()) {
      addEntity({
        id: `entity-${Date.now()}`,
        name: entityName.trim(),
        type: modalType,
        subtype: entitySubtype.trim() || undefined,
        description: entityDesc.trim()
      });
      setIsModalOpen(false);
    }
  };

  const getTypeIcon = (type: Entity['type']) => {
    switch (type) {
      case 'character': return 'group';
      case 'location': return 'location_on';
      case 'object': return 'category';
      case 'event': return 'event_note';
      default: return 'help';
    }
  };

  const getTypeColor = (type: Entity['type']) => {
    switch (type) {
      case 'character': return 'text-copper-glow border-copper-glow/20';
      case 'location': return 'text-secondary border-secondary/20';
      case 'object': return 'text-tertiary border-tertiary/20';
      case 'event': return 'text-error border-error/20';
      default: return 'text-on-surface-variant border-starlight-white/5';
    }
  };

  return (
    <AppShell>
      {/* Background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-surface-container-high/10 via-void-black to-void-black -z-10 pointer-events-none"></div>

      <main className="flex-1 min-h-screen overflow-y-auto px-8 md:px-12 py-10">
        <div className="max-w-7xl mx-auto flex flex-col gap-8 animate-fade-in-up">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-starlight-white/5 pb-6">
            <div>
              <span className="font-label-sm text-[10px] text-primary uppercase tracking-[0.2em] mb-1.5 block">World Archive</span>
              <h2 className="font-headline-lg text-starlight-white mb-2">World Ledger</h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant/80 max-w-2xl">
                Browse, search, and edit the characters, landmarks, and key objects of your universe.
              </p>
            </div>
            
            {/* Quick Forge Menu */}
            <div className="flex gap-2.5 shrink-0">
              <button 
                onClick={() => handleOpenModal('character')}
                className="flex items-center gap-1.5 font-label-sm text-[11px] text-primary border border-primary/20 hover:border-primary px-4 py-2 rounded uppercase tracking-wider font-semibold hover:bg-primary/5 transition-all"
              >
                <span className="material-symbols-outlined text-sm font-light">group</span> Character
              </button>
              <button 
                onClick={() => handleOpenModal('location')}
                className="flex items-center gap-1.5 font-label-sm text-[11px] text-secondary border border-secondary/20 hover:border-secondary px-4 py-2 rounded uppercase tracking-wider font-semibold hover:bg-secondary/5 transition-all"
              >
                <span className="material-symbols-outlined text-sm font-light">location_on</span> Location
              </button>
            </div>
          </div>

          {/* Search and Filters Bar */}
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
            
            {/* Tabs */}
            <div className="flex bg-surface-container-lowest/80 border border-starlight-white/10 p-1 rounded-lg">
              {([
                { id: 'all', label: 'All Entries', icon: 'list' },
                { id: 'character', label: 'Characters', icon: 'group' },
                { id: 'location', label: 'Locations', icon: 'location_on' },
                { id: 'object', label: 'Objects', icon: 'category' }
              ] as const).map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded font-label-sm text-xs uppercase tracking-wider transition-all ${
                    activeTab === tab.id 
                      ? 'bg-primary text-void-black font-semibold' 
                      : 'text-on-surface-variant hover:text-white'
                  }`}
                >
                  <span className="material-symbols-outlined text-[15px] font-light">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="relative group min-w-[260px]">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/40 text-lg group-focus-within:text-primary transition-colors font-light">search</span>
              <input 
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search ledger entries..."
                className="w-full bg-surface-container-lowest border border-starlight-white/10 rounded px-10 py-2.5 font-body-md text-xs text-on-surface placeholder:text-on-surface-variant/30 focus:border-primary focus:ring-0 focus:outline-none"
              />
            </div>

          </div>

          {/* Grid List */}
          {filteredEntities.length === 0 ? (
            <div className="py-20 text-center text-sm text-on-surface-variant/40 italic bg-surface-container-low/20 rounded-xl border border-dashed border-starlight-white/5">
              No chronicle ledger entries match your filter.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-24">
              {filteredEntities.map((e) => (
                <article 
                  key={e.id}
                  onClick={() => setActiveEntity(e.id)}
                  className="bg-surface-container-low/40 border border-starlight-white/5 hover:border-primary/30 rounded-xl p-5 hover-glow transition-all duration-300 flex flex-col gap-4 cursor-pointer relative overflow-hidden group"
                >
                  {/* Subtle hover glow accent */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

                  <header className="flex justify-between items-start border-b border-starlight-white/5 pb-3">
                    <div>
                      <span className={`font-label-sm text-[9px] uppercase tracking-widest border px-2 py-0.5 rounded-full flex items-center gap-1.5 ${getTypeColor(e.type)}`}>
                        <span className="material-symbols-outlined text-[12px] font-light">{getTypeIcon(e.type)}</span>
                        {e.type}
                      </span>
                      <h3 className="font-headline-md text-starlight-white mt-2 group-hover:text-primary transition-colors text-base font-semibold">
                        {e.name}
                      </h3>
                    </div>
                    {e.alias && (
                      <span className="font-body-md text-xs text-on-surface-variant/50 italic">
                        "{e.alias}"
                      </span>
                    )}
                  </header>

                  <p className="font-body-md text-xs text-on-surface-variant/80 leading-relaxed flex-1 line-clamp-3">
                    {e.description}
                  </p>

                  {/* Footer details */}
                  <footer className="mt-4 pt-3 border-t border-starlight-white/5 flex items-center justify-between text-[10px] font-label-sm text-on-surface-variant/40 uppercase tracking-widest">
                    <span>{e.subtype || 'Ledger entry'}</span>
                    <span>{e.facts.length} {e.facts.length === 1 ? 'Fact' : 'Facts'}</span>
                  </footer>
                </article>
              ))}
            </div>
          )}

        </div>
      </main>

      {/* Creation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-void-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-gutter">
          <div className="bg-surface-container-low border border-starlight-white/10 rounded-xl max-w-lg w-full p-6 shadow-2xl relative animate-fade-in-up">
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-on-surface-variant hover:text-white p-1 rounded-full hover:bg-white/5"
            >
              <span className="material-symbols-outlined font-light">close</span>
            </button>
            
            <h2 className="font-headline-md text-headline-md text-primary mb-2 capitalize">
              Forge New {modalType}
            </h2>
            <p className="text-xs text-on-surface-variant/60 mb-6">
              Create a new entity in the ledger. It will instantly link with manuscripts, timelines, and graphs.
            </p>

            <form onSubmit={handleForgeEntity} className="space-y-4">
              <div>
                <label className="block text-xs font-label-sm text-on-surface-variant/80 uppercase mb-2">Name</label>
                <input 
                  type="text"
                  required
                  value={entityName}
                  onChange={(e) => setEntityName(e.target.value)}
                  placeholder={`e.g. ${modalType === 'character' ? 'Valerius Thorne' : modalType === 'location' ? 'The Iron Valley' : 'Aetheric compass'}`}
                  className="w-full bg-void-black text-sm text-starlight-white border border-starlight-white/10 rounded p-2.5 focus:border-primary focus:ring-0 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-label-sm text-on-surface-variant/80 uppercase mb-2">Subtype / Role</label>
                <input 
                  type="text"
                  value={entitySubtype}
                  onChange={(e) => setEntitySubtype(e.target.value)}
                  placeholder={`e.g. ${modalType === 'character' ? 'Antagonist / Trader' : modalType === 'location' ? 'Syndicate Outpost' : 'Key Lore Item'}`}
                  className="w-full bg-void-black text-sm text-starlight-white border border-starlight-white/10 rounded p-2.5 focus:border-primary focus:ring-0 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-label-sm text-on-surface-variant/80 uppercase mb-2">Description / Synopsis</label>
                <textarea 
                  required
                  value={entityDesc}
                  onChange={(e) => setEntityDesc(e.target.value)}
                  placeholder="Enter a brief history or description..."
                  rows={3}
                  className="w-full bg-void-black text-sm text-starlight-white border border-starlight-white/10 rounded p-2.5 focus:border-primary focus:ring-0 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-starlight-white/5">
                <button 
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-label-sm uppercase tracking-widest text-on-surface-variant hover:text-white"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-6 py-2 bg-primary hover:bg-copper-glow text-void-black font-label-sm text-xs uppercase tracking-widest font-semibold rounded shadow-lg hover:shadow-primary/10 transition-all"
                >
                  Forge Entity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
};
