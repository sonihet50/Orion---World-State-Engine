import { create } from 'zustand';
import type { 
  World, 
  Entity, 
  TimelineEvent, 
  Contradiction, 
  Manuscript 
} from '../data/mockData';
import { 
  initialWorlds, 
  initialEntities, 
  initialTimelineEvents, 
  initialContradictions, 
  demoManuscripts 
} from '../data/mockData';

interface WorldState {
  worlds: World[];
  entities: Entity[];
  timelineEvents: TimelineEvent[];
  contradictions: Contradiction[];
  manuscripts: Manuscript[];
  
  activeWorldId: string | null;
  activeManuscriptId: string | null;
  activeChapterId: string | null;
  activeEntityId: string | null;
  activeTimelineEventId: string | null;
  
  // Navigation / Panel states
  isEntityPanelOpen: boolean;
  
  // Actions
  setActiveWorld: (id: string | null) => void;
  setActiveManuscript: (id: string | null) => void;
  setActiveChapter: (id: string | null) => void;
  setActiveEntity: (id: string | null) => void;
  setActiveTimelineEvent: (id: string | null) => void;
  setEntityPanelOpen: (isOpen: boolean) => void;
  
  // World Actions
  setWorlds: (worlds: World[]) => void;
  addWorld: (world: World) => void;
  
  // Entity Actions
  addEntity: (entity: Omit<Entity, 'facts' | 'relationships' | 'appearances'>) => void;
  updateEntity: (id: string, updated: Partial<Entity>) => void;
  deleteEntity: (id: string) => void;
  
  // Fact Actions
  addFact: (entityId: string, text: string, type?: 'manual' | 'extracted', source?: string) => void;
  deleteFact: (entityId: string, factId: string) => void;
  
  // Contradiction Actions
  resolveContradiction: (id: string) => void;
  
  // Manuscript Actions
  updateChapterContent: (manuscriptId: string, chapterId: string, content: string) => void;
}

