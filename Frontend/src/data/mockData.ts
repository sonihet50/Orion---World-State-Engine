export interface Entity {
  id: string;
  name: string;
  type: 'character' | 'location' | 'object' | 'event';
  subtype?: string;
  alias?: string;
  description: string;
  image?: string;
  traits?: string[];
  facts: {
    id: string;
    text: string;
    source: string;
    type: 'extracted' | 'manual';
  }[];
  relationships: {
    targetId: string;
    targetName: string;
    targetType: 'character' | 'location' | 'object' | 'event';
    relation: string;
    isNegative?: boolean;
  }[];
  appearances: string[]; // chapterIds
}

export interface TimelineEvent {
  id: string;
  year: number;
  period: string;
  title: string;
  description: string;
  stateChanges: {
    entityId: string;
    entityName: string;
    entityType: 'character' | 'location' | 'object';
    field: string;
    before: string;
    after: string;
    isError?: boolean;
  }[];
  chapters: { id: string; name: string }[];
}

export interface Contradiction {
  id: string;
  title: string;
  category: string;
  targetEntityId: string;
  severity: 'high' | 'medium' | 'low';
  summary: string;
  sources: {
    sourceName: string;
    text: string;
    highlightedWord: string;
  }[];
  resolved: boolean;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  content: string;
  wordCount: number;
}

export interface Manuscript {
  id: string;
  title: string;
  chapters: Chapter[];
}

export interface World {
  id: string;
  name: string;
  description: string;
  coverImage?: string;
  status: 'active' | 'archived' | 'drafting';
  entryCount: number;
  entityCount: number;
  manuscriptCount: number;
  characterCount: number;
  locationCount: number;
  objectCount: number;
  eventCount: number;
}

export const initialWorlds: World[] = [
  {
    id: 'terra-incognita',
    name: 'Terra Incognita',
    description: 'A fragmented archipelago floating above the Abyssal Sea, where remnants of the Old Magic clash with emerging steam-powered syndicates.',
    coverImage: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAuBUQknn_uISnwdR-0unHTT5VRn-yce6HhfPUnOIG_Ony7WbXISoUWuWh5wyVeqSOLTYFIiAP74lHr0RUBulB0dCbAuA9H3-tAAOjJyR81Mq8O6R3RvmKn59tBm-9l7GCG4SfTilfGXtrFZCYZB8exnTe1_mAXZFow2X7Xc6mLFUmxt3pgQ06mqEa2md5K7Pjv_DD0xt27x6wjj1JqQ9A-zVBTwdoBwbbKRPLuYWojrHy2j6YDRs9kHg',
    status: 'active',
    entryCount: 14,
    entityCount: 42,
    manuscriptCount: 2,
    characterCount: 6,
    locationCount: 4,
    objectCount: 4,
    eventCount: 4,
  },
  {
    id: 'sundered-isles',
    name: 'The Sundered Isles',
    description: 'A minimalist line art illustration of a fractured celestial sphere hovering above a dark, vast ocean with subtle hints of copper.',
    coverImage: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBouZab8-ItfAtiaomHqKLcsJBfkbvirWQ1o0c-OpeNnBCnkkAWB9ZBawOkSCThDj6ABVAzoTccSXClky2sxMY3tyDnUgplfGbMucsVLlmFtuZ7V2R6eW6JJGKDfFPJrDO0b-s_0MEa8COEcnhtE76pag9CMnpFd4D49_WJ3NHrixmtrKj8dwLB6x3znvYGtF4axKawM9GPaoA9TWPVBZ54hd9QTpNNVmWkKXvmpwljN2HwsZ2sk3md4g',
    status: 'archived',
    entryCount: 8,
    entityCount: 12,
    manuscriptCount: 1,
    characterCount: 3,
    locationCount: 2,
    objectCount: 2,
    eventCount: 2,
  },
  {
    id: 'neo-veridia',
    name: 'Neo-Veridia',
    description: 'A dense, vertical cyberpunk cityscape enveloped in perpetual twilight, characterized by towering brutalist structures of dark concrete.',
    coverImage: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCddch7vjtrfzJFj8ghyS2sVDzmGKlN5PYlcaCIlyhnIm2otSz9r84B5txC7BYgKGcLwL1_eUtYDXAL8pGLdymnZMEReWaZpndRDfH0_AgSe8Bkhgu9O2Gitf5yryjiFJXuvj9nbtIWmMHiki2_tAep_KIjaFODwxvAE0p5YtZk9qA4jkbAeEp7JyiAP5-4f7XtdfLz-wIFvqtLfj38-WmOF5emEt5CbXywVmDSqkBvded5LaRF1lvbYQ',
    status: 'drafting',
    entryCount: 2,
    entityCount: 12,
    manuscriptCount: 1,
    characterCount: 4,
    locationCount: 3,
    objectCount: 2,
    eventCount: 1,
  }
];

