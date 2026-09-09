You are implementing the frontend prototype for **World State Engine**, a creative worldbuilding and manuscript-consistency application for novelists.

This is currently a **frontend-only prototype**. There is no backend, database, API, LLM service, extraction pipeline, authentication service, or persistent storage.

The goal is to reproduce and make interactive the existing Stitch UI designs.

## SOURCE OF TRUTH

The project contains:

1. `design.md`
2. The exported Stitch UI reference files/screenshots
3. The existing project requirements discussed in the application context

Treat `design.md` as the authoritative design-system specification.

Treat the Stitch-generated screens as the authoritative visual reference for page layouts.

Do NOT redesign the product.

Do NOT invent a new visual style.

Do NOT replace the Stitch layouts with a generic SaaS dashboard.

The implementation should reproduce the visual language, layout, spacing, typography, hierarchy, and interaction patterns of the provided designs as closely as practical.

## PRODUCT MODEL

The application represents:

WORLD
  ├── MANUSCRIPTS
  │     ├── CHAPTERS
  │     └── CHAPTERS
  │
  └── WORLD KNOWLEDGE
        ├── Characters
        ├── Locations
        ├── Objects
        ├── Relationships
        ├── Events
        └── Facts

AI extraction helps the writer create this information from existing material, but the writer remains the authority.

Everything extracted by the system must be editable.

Writers must also be able to create world information manually.

For this prototype, simulate all backend behavior with local mock data and client-side state.

## TECHNOLOGY

Use:

- React
- TypeScript
- Vite
- Tailwind CSS
- Motion for React
- React Router
- Zustand
- Lucide React
- React Flow for the world graph

Use shadcn/ui only where useful as an unstyled/accessibility-oriented primitive.

Do not allow shadcn's default visual styling to override the provided Stitch design.

Do not install unnecessary libraries.

## DESIGN SYSTEM

Read `design.md` completely before implementation.

Important requirements include:

- Atmospheric Minimalist
- "The Archive at Night"
- deep Void Black / charcoal backgrounds
- Copper Glow accent
- Source Serif 4 for the World Layer
- Geist for the System Layer
- Space Grotesk for functional labels
- 64px navigation rail
- large central Stage
- approximately 320px contextual Wings
- 24–32px major spacing
- refined rounded shapes
- subtle borders
- tonal layering
- glassmorphism used carefully
- minimal shadows
- contextual right-side panels
- copper active states
- generous negative space

Use the exact color and typography tokens specified in `design.md` rather than approximating them.

Create these as reusable CSS/design tokens.

Do not scatter arbitrary colors throughout components.

## APPLICATION SHELL

Create one reusable application shell shared across all workspace pages.

The shell should contain:

### Left rail

Approximately 64px wide.

Primary navigation:

- Home
- Manuscripts
- World
- Graph
- Timeline

Settings should appear as a secondary control near the bottom.

Use thin-line icons.

Active navigation should use the Copper Glow treatment described in `design.md`.

### Stage

The large central workspace.

### Wings

Contextual panels approximately 320px wide that slide from the right when additional world information needs to be displayed.

Use the backdrop blur and subtle focus treatment specified in `design.md`.

## ROUTES

Create routes for the following screens:

- `/signin`
- `/worlds`
- `/worlds/new`
- `/worlds/:worldId/processing`
- `/worlds/:worldId`
- `/worlds/:worldId/manuscripts`
- `/worlds/:worldId/manuscripts/:manuscriptId`
- `/worlds/:worldId/world`
- `/worlds/:worldId/graph`
- `/worlds/:worldId/timeline`
- `/worlds/:worldId/contradictions`
- `/worlds/:worldId/assistant`

Entity details should preferably be implemented as a reusable contextual panel rather than a completely separate page.

## MOCK DATA

Create realistic mock data for one primary demo World.

Use a fictional world with:

- 2 manuscripts
- approximately 5–8 chapters
- 5–8 characters
- several locations
- several objects
- relationships between characters
- several events
- historical facts
- a few intentional contradictions

The data should be rich enough for the Graph, Timeline, Manuscript, Entity, and Contradiction screens to feel genuinely connected.

Keep mock data in dedicated TypeScript files.

Do not put large mock datasets directly inside page components.

## INTERACTION MODEL

The prototype must feel interactive rather than being a collection of static screenshots.

Examples:

Clicking a character:
→ opens the reusable Entity Detail panel.

Clicking a graph node:
→ opens the same Entity Detail panel.

Clicking a character mention in a manuscript:
→ opens the same Entity Detail panel.

Clicking a contradiction:
→ opens the relevant entity and source information.

Clicking a chapter:
→ changes the displayed manuscript/world state.

Moving through the timeline:
→ changes the visible world state.

Adding a character:
→ creates the character in local prototype state.

Editing a fact:
→ updates the local state.

Resolving a contradiction:
→ updates the contradiction state and animates the item out.

Navigation between screens must work.

## ANIMATION SYSTEM

Use **Motion for React**.

Create reusable animation primitives/variants instead of defining unrelated animation values in every component.

The animation philosophy is:

**quiet, spatial, tactile, editorial.**

Animations should make the interface feel alive without becoming flashy.

Use:

- 150–300ms for small interactions
- 250–450ms for larger panel transitions
- spring transitions where spatial movement benefits from them
- subtle opacity transitions
- small translate transitions
- layout animations when elements move
- hover/tap micro-interactions
- subtle scale changes
- backdrop transitions
- graph node emphasis
- timeline state transitions

Important interactions:

### Contextual panel

When opening an entity:

- panel slides from the right
- fades in
- backdrop blur increases subtly
- underlying workspace remains visible

### Navigation

Workspace transitions should use subtle fade/slide transitions.

Do not use dramatic page animations.

### Cards

Use subtle hover elevation/scale/opacity changes.

### Graph

Hovering a node should emphasize the node and its connected relationships while slightly reducing visual prominence of unrelated nodes.

Clicking a node opens the Entity panel.

### Timeline

Changing the selected chapter should transition world-state information instead of abruptly replacing it.

### Contradictions

When a contradiction is resolved:

- briefly highlight the resolution
- smoothly remove/reposition the item
- update the visible count

### Reduced motion

Respect `prefers-reduced-motion`.

Do not create animations that interfere with reading or writing.

## RESPONSIVENESS

The primary target is desktop/laptop because this is a writing workspace.

Prioritize approximately:

- 1440×900
- 1600×900
- 1920×1080

Do not sacrifice desktop fidelity to create a generic mobile layout.

However, the application should degrade gracefully on smaller screens.

## IMPLEMENTATION PROCESS

Do NOT implement all pages immediately.

First:

1. Read `design.md`.
2. Inspect the Stitch reference screens.
3. Identify duplicate screen variants.
4. Identify the canonical visual version of each screen.
5. Create the shared design tokens.
6. Create the typography system.
7. Create the application shell.
8. Create reusable UI primitives.
9. Create mock data and Zustand state.
10. Set up routing.
11. Build the first page.
12. Run the application.
13. Use browser inspection to compare the implementation against the Stitch reference.
14. Correct visual differences before proceeding.

Do not make large architectural changes without first checking whether the existing Stitch design already establishes the intended behavior.

The final prototype should feel like:

**a quiet, atmospheric creative workspace where a novelist can enter a fictional world, understand its structure, write within it, and explore how that world changes over time.**