---
name: debate-storyboard
alias: gerador_storyboard_debate
description: Generates high-fidelity television debate storyboards and media training scripts in HTML and A4 PDF, featuring studio broadcast split-monitors, stage direction cues, and color-coded rebuttal dialogues.
tags: [storyboard, debate, media-training, pdf, html, print, broadcast, tv-direction]
triggers: ["cria um storyboard", "gerar storyboard", "storyboard do debate", "novo storyboard", "storyboard em pdf", "fazer outro storyboard", "gerar storyboard pdf", "mesmo estilo de storyboard"]
---

# Purpose

Use this skill whenever requested to transform a political debate transcript, media training script, or confrontation rehearsal into an executive, television-style **Storyboard in HTML and A4 PDF**.

The resulting document reconstructs debate interactions scene by scene as an audiovisual studio transmission, featuring:
- An executive presidential cover with separated broadcast studio monitors and confrontation badges.
- Exactly **one scene per A4 page** with strict page-break guarantees.
- A **two-row broadcast layout**:
  - **Upper Row (Blue):** Opponent or mediator question/attack with studio camera monitor (CAM 02) and styled dialogue box.
  - **Camera Cut Strip:** High-contrast transmission cut indicator (`⚡ CORTE DE TRANSMISSÃO ➔ CÂMERA 1 • LULA`).
  - **Lower Row (Red):** Presidential rebuttal (CAM 01 [AO VIVO]) with stage direction cues, presidential typography (Newsreader 11pt), and tactical objective breakdown.

## Language Boundary (Mandatory)

Instructions in this skill definition are written in English for agent instruction compliance. However, all generated user-facing outputs, HTML markup text, dialogues, summaries, and Portuguese domain code comments MUST remain strictly in Brazilian Portuguese (`pt-BR`) with correct UTF-8 diacritics.

---

# Prerequisites

1. **Python Environment:**
   - Standard library (`os`, `re`, `base64`, `pathlib`).
   - `Pillow` for image cropping and aspect ratio normalization:
     ```powershell
     pip install pillow pypdf
     ```
2. **Headless Browser for A4 PDF Printing:**
   - Microsoft Edge or Google Chrome available on the system:
     - Windows Edge default: `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
3. **Source Material:**
   - Markdown script containing structured scenes with Title, TC (timecode), Block, Opponent attack, Lula response, Stage direction (`*(cenas de palco)*`), and Tactical takeaway.
   - High-resolution portraits of the participants.

---

# Design System & Visual Specification

### 1. Page Geometry & Print Constraints
- **Format:** A4 Portrait.
- **Page Margin:** `@page { size: A4 portrait; margin: 7mm 9mm 7mm 9mm; }`
- **Page Container:**
  ```css
  .page-container {
    width: 210mm;
    height: 283mm;
    max-height: 283mm;
    margin: 0 auto;
    page-break-after: always;
    break-after: page;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 6mm 8mm;
  }
  ```
- **Rule of Strict 1 Scene = 1 Page:** Never allow content to spill over to an accidental blank or partial page.

### 2. Curated Typography
- **Headings & Badges:** `'Cinzel', serif` (uppercase, presidential elegance, weight 700/800).
- **Oral Dialogue & Rebuttal:** `'Newsreader', Georgia, serif` (optical size 6..72, weight 400/600, font-size 11pt, line-height 1.45, italic quotes for oral cadences).
- **Interface & Stage Directions:** `'Plus Jakarta Sans', sans-serif` (weight 500/600/700).
- **Technical Metrics & Cameras:** `'JetBrains Mono', monospace` (weight 500/700).

### 3. Color Harmony & Identity
- **Opponent / Mediator (Blue Palette):**
  - Accent / Border: `#1d4ed8` (primary), `#2563eb` (light).
  - Background: `#f0f7ff` (subtle ice blue).
  - Topbar Dot / Indicator: `#3b82f6`.
- **Lula Presidential (Red Palette):**
  - Accent / Border: `#dc2626` (primary), `#ef4444` (light).
  - Background: `#ffffff` (crisp white card with red left border) and `#fff5f5` (accents).
  - Topbar Dot / Indicator: `#ef4444` (REC indicator).
- **Institutional Framing (Navy & Gold):**
  - Navy: `#0c2340` (borders, display titles, seal text).
  - Gold: `#b45309` / `#d97706` / `#fbbf24` (subtitles, VS badge, timecodes).