export const initialEntities: Entity[] = [
  {
    id: 'elara-vance',
    name: 'Elara Vance',
    type: 'character',
    subtype: 'Protagonist',
    alias: 'Spark',
    description: 'A former archivist of the Old Citadel who discovered the anomalous texts leading to the Great Severance. She possesses an innate, untrained affinity for interpreting Aetheric patterns.',
    image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB9R-xwqUHO8lXChd8E8dr-yNUy4dZldRpySAuoA0XHn6VWDerXmMAYNpup4C-6kEqU6mAyf6qgTJqLN5HcyHMjlQ8W2DjhpOlrqwtd5h7uPjgC0uy6av5egMOr9xn6WRmygNwu1p4kWmWRENfbtphCiy1gYJhcNDCUG5o6BpZCh1syq89vEe54gUC06PU-C0PQPmSPnHetoPio3M-92Lfquoxq4QIrLCt2XlOOpYYDChQtcbPqiGupLw',
    traits: ['Intuitive', 'Determined', 'Vulnerable', 'Brilliant scholar'],
    facts: [
      { id: 'ev-f1', text: 'Discovered the precursor Aetheric patterns in the Old Citadel libraries.', source: 'Ch. 1', type: 'extracted' },
      { id: 'ev-f2', text: 'Stole the Aetheric Compass from her former supervisor before fleeing.', source: 'Ch. 2', type: 'extracted' },
      { id: 'ev-f3', text: 'Suffers from recurrent sleepwalking during high solar flares.', source: 'Manual entry', type: 'manual' }
    ],
    relationships: [
      { targetId: 'kaelen', targetName: 'Kaelen', targetType: 'character', relation: 'Former Mentor' },
      { targetId: 'lyra', targetName: 'Lyra', targetType: 'character', relation: 'Handler / Trusted Ally' },
      { targetId: 'sunken-city', targetName: 'The Sunken City', targetType: 'location', relation: 'Birthplace' }
    ],
    appearances: ['ch1', 'ch2', 'ch3', 'ch4']
  },
  {
    id: 'ethan-vance',
    name: 'Ethan Vance',
    type: 'character',
    subtype: 'Protagonist',
    alias: 'Wraith',
    description: 'Elara\'s elder brother and tactical partner. A former vanguard soldier who provides security and streetwise pragmatism during expeditions.',
    image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCoFjO1n97YH2VMGTmFFSWuer65vFN0ios4JWMCJLNrREpa2pHl_5KU0kBZKE3HvFL0y90WLLdMWCLQrTx9Q6YaxZdCwRLd_cYUvwgWIrUbNRQcTRp1SM0jlyKEOBXwbfE_4DgYD5KVumAxemw3Wmc8UPl5OzgxmvZFwcGHYBCxzI0OSUY9eNxeHLO723TuPfZbbw9lKSQMtDLJfuZ0o0s4po__Ev94SRfPXtr4i1cVQeqb6ZoTYhzagQ',
    traits: ['Pragmatic', 'Cynical', 'Loyal to a fault', 'Tactical specialist'],
    facts: [
      { id: 'eth-f1', text: 'Former operative for the Syndicate\'s Deep Void division.', source: 'Ch. 1', type: 'extracted' },
      { id: 'eth-f2', text: 'Requires neural stabilizers due to prolonged exposure to raw tachyon fields.', source: 'Manual entry', type: 'manual' }
    ],
    relationships: [
      { targetId: 'elara-vance', targetName: 'Elara Vance', targetType: 'character', relation: 'Sibling / Protector' },
      { targetId: 'lyra', targetName: 'Lyra', targetType: 'character', relation: 'Handler' },
      { targetId: 'obsidian-syndicate', targetName: 'The Obsidian Syndicate', targetType: 'character', relation: 'Antagonist Org', isNegative: true }
    ],
    appearances: ['ch1', 'ch4']
  },
  {
    id: 'lyra',
    name: 'Lyra',
    type: 'character',
    subtype: 'Ally',
    alias: 'Comms',
    description: 'A brilliant network handler operating from the upper tiers of the capital. She coordinates the Vance siblings\' expeditions and maintains their technological gear.',
    traits: ['Analytical', 'Supportive', 'Secretive'],
    facts: [
      { id: 'ly-f1', text: 'Maintains a hidden relay node in the Ventilation Shaft 14.', source: 'Ch. 2', type: 'extracted' },
      { id: 'ly-f2', text: 'Secretly leaks Syndicate flight paths to the rebellion.', source: 'Manual entry', type: 'manual' }
    ],
    relationships: [
      { targetId: 'elara-vance', targetName: 'Elara Vance', targetType: 'character', relation: 'Technical Advisor' },
      { targetId: 'ethan-vance', targetName: 'Ethan Vance', targetType: 'character', relation: 'Comms Link' }
    ],
    appearances: ['ch2', 'ch4']
  },
  {
    id: 'kaelen',
    name: 'Kaelen',
    type: 'character',
    subtype: 'Mentor',
    alias: 'The Hermit',
    description: 'A legendary archivist who withdrew from the Citadel before the Severance. He lives in the damp depths of the Undercity, researching precursor keys.',
    traits: ['Stoic', 'Wise', 'Hermit'],
    facts: [
      { id: 'ka-f1', text: 'Lost his left eye during the Great Severance feedback loop.', source: 'Ch. 1', type: 'extracted' },
      { id: 'ka-f2', text: 'Lives in the sub-vaults of the Undercity Archives.', source: 'Ch. 2', type: 'extracted' }
    ],
    relationships: [
      { targetId: 'elara-vance', targetName: 'Elara Vance', targetType: 'character', relation: 'Former Mentor' },
      { targetId: 'undercity-archives', targetName: 'Undercity Archives', targetType: 'location', relation: 'Resident' }
    ],
    appearances: ['ch2']
  },
  {
    id: 'valerius-thorne',
    name: 'Valerius Thorne',
    type: 'character',
    subtype: 'Antagonist',
    alias: 'The Broker',
    description: 'A ruthless corporate broker for the Obsidian Syndicate. He tracks down precursor artifacts in the Abyssal Sea to fuel industrial engines.',
    traits: ['Ambitious', 'Mercenary', 'Deceptive'],
    facts: [
      { id: 'vt-f1', text: 'Ordered the capture of Elara Vance and confiscation of her research notes.', source: 'Ch. 3', type: 'extracted' }
    ],
    relationships: [
      { targetId: 'obsidian-syndicate', targetName: 'The Obsidian Syndicate', targetType: 'character', relation: 'High-ranking Agent' },
      { targetId: 'elara-vance', targetName: 'Elara Vance', targetType: 'character', relation: 'Hunter / Prey', isNegative: true }
    ],
    appearances: ['ch3']
  },
  {
    id: 'obsidian-syndicate',
    name: 'The Obsidian Syndicate',
    type: 'character',
    subtype: 'Organization',
    description: 'A powerful industrial conglomerate dominating the lower tiers of the floating islands, extracting precursor energy cores by force.',
    traits: ['Authoritarian', 'Exploitative', 'Highly Technological'],
    facts: [
      { id: 'os-f1', text: 'Controls the steam-engine coal trade and precursor core distribution.', source: 'Ch. 1', type: 'extracted' }
    ],
    relationships: [
      { targetId: 'valerius-thorne', targetName: 'Valerius Thorne', targetType: 'character', relation: 'Employer' }
    ],
    appearances: ['ch1', 'ch3', 'ch4']
  },
  // Locations
  {
    id: 'sunken-city',
    name: 'The Sunken City',
    type: 'location',
    subtype: 'Ruins',
    description: 'The ancient capital of Oakhaven, flooded and submerged after the magical disaster. Only its tallest obsidian spires remain above the tides.',
    facts: [
      { id: 'sc-f1', text: 'Submerged under 50 fathoms of corrosive salt water.', source: 'Atlas', type: 'manual' }
    ],
    relationships: [
      { targetId: 'elara-vance', targetName: 'Elara Vance', targetType: 'character', relation: 'Birthplace' }
    ],
    appearances: ['ch1', 'ch3']
  },
  {
    id: 'undercity-archives',
    name: 'Undercity Archives',
    type: 'location',
    subtype: 'Citadel Deep',
    description: 'A dusty, subterranean labyrinth beneath the spires of Aethelgard. Holds rows of crystalline precursor memory matrices.',
    facts: [
      { id: 'ua-f1', text: 'Guarded by decaying mechanical sentinel drones.', source: 'Ch. 2', type: 'extracted' }
    ],
    relationships: [
      { targetId: 'kaelen', targetName: 'Kaelen', targetType: 'character', relation: 'Shelter' }
    ],
    appearances: ['ch2']
  },
  {
    id: 'ashen-wastes',
    name: 'The Ashen Wastes',
    type: 'location',
    subtype: 'Barrens',
    description: 'A barren, ash-choked plain extending from the crater of the Sundering. The atmosphere is filled with dangerous tachyon static.',
    facts: [
      { id: 'aw-f1', text: 'Atlas records the wastes bordering the Eastern Sea.', source: 'World Atlas', type: 'manual' }
    ],
    relationships: [],
    appearances: ['ch3', 'ch4']
  },
  // Objects
  {
    id: 'resonance-cipher',
    name: 'Resonance Cipher',
    type: 'object',
    subtype: 'Artifact',
    description: 'A glowing copper cylinder covered in mechanical concentric rings, used to decode data storage crystals from precursor vaults.',
    facts: [
      { id: 'rc-f1', text: 'Emits a low frequency tone when near active memory grids.', source: 'Ch. 2', type: 'extracted' }
    ],
    relationships: [
      { targetId: 'undercity-archives', targetName: 'Undercity Archives', targetType: 'location', relation: 'Hidden Location' }
    ],
    appearances: ['ch2']
  },
  {
    id: 'aetheric-compass',
    name: 'Aetheric Compass',
    type: 'object',
    subtype: 'Tool',
    description: 'A modified pocket compass that reacts to magnetic currents generated by precursor machinery rather than the world\'s poles.',
    facts: [
      { id: 'ac-f1', text: 'Created by Kaelen during his early tenure at the Citadel.', source: 'Ch. 1', type: 'extracted' }
    ],
    relationships: [
      { targetId: 'elara-vance', targetName: 'Elara Vance', targetType: 'character', relation: 'Carried By' }
    ],
    appearances: ['ch1', 'ch2']
  }
];