export const useWorldStore = create<WorldState>((set) => ({
  worlds: initialWorlds,
  entities: initialEntities,
  timelineEvents: initialTimelineEvents,
  contradictions: initialContradictions,
  manuscripts: demoManuscripts,
  
  activeWorldId: 'terra-incognita',
  activeManuscriptId: 'ms-1',
  activeChapterId: 'ch2',
  activeEntityId: null,
  activeTimelineEventId: 'tle-2', // Default to active timeline year 45
  
  isEntityPanelOpen: false,
  
  setActiveWorld: (id) => set({ 
    activeWorldId: id,
    // Reset selections on world change
    activeManuscriptId: id === 'terra-incognita' ? 'ms-1' : null,
    activeChapterId: id === 'terra-incognita' ? 'ch2' : null,
    activeEntityId: null,
    activeTimelineEventId: id === 'terra-incognita' ? 'tle-2' : null,
    isEntityPanelOpen: false
  }),
  
  setActiveManuscript: (id) => set((state) => {
    const manuscript = state.manuscripts.find((m) => m.id === id);
    const firstChapterId = manuscript?.chapters[0]?.id || null;
    return {
      activeManuscriptId: id,
      activeChapterId: firstChapterId
    };
  }),
  
  setActiveChapter: (id) => set({ activeChapterId: id }),
  
  setActiveEntity: (id) => set((state) => ({
    activeEntityId: id,
    isEntityPanelOpen: id !== null
  })),
  
  setActiveTimelineEvent: (id) => set((state) => {
    // When changing the selected timeline event, update the world status description
    // for a dynamic simulation
    const updatedWorlds = state.worlds.map((w) => {
      if (w.id === state.activeWorldId && id) {
        const ev = state.timelineEvents.find((e) => e.id === id);
        if (ev) {
          return {
            ...w,
            description: `${ev.title} (${ev.period} • Year ${ev.year}): ${ev.description}`
          };
        }
      }
      return w;
    });
    return {
      activeTimelineEventId: id,
      worlds: updatedWorlds
    };
  }),
  
  setEntityPanelOpen: (isOpen) => set((state) => ({ 
    isEntityPanelOpen: isOpen,
    activeEntityId: isOpen ? state.activeEntityId : null
  })),
  
  setWorlds: (worlds) => set({ worlds }),
  
  addWorld: (world) => set((state) => ({
    worlds: [...state.worlds, world]
  })),
  
  addEntity: (entityData) => set((state) => {
    const newEntity: Entity = {
      ...entityData,
      facts: [],
      relationships: [],
      appearances: []
    };
    
    // Update count in active world
    const updatedWorlds = state.worlds.map((w) => {
      if (w.id === state.activeWorldId) {
        return {
          ...w,
          entityCount: w.entityCount + 1,
          characterCount: entityData.type === 'character' ? w.characterCount + 1 : w.characterCount,
          locationCount: entityData.type === 'location' ? w.locationCount + 1 : w.locationCount,
          objectCount: entityData.type === 'object' ? w.objectCount + 1 : w.objectCount,
          eventCount: entityData.type === 'event' ? w.eventCount + 1 : w.eventCount
        };
      }
      return w;
    });

    return {
      entities: [...state.entities, newEntity],
      worlds: updatedWorlds,
      activeEntityId: newEntity.id,
      isEntityPanelOpen: true
    };
  }),
  
  updateEntity: (id, updated) => set((state) => ({
    entities: state.entities.map((e) => e.id === id ? { ...e, ...updated } : e)
  })),
  
  deleteEntity: (id) => set((state) => {
    const entityToDelete = state.entities.find((e) => e.id === id);
    const updatedWorlds = state.worlds.map((w) => {
      if (w.id === state.activeWorldId && entityToDelete) {
        return {
          ...w,
          entityCount: Math.max(0, w.entityCount - 1),
          characterCount: entityToDelete.type === 'character' ? Math.max(0, w.characterCount - 1) : w.characterCount,
          locationCount: entityToDelete.type === 'location' ? Math.max(0, w.locationCount - 1) : w.locationCount,
          objectCount: entityToDelete.type === 'object' ? Math.max(0, w.objectCount - 1) : w.objectCount,
          eventCount: entityToDelete.type === 'event' ? Math.max(0, w.eventCount - 1) : w.eventCount
        };
      }
      return w;
    });

    return {
      entities: state.entities.filter((e) => e.id !== id),
      worlds: updatedWorlds,
      activeEntityId: state.activeEntityId === id ? null : state.activeEntityId,
      isEntityPanelOpen: state.activeEntityId === id ? false : state.isEntityPanelOpen
    };
  }),
  
  addFact: (entityId, text, type = 'manual', source = 'Manual') => set((state) => ({
    entities: state.entities.map((e) => {
      if (e.id === entityId) {
        const newFact = {
          id: `fact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          text,
          source,
          type
        };
        return {
          ...e,
          facts: [...e.facts, newFact]
        };
      }
      return e;
    })
  })),
  
  deleteFact: (entityId, factId) => set((state) => ({
    entities: state.entities.map((e) => {
      if (e.id === entityId) {
        return {
          ...e,
          facts: e.facts.filter((f) => f.id !== factId)
        };
      }
      return e;
    })
  })),
  
  resolveContradiction: (id) => set((state) => {
    // Smoothly mark resolved, which will allow UI exit animations
    const updatedContradictions = state.contradictions.map((c) => 
      c.id === id ? { ...c, resolved: true } : c
    );
    return {
      contradictions: updatedContradictions
    };
  }),
  
  updateChapterContent: (manuscriptId, chapterId, content) => set((state) => {
    const updatedManuscripts = state.manuscripts.map((m) => {
      if (m.id === manuscriptId) {
        const updatedChapters = m.chapters.map((ch) => {
          if (ch.id === chapterId) {
            // Count words (naive space splitting)
            const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
            return {
              ...ch,
              content,
              wordCount
            };
          }
          return ch;
        });
        return { ...m, chapters: updatedChapters };
      }
      return m;
    });
    return { manuscripts: updatedManuscripts };
  })
}));