---

# Layout Architecture

## 1. Cover Page (`.cover-page`)
The cover sets the executive tone:
1. **Header:** Top seal (`CONFIDENCIAL • MEDIA TRAINING DE PALCO • ELEIÇÕES 2026`) and debate network tag.
2. **Main Titles:** Cinzel title `STORYBOARD DO DEBATE`, subtitle in Newsreader italic, and explanatory synopsis.
3. **Dual-Monitor Confrontation Graphic (`.cover-duel-container`):**
   - **Crucial Rule:** Never glue the candidates side-by-side into a single split screen without spacing.
   - Use two separate broadcast monitors:
     - Left: Opponent monitor (Blue border `#2563eb`, topbar `CAM 02 • FLÁVIO`, lower-third chyron).
     - Center: Circular `VS` badge (Navy/gold gradient, 44px circle, with `CONFRONTO DIRETO` and `BANCO DE TEMPO LIVRE` labels, `gap: 36px`).
     - Right: Lula monitor (Red border `#dc2626`, topbar `CAM 01 • LULA`, lower-third chyron).
   - **Aspect Ratio & Height:** The monitor screens MUST have `height: 225px !important; width: 195px;` and use portrait images cropped to aspect ratio ~0.85 (330x390) with headroom above the hair to ensure faces, ties, and sashes are fully visible without chin or forehead cutoff.
4. **Stats Grid (4 Metrics):** 20 Cenas, 3 Blocos, 100% Oral, 43 Fatos Desmontados.
5. **Strategic Pillars Box:** 2x2 grid highlighting media training techniques.
6. **Footer:** Confidential preparation label and page 01 of N.

## 2. Scene Pages (`.scene-page`)
Each scene represents one complete TV round:
1. **Scene Header:**
   - Badges: `CENA XX / 20`, `BLOCO X`, `⏱ TC 00:00`.
   - Framing tag: `SPLIT-SCREEN & CLOSE-UP` or `PLANO DE BANCADA & CLOSE-UP`.
   - Title: Cinzel bold headline.