export const initialTimelineEvents: TimelineEvent[] = [
  {
    id: 'tle-1',
    year: 30,
    period: 'Age of Ash',
    title: 'The Great Severance',
    description: 'The global core network destabilized, fracturing the land into floating archipelagos and creating the Abyssal Sea below.',
    stateChanges: [
      { entityId: 'sunken-city', entityName: 'Oakhaven Territory', entityType: 'location', field: 'State', before: 'Flourishing Kingdom', after: 'Flooded Ruins' }
    ],
    chapters: [{ id: 'ch1', name: 'Chapter 1: The Awakening' }]
  },
  {
    id: 'tle-2',
    year: 42,
    period: 'Age of Ash',
    title: 'The Sundering of Oakhaven',
    description: 'A catastrophic magical feedback loop detonated the core power grid, converting fertile forests into the ash-covered deadlands.',
    stateChanges: [
      { entityId: 'ashen-wastes', entityName: 'Oakhaven Territory', entityType: 'location', field: 'Control', before: 'House Vance', after: 'Contested Wastes' }
    ],
    chapters: [{ id: 'ch3', name: 'Chapter 3: Echoes of the Precursors' }]
  },
  {
    id: 'tle-3',
    year: 45,
    period: 'Age of Ash',
    title: 'Elara\'s Departure',
    description: 'Fleeing the newly formed Ashen Wastes following a close call with Syndicate scouts, Elara journeys south towards the Undercity.',
    stateChanges: [
      { entityId: 'elara-vance', entityName: 'Elara Vance', entityType: 'character', field: 'Status', before: 'Safe / Noble', after: 'Exile / Hunted' }
    ],
    chapters: [{ id: 'ch4', name: 'Chapter 4: The Fractal Key' }]
  },
  {
    id: 'tle-4',
    year: 47,
    period: 'Age of Ash',
    title: 'The Council of Three',
    description: 'The three largest merchant factions of the floating islands establish a fragile truce to coordinate the recovery of precursor fuel cells.',
    stateChanges: [
      { entityId: 'obsidian-syndicate', entityName: 'The Obsidian Syndicate', entityType: 'character', field: 'Influence', before: 'Regional Syndicate', after: 'Global Cartel' }
    ],
    chapters: []
  }
];

