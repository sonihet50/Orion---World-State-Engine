---
name: Orion Engine
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1c1b1d'
  surface-container: '#201f22'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#d7c2b8'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#313032'
  outline: '#9f8d84'
  outline-variant: '#52443c'
  surface-tint: '#feb68d'
  primary: '#feb68d'
  on-primary: '#502406'
  primary-container: '#cc8b65'
  on-primary-container: '#522608'
  inverse-primary: '#875130'
  secondary: '#c2c6d6'
  on-secondary: '#2b303c'
  secondary-container: '#424754'
  on-secondary-container: '#b0b5c4'
  tertiary: '#c8c6c5'
  on-tertiary: '#303030'
  tertiary-container: '#9b9999'
  on-tertiary-container: '#323131'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbc9'
  primary-fixed-dim: '#feb68d'
  on-primary-fixed: '#321200'
  on-primary-fixed-variant: '#6b3a1b'
  secondary-fixed: '#dee2f2'
  secondary-fixed-dim: '#c2c6d6'
  on-secondary-fixed: '#171b27'
  on-secondary-fixed-variant: '#424754'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1b1b1b'
  on-tertiary-fixed-variant: '#474746'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
  void-black: '#000000'
  starlight-white: '#FAFAFA'
  copper-glow: '#E6A27E'
  deep-charcoal: '#121212'
typography:
  display-lg:
    fontFamily: Source Serif 4
    fontSize: 48px
    fontWeight: '300'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Source Serif 4
    fontSize: 28px
    fontWeight: '400'
    lineHeight: 36px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  nav-rail-width: 64px
  side-panel-width: 320px
  gutter: 24px
  margin-safe: 40px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is centered on the concept of "The Archive at Night"—a sanctuary for creative world-building that prioritizes focus, atmosphere, and spatial continuity. The target audience consists of novelists and world-builders who require a high degree of organizational complexity without the mechanical coldness of traditional database software.

The aesthetic follows an **Atmospheric Minimalist** approach. It leverages deep, expansive backgrounds to create a sense of infinite digital space, punctuated by warm, ember-like accents that guide the eye to critical storytelling elements. The interface should feel like a physical desk in a dimly lit room, where only the active manuscript and its immediate references are illuminated.

Key principles:
- **Spatiality:** Use of depth and subtle lighting to imply a physical environment.
- **Restraint:** High-density information is tucked into contextual panels to keep the primary workspace "hushed."
- **Organic Precision:** A blend of sharp, modern UI mechanics with the warm, literary feel of classic typography.

## Colors

The palette is anchored by **Void Black** (#000000) and **Deep Charcoal**, creating a canvas that eliminates peripheral distractions. 

The primary accent, **Copper Glow**, is used sparingly for interactive states, progress indicators, and "active world" elements. Secondary and Tertiary colors are reserved for surface layering—using `#0A0F1A` for background depth and `#1D1D1D` for elevated panels. All "white" text should utilize the slightly softened `#FAFAFA` to reduce eye strain during long writing sessions. Use subtle gradients (Radial) originating from the cursor or active element to simulate ambient light falling on the workspace.

## Typography

This system employs a dual-personality typographic approach. 

**Source Serif 4** is used for the "World Layer"—titles, manuscript text, and lore descriptions—to evoke the feeling of a printed book. **Geist** provides a high-performance, technical contrast for the "System Layer"—navigation, input fields, and metadata. **Space Grotesk** is used exclusively for functional labels and micro-copy, providing a slight technical/futuristic edge that aligns with the "World State Engine" concept.

All serif headings should utilize generous line height and tight letter-spacing for a sophisticated, editorial appearance.

## Layout & Spacing

The layout is a **Spatial Fixed-Fluid Hybrid**. 

1.  **The Rail:** A persistent 64px left navigation rail houses the highest-level engine controls (World, Timeline, Manuscript, Settings).
2.  **The Stage:** A large, central workspace for writing and visualization.
3.  **The Wings:** Contextual side panels (320px) that slide in from the right to provide world-building data without obscuring the stage.

Use a 4px base grid. Spacing between major panels should be wide (24px - 32px) to allow the background "void" to act as a separator, reinforcing the feeling of floating workspace modules.

## Elevation & Depth

Depth is achieved through **Tonal Layering and Glassmorphism** rather than traditional drop shadows.

- **Level 0 (The Void):** `#000000` - The base background.
- **Level 1 (The Stage):** `#09090B` - The primary workspace area.
- **Level 2 (Floating Panels):** `#1D1D1D` with a subtle `1px` solid border of `#FAFAFA` at 10% opacity.
- **Interactive States:** Use a soft, 40px blur radial gradient behind active cards using the Primary Copper color at 5% opacity to create a "glow" effect.

Avoid heavy shadows. Use "inner-glow" borders (0.5px) to define edges against the black background.

## Shapes

The design system uses a **Refined Rounded** language (0.5rem base). 

This softening of the UI helps the technical engine feel more approachable and "human." Large cards and central workspace containers should utilize `rounded-xl` (1.5rem) to create a "nested" or "pulpit" feel. Small UI elements like inputs and buttons remain at the base `rounded` level for a crisp, functional look.

## Components

### Buttons
Primary buttons use a ghost-style with a thin Copper border and Copper text. On hover, they transition to a solid Copper background with Void Black text. Secondary buttons are entirely borderless, using only text with a slight increase in opacity on hover.

### Panels & Cards
Cards are the primary container for lore entries. They should feature a "glass" header—a slightly lighter background with a 1px bottom border. Content inside cards uses the Serif font for titles and Geist for details.

### Navigation Rail
Icons should be thin-line (0.5pt to 1pt weight). The active state is indicated by a vertical 2px Copper line on the far left and a subtle Copper glow behind the icon.

### Contextual Side Panels
These should slide from the right, utilizing a heavy backdrop blur (20px) to partially obscure the workspace, creating a focus on the metadata being edited.

### Input Fields
Minimalist underline-only or low-contrast bordered boxes. Focus states should gently animate the border color from charcoal to copper.