2. **Row 1 — O Questionamento / Ataque (Azul):**
   - **Left Column (`.monitor-column`, width 130px):**
     - Compact broadcast monitor (width 130px, height 140px).
     - Topbar with blue dot, REC timecode, and `CAM 02 • OPONENTE`.
     - Lower Third GC (Blue gradient with opponent's name and role).
   - **Right Column (`.speech-column`):**
     - Blue Speech Box with `#2563eb` 5px left border, `#f0f7ff` background.
     - Header with speaker icon and badge `O QUESTIONAMENTO / ATAQUE NA TV`.
     - Attack text with bold timestamps and moment indicators (`⏱ 1º Momento [15:34] — A Fuga`).
3. **Camera Cut Divider (`.camera-cut-divider`):**
   - Horizontal rule with central badge: `⚡ CORTE DE TRANSMISSÃO ➔ CÂMERA 1 • LULA [CLOSE-UP FRONTAL]`.
4. **Row 2 — A Resposta Presidencial (Vermelho):**
   - **Left Column (`.monitor-column`, width 130px):**
     - Compact broadcast monitor (width 130px, height 140px, red border `#dc2626`).
     - Topbar with blinking red dot, REC timecode, and `CAM 01 • LULA [AO VIVO]`.
     - Lower Third GC (Red gradient, `LUIZ INÁCIO LULA DA SILVA / PRESIDENTE DA REPÚBLICA`).
     - **Stage Direction Card (`.stage-direction-card`):** Dark slate card with `🎬 DIREÇÃO DE PALCO` and posture/gaze instructions.
   - **Right Column (`.speech-column`):**
     - Red Speech Box with `#dc2626` 5px left border, pure white background.
     - Header: `🗣️ LUIZ INÁCIO LULA DA SILVA (PRESIDENTE)` and `RESPOSTA RECOMENDADA • ⏱ DURAÇÃO`.
     - Speech content: Newsreader 11pt, line-height 1.45.
     - Screenplay parentheticals formatted as:
       ```html
       <div class="screenplay-parenthetical">🎬 <em>(Interrompendo a manobra e olhando firme nos olhos do adversário)</em></div>
       ```
     - **Tactical Takeaway Box (`.tactical-takeaway-box`):** Gold-accented box with `🎯 OBJETIVO TÁTICO & PONTOS DESMONTADOS`.
5. **Scene Footer:**
   - Pagination: `PÁGINA XX DE 21`.

---

# Execution Workflow

### Step 1: Parse and Normalize the Debate Script
Extract each scene using a Python parser (such as [scripts/generate_storyboard.py](scripts/generate_storyboard.py)):
1. Split by scene headers (`### Cena XX:`).
2. Extract Timecode, Block, Opponent name, and Title.
3. Parse attacks, including sub-moments:
   - Convert `- **1º Momento de Flávio [[15:34] — A Fuga]:` to clean HTML `⏱ <strong>1º Momento de Flávio [15:34] — A Fuga:</strong>`.
4. Parse Lula's responses:
   - Detect stage directions in parentheses (`*(...)*`) and wrap them in `<div class="screenplay-parenthetical">🎬 <em>(...)</em></div>`.
   - Preserve paragraphs as `<p class="speech-p">`.
5. Extract stage directions and tactical objectives.
6. Calculate response text length and assign overflow mitigation classes:
   - If length > 2000 chars: add class `is-very-long` (reduces font to 9pt, line-height 1.32, tighter padding).
   - If length > 1400 chars: add class `is-long` (reduces font to 9.8pt, line-height 1.36).

### Step 2: Prepare & Crop Participant Images
1. Use PIL / Pillow to crop high-resolution photos into consistent portrait proportions:
   - Headroom above the hair must be at least 15–20% of the crop height.
   - For Scene Monitors (130px width): 320x360 px (aspect ratio 8:9).
   - For Cover Monitors (195px width): 330x390 px (aspect ratio 0.85).
2. Convert images to Base64 data URIs (`data:image/jpeg;base64,...`) so the generated HTML is 100% self-contained and portable.

### Step 3: Generate the Standalone HTML
1. Combine the design system CSS and the scene loop into a single HTML file:
   - Output path convention: `roteiros_respostas/storyboard_debate_<identificador>.html`.
2. Inspect the HTML structure:
   - Ensure the cover container closes cleanly before `.scene-page`.
   - Verify all 20 scenes are rendered in sequential order.

### Step 4: Compile to A4 PDF via Headless Edge
Run the headless command using an isolated temporary profile to prevent Windows file-lock errors (`0x20` / Error 32):

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless `
  --disable-gpu `
  --user-data-dir="$env:TEMP\edge_temp_storyboard_build" `
  --print-to-pdf="C:\caminho\absoluto\storyboard_debate.pdf" `
  --no-pdf-header-footer `
  "C:\caminho\absoluto\storyboard_debate.html"
```

### Step 5: Verification & Quality Assurance
1. **Page Count Verification:**
   - Run Python with `pypdf` to assert: `Total Pages == 1 + Number of Scenes`.
   - If page count exceeds expected (e.g. 22 or 23 for 20 scenes), find which scene has overflow, apply `.is-long` or `.is-very-long`, and recompile.
2. **Visual Inspection:**
   - Capture a screenshot of Page 1 (Cover) and at least one heavy scene page (e.g., Scene 4 or 8) to verify that chins, foreheads, and speech boxes fit within page boundaries.

---

# Reusable Assets in this Skill

- [resources/storyboard_theme.css](resources/storyboard_theme.css): Standalone, modular CSS design system ready for inclusion.
- [scripts/generate_storyboard.py](scripts/generate_storyboard.py): End-to-end Python pipeline script for parsing markdown and compiling HTML/PDF.

---

# Rules and Constraints

1. **Candidate Separation on Cover:** Never place candidates touching shoulder-to-shoulder in a single split box. Always render two distinct broadcast monitors separated by the circular VS badge.
2. **Color Boundaries:** Strict blue styling for opponents/mediators and strict red styling for presidential responses.
3. **One Page Rule:** Each scene MUST fit on exactly one A4 page. Never allow an orphan cut or accidental second page.
4. **Verbatim Fidelity:** Preserve the political candidate's speech and user text without altering arguments or inventing statistics. Format oral rhythm, timestamps, and stage directions cleanly.
5. **Clean Exit:** Always remove temporary preview images or scratch profiles upon completion.