export const initialContradictions: Contradiction[] = [
  {
    id: 'con-1',
    title: 'Elara Vance Age Discrepancy',
    category: 'Character History',
    targetEntityId: 'elara-vance',
    severity: 'high',
    summary: 'A temporal mismatch in the character\'s age progression between chapters.',
    resolved: false,
    sources: [
      {
        sourceName: 'Chapter 3',
        text: 'Elara celebrated her 32nd birthday beneath the spires of Aethelgard.',
        highlightedWord: '32nd'
      },
      {
        sourceName: 'Chapter 12',
        text: 'Now, at 34 years of age, she recounted the events of three years prior.',
        highlightedWord: '34'
      }
    ]
  },
  {
    id: 'con-2',
    title: 'The Ashen Wastes Location Geographics',
    category: 'Location Geography',
    targetEntityId: 'ashen-wastes',
    severity: 'medium',
    summary: 'Conflicting cardinal directions recorded between travel logs and maps.',
    resolved: false,
    sources: [
      {
        sourceName: 'World Atlas',
        text: 'Described as bordering the Eastern Sea.',
        highlightedWord: 'Eastern Sea'
      },
      {
        sourceName: 'Prologue',
        text: 'Travellers journeyed Westward from the Wastes to reach the ocean.',
        highlightedWord: 'Westward'
      }
    ]
  }
];

export const demoManuscripts: Manuscript[] = [
  {
    id: 'ms-1',
    title: 'The Ash Chronicles',
    chapters: [
      {
        id: 'ch1',
        number: 1,
        title: 'The Awakening',
        content: 'The air in the lower levels tasted of dust and static electricity. Elara Vance adjusted her rebreather, the soft hum of its filtration unit the only sound cutting through the oppressive silence of the Undercity Archives. She held the Aetheric Compass high, its pale beam cutting swathes through the gloom, illuminating rows of crystalline storage matrices that stretched into the abyss.',
        wordCount: 1200
      },
      {
        id: 'ch2',
        number: 2,
        title: 'Descent into the Archives',
        content: 'The air in the lower levels tasted of dust and static electricity. Kaelen adjusted his rebreather, the soft hum of its filtration unit the only sound cutting through the oppressive silence of the Undercity Archives. He held the luminator high, its pale beam cutting swathes through the gloom, illuminating rows of crystalline storage matrices that stretched into the abyss. "Any signal yet?" asked Lyra, her voice crackling over the comms link. She was stationed three levels above, monitoring structural integrity. "Negative. The interference is getting stronger the deeper I go. It\'s like the walls themselves are absorbing the telemetry." Kaelen paused, running a gloved hand along a shattered interface console. He needed to find the Resonance Cipher before the automated defense grids initiated their next cycle.',
        wordCount: 2400
      },
      {
        id: 'ch3',
        number: 3,
        title: 'Echoes of the Precursors',
        content: 'Travel logs from the Ashen Wastes showed that travelers journeyed Westward to reach the shore. Elara Vance celebrated her 32nd birthday beneath the spires of Aethelgard. She looked at her notes, remembering Oakhaven before the flood. She knew Valerius Thorne was tracking her. The Obsidian Syndicate would stop at nothing to recover the cores. "We must head East," she said, looking at the compass.',
        wordCount: 1800
      },
      {
        id: 'ch4',
        number: 4,
        title: 'The Descent',
        content: 'Ethan Vance hesitated at the edge of the chasm. The air was thick with the scent of ozone and crushed stone, a stark contrast to the sterile environment of the upper levels. He adjusted the straps of his pack, the weight a constant reminder of the supplies he\'d secured—or stolen. "We don\'t have all day," Lyra\'s voice crackled through the comms. "The perimeter sensors are already resetting." He knew she was right. The Syndicate wouldn\'t wait. Taking a deep breath, he stepped into the void, the familiar hum of the repulsor boots kicking in just before he hit terminal velocity.',
        wordCount: 1950
      }
    ]
  },
  {
    id: 'ms-2',
    title: 'The Obsidian Accord',
    chapters: [
      {
        id: 'ch2-1',
        number: 1,
        title: 'The Tunnels of Steel',
        content: 'Valerius Thorne surveyed the excavation chamber. Giant steam cylinders hissed, venting white clouds into the dark concrete cavern. The miners worked in silhouetted rows, chipping away at the black obsidian shell surrounding the core. "Sir," the lieutenant approached, "we\'ve found another chamber. Crystalline matrices, similar to the ones in the Undercity Archives. But these are glowing."',
        wordCount: 1540
      }
    ]
  }
];
