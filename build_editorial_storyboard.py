import os
import re
import base64
from parse_scenes import parse_all_scenes, format_speech_html, get_base64_image

def generate_refined_storyboard():
    scenes = parse_all_scenes()
    print(f"Loaded {len(scenes)} scenes.")

    # Base64 compact cropped images
    b64_lula = get_base64_image("assets/images/crop_lula.jpg")
    b64_flavio = get_base64_image("assets/images/crop_flavio.jpg")
    b64_adriana = get_base64_image("assets/images/crop_adriana.jpg")
    b64_oinegue = get_base64_image("assets/images/crop_oinegue.jpg")
    b64_split = get_base64_image("assets/images/studio_split_screen.jpg")
    b64_lula_cover = get_base64_image("assets/images/crop_lula_cover.jpg")
    b64_flavio_cover = get_base64_image("assets/images/crop_flavio_cover.jpg")

    b64_map = {
        "lula": b64_lula,
        "flavio": b64_flavio,
        "adriana": b64_adriana,
        "oinegue": b64_oinegue,
        "split": b64_split
    }

    css_content = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    :root {
      --font-serif: 'Newsreader', Georgia, serif;
      --font-display: 'Cinzel', serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

      --blue-opp: #1d4ed8;
      --blue-opp-light: #2563eb;
      --blue-opp-bg: #f0f7ff;
      --blue-opp-border: #93c5fd;

      --red-lula: #dc2626;
      --red-lula-light: #ef4444;
      --red-lula-bg: #fff5f5;
      --red-lula-border: #fca5a5;

      --navy-presidential: #0c2340;
      --gold-accent: #b45309;
      --gold-light: #d97706;
      --slate-dark: #0f172a;
      --slate-body: #1e293b;
      --slate-muted: #475569;
      --border-light: #e2e8f0;
      --bg-page: #ffffff;
      --bg-subtle: #f8fafc;
    }

    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    @page {
      size: A4 portrait;
      margin: 7mm 9mm 7mm 9mm;
    }

    body {
      margin: 0;
      padding: 0;
      font-family: var(--font-sans);
      background-color: #cbd5e1;
      color: var(--slate-body);
      -webkit-font-smoothing: antialiased;
    }

    /* Page container */
    .page-container {
      width: 210mm;
      height: 283mm;
      max-height: 283mm;
      margin: 0 auto;
      background-color: var(--bg-page);
      page-break-after: always;
      break-after: page;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 6mm 8mm;
    }

    @media screen {
      .page-container {
        margin: 25px auto;
        box-shadow: 0 12px 36px rgba(0,0,0,0.18);
        border-radius: 4px;
      }
    }

    @media print {
      body {
        background: transparent;
      }
      .page-container {
        margin: 0;
        box-shadow: none;
        border-radius: 0;
        padding: 0;
        width: 100%;
        height: 283mm;
      }
    }

    /* =========================================
       COVER PAGE STYLES
       ========================================= */
    .cover-page {
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
      border: 3px double #0c2340;
      outline: 1px solid #d97706;
      outline-offset: -8px;
      padding: 12mm 12mm 8mm 12mm;
      justify-content: space-between;
    }

    .cover-top-badge {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #0c2340;
      padding-bottom: 5px;
    }

    .cover-seal {
      font-family: var(--font-mono);
      font-size: 8.5px;
      font-weight: 700;
      letter-spacing: 1.5px;
      color: var(--gold-accent);
      text-transform: uppercase;
    }

    .cover-band-tag {
      font-family: var(--font-mono);
      font-size: 8.5px;
      font-weight: 700;
      letter-spacing: 1px;
      color: var(--red-lula);
      text-transform: uppercase;
    }

    .cover-main-header {
      text-align: center;
      margin: 12px 0 8px 0;
    }

    .cover-pretitle {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      color: var(--gold-light);
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .cover-title {
      font-family: var(--font-display);
      font-size: 30px;
      font-weight: 800;
      color: var(--navy-presidential);
      letter-spacing: 0.5px;
      line-height: 1.15;
      margin: 0 0 5px 0;
    }

    .cover-subtitle {
      font-family: var(--font-serif);
      font-size: 16px;
      font-weight: 600;
      font-style: italic;
      color: var(--red-lula);
      margin: 0 0 10px 0;
    }

    .cover-desc {
      font-family: var(--font-sans);
      font-size: 9.5px;
      line-height: 1.45;
      color: var(--slate-muted);
      max-width: 580px;
      margin: 0 auto;
    }

    .cover-duel-container {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 36px;
      margin: 14px auto 10px auto;
      max-width: 580px;
    }

    .cover-monitor {
      width: 195px;
      min-width: 195px;
      border-radius: 7px;
      overflow: hidden;
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
    }

    .cover-monitor .cover-screen,
    .cover-screen {
      width: 100%;
      height: 225px !important;
      position: relative;
      background: #000;
      overflow: hidden;
    }

    .cover-screen img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .cover-vs-badge-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 4px;
    }

    .cover-vs-circle {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0c2340 0%, #1e3a8a 100%);
      border: 2px solid #d97706;
      color: #fbbf24;
      font-family: var(--font-display);
      font-size: 17px;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(12, 35, 64, 0.3);
    }

    .cover-vs-label {
      font-family: var(--font-mono);
      font-size: 8px;
      font-weight: 700;
      color: var(--navy-presidential);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-top: 2px;
    }

    .cover-vs-sub {
      font-family: var(--font-mono);
      font-size: 7px;
      color: var(--gold-accent);
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    .cover-stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin: 8px 0;
    }

    .cover-stat-card {
      background: #ffffff;
      border: 1px solid var(--border-light);
      border-top: 3px solid var(--navy-presidential);
      border-radius: 6px;
      padding: 7px 5px;
      text-align: center;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .stat-number {
      font-family: var(--font-display);
      font-size: 15px;
      font-weight: 700;
      color: var(--navy-presidential);
      margin-bottom: 2px;
    }

    .stat-label {
      font-family: var(--font-mono);
      font-size: 7.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--gold-accent);
    }

    .cover-pillars-box {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 9px 12px;
      margin-top: 5px;
    }

    .pillars-title {
      font-family: var(--font-mono);
      font-size: 8px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--navy-presidential);
      margin-bottom: 5px;
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .pillars-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .pillar-item {
      font-size: 8.5px;
      line-height: 1.35;
      color: var(--slate-body);
    }

    .pillar-item strong {
      color: var(--red-lula);
    }

    .cover-footer {
      border-top: 1px solid #cbd5e1;
      padding-top: 5px;
      display: flex;
      justify-content: space-between;
      font-family: var(--font-mono);
      font-size: 7.5px;
      color: var(--slate-muted);
    }

    /* =========================================
       SCENE PAGE HEADER
       ========================================= */
    .scene-header {
      border-bottom: 2px solid var(--navy-presidential);
      padding-bottom: 4px;
      margin-bottom: 6px;
    }

    .scene-meta-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2px;
    }

    .scene-badges {
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .scene-num-badge {
      background: var(--navy-presidential);
      color: #ffffff;
      font-family: var(--font-mono);
      font-size: 8.5px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 3px;
    }

    .scene-block-badge {
      background: #f1f5f9;
      color: var(--slate-dark);
      font-family: var(--font-mono);
      font-size: 8px;
      font-weight: 700;
      padding: 2px 5px;
      border: 1px solid #cbd5e1;
      border-radius: 3px;
    }

    .scene-tc-badge {
      font-family: var(--font-mono);
      font-size: 8px;
      font-weight: 700;
      color: var(--gold-accent);
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .scene-shot-type {
      font-family: var(--font-mono);
      font-size: 8px;
      font-weight: 700;
      color: var(--red-lula);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .scene-title {
      font-family: var(--font-display);
      font-size: 13px;
      font-weight: 700;
      color: var(--navy-presidential);
      line-height: 1.2;
      margin: 0;
    }

    /* =========================================
       TWO HORIZONTAL INTERACTION ROWS
       ========================================= */
    .dialogue-row {
      display: flex;
      gap: 10px;
      align-items: stretch;
      margin-bottom: 6px;
    }



    .row-lula {
      /* Lower row */
      overflow: hidden;
      margin-bottom: 4px;
    }

    /* COMPACT BROADCAST MONITOR */
    .monitor-column {
      width: 130px;
      min-width: 130px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .broadcast-monitor {
      background: #090d16;
      border-radius: 6px;
      overflow: hidden;
      box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
      position: relative;
    }

    .monitor-blue {
      border: 2.5px solid var(--blue-opp);
      box-shadow: 0 3px 12px rgba(29, 78, 216, 0.22);
    }

    .monitor-red {
      border: 2.5px solid var(--red-lula);
      box-shadow: 0 3px 12px rgba(220, 38, 38, 0.22);
    }

    .monitor-topbar {
      background: #0f172a;
      padding: 2px 5px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--font-mono);
      font-size: 7px;
      color: #94a3b8;
      border-bottom: 1px solid #1e293b;
    }

    .dot-blue {
      width: 5px;
      height: 5px;
      background-color: #3b82f6;
      border-radius: 50%;
      display: inline-block;
    }

    .dot-red {
      width: 5px;
      height: 5px;
      background-color: #ef4444;
      border-radius: 50%;
      display: inline-block;
    }

    .monitor-screen {
      position: relative;
      width: 100%;
      height: 140px;
      background: #000;
      overflow: hidden;
    }

    .monitor-screen img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    /* Lower Third GC */
    .lower-third-gc {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 3px 5px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .gc-blue {
      background: linear-gradient(90deg, rgba(29,78,216,0.95) 0%, rgba(12,35,64,0.92) 100%);
      border-top: 1.5px solid #60a5fa;
    }

    .gc-red {
      background: linear-gradient(90deg, rgba(220,38,38,0.95) 0%, rgba(12,35,64,0.92) 100%);
      border-top: 1.5px solid #f87171;
    }

    .gc-name {
      font-family: var(--font-sans);
      font-size: 8px;
      font-weight: 800;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      line-height: 1.1;
    }

    .gc-role {
      font-family: var(--font-sans);
      font-size: 6.8px;
      color: #e2e8f0;
      line-height: 1.1;
    }

    /* STAGE DIRECTION CARD (Below Lula's Monitor) */
    .stage-direction-card {
      background-color: #fffbeb;
      border: 1px solid #fde68a;
      border-left: 3px solid var(--gold-accent);
      border-radius: 4px;
      padding: 4px 6px;
      font-size: 7.8px;
      line-height: 1.35;
      color: #78350f;
    }

    .stage-direction-title {
      font-family: var(--font-mono);
      font-size: 7px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--gold-accent);
      margin-bottom: 2px;
      display: flex;
      align-items: center;
      gap: 3px;
    }

    /* SPEECH COLUMN */
    .speech-column {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* OPPONENT SPEECH BOX */
    .opponent-speech-box {
      background-color: var(--blue-opp-bg);
      border: 1.5px solid var(--blue-opp-border);
      border-left: 5px solid var(--blue-opp);
      border-radius: 6px;
      padding: 6px 9px;
      box-shadow: 0 1px 4px rgba(29, 78, 216, 0.05);
    }

    .speech-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 3px;
      padding-bottom: 2px;
    }

    .header-blue {
      border-bottom: 1px solid #bfdbfe;
    }

    .header-red {
      border-bottom: 1px solid #fecaca;
    }

    .speaker-badge-blue {
      font-family: var(--font-sans);
      font-size: 8px;
      font-weight: 800;
      color: var(--blue-opp);
      text-transform: uppercase;
      letter-spacing: 0.4px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .speaker-badge-red {
      font-family: var(--font-sans);
      font-size: 8.5px;
      font-weight: 800;
      color: var(--red-lula);
      text-transform: uppercase;
      letter-spacing: 0.4px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .speaker-type-tag {
      font-family: var(--font-mono);
      font-size: 7px;
      color: #64748b;
      font-weight: 600;
      text-transform: uppercase;
    }

    .opponent-content-text {
      font-size: 9.6pt;
      line-height: 1.42;
      color: #1e293b;
      font-style: italic;
    }

    .opponent-content-text p {
      margin: 0 0 3px 0;
    }

    .opponent-content-text p:last-child {
      margin-bottom: 0;
    }

    .opponent-content-text strong {
      font-weight: 700;
      font-style: normal;
      color: var(--navy-presidential);
    }

    .sub-moment-tag {
      font-family: var(--font-mono);
      font-size: 8px;
      font-weight: 700;
      color: #1e40af;
      background: #dbeafe;
      border: 1px solid #bfdbfe;
      border-radius: 3px;
      padding: 1.5px 5px;
      margin: 3px 0 2px 0;
      display: inline-block;
      font-style: normal;
    }

    /* CAMERA CUT DIVIDER */
    .camera-cut-divider {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 2px 0 5px 0;
    }

    .cut-line {
      flex: 1;
      height: 1px;
      background: #cbd5e1;
    }

    .cut-badge {
      background: #f1f5f9;
      border: 1px dashed #94a3b8;
      border-radius: 3px;
      padding: 2px 7px;
      font-family: var(--font-mono);
      font-size: 7.5px;
      font-weight: 700;
      color: var(--red-lula);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* LULA SPEECH BOX */
    .lula-speech-box {
      background-color: #ffffff;
      border: 1.5px solid var(--red-lula-border);
      border-left: 5px solid var(--red-lula);
      border-radius: 6px;
      padding: 7px 10px;
      box-shadow: 0 1px 4px rgba(220, 38, 38, 0.05);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      margin-bottom: 5px;
    }

    .lula-speech-content {
      font-family: var(--font-serif);
      font-size: 11pt;
      line-height: 1.5;
      color: #0f172a;
      overflow: hidden;
    }

    .lula-speech-content p {
      margin: 0 0 4.5px 0;
    }

    .lula-speech-content p:last-child {
      margin-bottom: 0;
    }

    .lula-speech-content strong {
      font-family: var(--font-sans);
      font-weight: 700;
      color: var(--navy-presidential);
    }

    .screenplay-parenthetical {
      font-family: var(--font-sans);
      font-size: 8px;
      font-weight: 600;
      color: var(--gold-accent);
      background: #fffbeb;
      border: 1px dashed #fde68a;
      border-radius: 4px;
      padding: 2px 5px;
      margin: 2.5px 0 3.5px 0;
      display: block;
    }

    /* DYNAMIC SCALING FOR LONG SCENES */
    .scene-page.is-long .lula-speech-content {
      font-size: 10pt;
      line-height: 1.42;
    }
    .scene-page.is-long .lula-speech-content p {
      margin-bottom: 3px;
    }

    .scene-page.is-very-long .lula-speech-content {
      font-size: 8.8pt;
      line-height: 1.35;
    }
    .scene-page.is-very-long .lula-speech-content p {
      margin-bottom: 2px;
    }
    .scene-page.is-very-long .opponent-content-text {
      font-size: 8.5pt;
      line-height: 1.3;
    }
    .scene-page.is-very-long .monitor-screen {
      height: 120px;
    }

    /* TACTICAL TAKEAWAY BOX (Below Lula Speech) */
    .tactical-takeaway-box {
      background-color: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-left: 3px solid #16a34a;
      border-radius: 4px;
      padding: 4px 8px;
      font-size: 8.2px;
      line-height: 1.32;
      color: #166534;
    }

    .tactical-title {
      font-family: var(--font-mono);
      font-size: 7.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #15803d;
      margin-bottom: 1.5px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    /* FOOTER */
    .scene-footer {
      border-top: 1px solid var(--border-light);
      padding-top: 3px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--font-mono);
      font-size: 7.5px;
      color: #94a3b8;
    }
    """

    # Build HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='pt-BR'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>Storyboard do Debate: Como Lula Deveria Ter Respondido (Band)</title>",
        f"<style>{css_content}</style>",
        "</head>",
        "<body>"
    ]

    # 1. COVER PAGE
    cover_html = f"""
    <div class="page-container cover-page">
      <div class="cover-top-badge">
        <span class="cover-seal">CONFIDENCIAL • MEDIA TRAINING DE PALCO • ELEIÇÕES 2026</span>
        <span class="cover-band-tag">REDE BANDEIRANTES • 1º DEBATE</span>
      </div>

      <div class="cover-main-header">
        <div class="cover-pretitle">ROTEIRO AUDIOVISUAL & DIREÇÃO DE TV</div>
        <h1 class="cover-title">STORYBOARD DO DEBATE</h1>
        <div class="cover-subtitle">Como Lula Deveria Ter Respondido no Debate da Band</div>
        <div class="cover-desc">
          Reconstituição cena a cena do confronto com Flávio Bolsonaro e as perguntas dos mediadores. 
          Cada interação foi estruturada em linguagem televisiva popular, com enquadramentos de estúdio, 
          direção cênica e contra-ataques fundamentados em fatos judiciais e compromissos concretos com o trabalhador.
        </div>
      </div>

      <div class="cover-duel-container">
        <!-- Monitor Flávio (Esquerda - Azul) -->
        <div class="broadcast-monitor monitor-blue cover-monitor">
          <div class="monitor-topbar">
            <span><span class="dot-blue"></span> REC 00:29:55</span>
            <span>CAM 02 • FLÁVIO</span>
          </div>
          <div class="monitor-screen cover-screen">
            <img src="{b64_flavio_cover}" alt="Flávio Bolsonaro">
            <div class="lower-third-gc gc-blue">
              <div class="gc-name">FLÁVIO BOLSONARO</div>
              <div class="gc-role">SENADOR DA REPÚBLICA / OPOSITOR</div>
            </div>
          </div>
        </div>

        <!-- Central VS Badge com amplo espaçamento -->
        <div class="cover-vs-badge-container">
          <div class="cover-vs-circle">VS</div>
          <div class="cover-vs-label">CONFRONTO DIRETO</div>
          <div class="cover-vs-sub">BANCO DE TEMPO LIVRE</div>
        </div>

        <!-- Monitor Lula (Direita - Vermelho) -->
        <div class="broadcast-monitor monitor-red cover-monitor">
          <div class="monitor-topbar">
            <span><span class="dot-red"></span> REC 00:29:55</span>
            <span>CAM 01 • LULA</span>
          </div>
          <div class="monitor-screen cover-screen">
            <img src="{b64_lula_cover}" alt="Lula Presidente">
            <div class="lower-third-gc gc-red">
              <div class="gc-name">LUIZ INÁCIO LULA DA SILVA</div>
              <div class="gc-role">PRESIDENTE DA REPÚBLICA</div>
            </div>
          </div>
        </div>
      </div>

      <div class="cover-stats-grid">
        <div class="cover-stat-card">
          <div class="stat-number">20 CENAS</div>
          <div class="stat-label">Confrontos Reconstituídos</div>
        </div>
        <div class="cover-stat-card">
          <div class="stat-number">3 BLOCOS</div>
          <div class="stat-label">Estrutura Integral Band</div>
        </div>
        <div class="cover-stat-card">
          <div class="stat-number">100% ORAL</div>
          <div class="stat-label">Linguagem Direta de TV</div>
        </div>
        <div class="cover-stat-card">
          <div class="stat-number">43 FATOS</div>
          <div class="stat-label">Narrativas Desmontadas</div>
        </div>
      </div>

      <div class="cover-pillars-box">
        <div class="pillars-title">🎯 PILARES ESTRATÉGICOS DE MEDIA TRAINING APLICADOS</div>
        <div class="pillars-grid">
          <div class="pillar-item">
            <strong>1. Desarme Imediato de Provocações:</strong> Não entrar em acusações abstratas; rebater no primeiro segundo com a loja de chocolates, Mansão do BRB e as 43 mentiras catalogadas.
          </div>
          <div class="pillar-item">
            <strong>2. Domínio Cênico & Expressão:</strong> Manter postura de autoridade de Estado, olhar direto nos olhos do adversário e transição para a câmera central sem demonstrar irritação.
          </div>
          <div class="pillar-item">
            <strong>3. Foco na Mesa do Trabalhador:</strong> Conectar cada tema (juros, segurança, 6x1) à vida real do eleitor, contrapondo propostas de futuro ao terrorismo da oposição.
          </div>
          <div class="pillar-item">
            <strong>4. O Contraste Histórico:</strong> Evidenciar a diferença entre quem tirou o Brasil da fome e quem votou contra a licença-maternidade e raspou a numeração de balas.
          </div>
        </div>
      </div>

      <div class="cover-footer">
        <span>DOCUMENTO DE USO INTERNO E EXCLUSIVO DE PREPARAÇÃO</span>
        <span>ASSESSORIA DE COMUNICAÇÃO ESTRATÉGICA</span>
        <span>PÁGINA 01 DE 21</span>
      </div>
    </div>
    """
    html_parts.append(cover_html)

    # 2. SCENE PAGES (Pages 2 to 21)
    for sc in scenes:
        idx = sc["index"]
        page_num = idx + 1
        opp_key = sc["opp_key"]
        opp_img = b64_map.get(opp_key, b64_flavio)
        shot_type = "SPLIT-SCREEN & CLOSE-UP" if sc["is_direct"] else "PLANO DE BANCADA & CLOSE-UP"

        # Determine long scenes
        resp_len = len(sc["lula_text"])
        long_class = ""
        if resp_len > 2000:
            long_class = "is-very-long"
        elif resp_len > 1400:
            long_class = "is-long"

        # Format Lula speech
        lula_html = format_speech_html(sc["lula_text"])

        scene_html = f"""
        <div class="page-container scene-page {long_class}">
          <!-- HEADER -->
          <div class="scene-header">
            <div class="scene-meta-row">
              <div class="scene-badges">
                <span class="scene-num-badge">CENA {idx:02d} / 20</span>
                <span class="scene-block-badge">{sc["block"]}</span>
                <span class="scene-tc-badge">⏱ TC {sc["tc"]}</span>
              </div>
              <span class="scene-shot-type">{shot_type}</span>
            </div>
            <h2 class="scene-title">{sc["title"]}</h2>
          </div>

          <!-- ROW 1: O QUESTIONAMENTO / ATAQUE (AZUL) -->
          <div class="dialogue-row row-opponent">
            <!-- Left: Opponent Monitor (BLUE BORDER) -->
            <div class="monitor-column">
              <div class="broadcast-monitor monitor-blue">
                <div class="monitor-topbar">
                  <span><span class="dot-blue"></span> REC {sc["tc"]}:00</span>
                  <span>CAM 02 • {sc["opp_name"].upper()}</span>
                </div>
                <div class="monitor-screen">
                  <img src="{opp_img}" alt="{sc["opp_name"]}">
                  <div class="lower-third-gc gc-blue">
                    <div class="gc-name">{sc["opp_name"]}</div>
                    <div class="gc-role">{sc["opp_role"]}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Opponent Speech Box (BLUE BORDER) -->
            <div class="speech-column">
              <div class="opponent-speech-box">
                <div class="speech-header-row header-blue">
                  <span class="speaker-badge-blue">🎙️ {sc["opp_name"].upper()}</span>
                  <span class="speaker-type-tag">O QUESTIONAMENTO / ATAQUE NA TV</span>
                </div>
                <div class="opponent-content-text">
                  {sc["clean_attack_html"]}
                </div>
              </div>
            </div>
          </div>

          <!-- CAMERA CUT DIVIDER -->
          <div class="camera-cut-divider">
            <span class="cut-line"></span>
            <span class="cut-badge">⚡ CORTE DE TRANSMISSÃO ➔ CÂMERA 1 • LULA [CLOSE-UP FRONTAL]</span>
            <span class="cut-line"></span>
          </div>

          <!-- ROW 2: A RESPOSTA PRESIDENCIAL (VERMELHO) -->
          <div class="dialogue-row row-lula">
            <!-- Left: Lula Monitor (RED BORDER) + Stage Direction -->
            <div class="monitor-column">
              <div class="broadcast-monitor monitor-red">
                <div class="monitor-topbar">
                  <span><span class="dot-red"></span> REC {sc["tc"]}:25</span>
                  <span>CAM 01 • LULA [AO VIVO]</span>
                </div>
                <div class="monitor-screen">
                  <img src="{b64_lula}" alt="Lula Presidente">
                  <div class="lower-third-gc gc-red">
                    <div class="gc-name">LUIZ INÁCIO LULA DA SILVA</div>
                    <div class="gc-role">PRESIDENTE DA REPÚBLICA</div>
                  </div>
                </div>
              </div>

              <!-- Stage Direction Card -->
              <div class="stage-direction-card">
                <div class="stage-direction-title">🎬 DIREÇÃO DE PALCO</div>
                <div>{sc["direction"]}</div>
              </div>
            </div>

            <!-- Right: Lula Speech Box (RED BORDER) + Tactical Box -->
            <div class="speech-column">
              <div class="lula-speech-box">
                <div class="speech-header-row header-red">
                  <span class="speaker-badge-red">🗣️ LUIZ INÁCIO LULA DA SILVA (PRESIDENTE)</span>
                  <span class="speaker-type-tag">RESPOSTA RECOMENDADA • ⏱ {sc["dur"]}</span>
                </div>
                <div class="lula-speech-content">
                  {lula_html}
                </div>
              </div>

              <!-- Tactical Takeaway Box -->
              <div class="tactical-takeaway-box">
                <div class="tactical-title">🎯 OBJETIVO TÁTICO & PONTOS DESMONTADOS</div>
                <div>{sc["takeaway"]}</div>
              </div>
            </div>
          </div>

          <!-- FOOTER -->
          <div class="scene-footer">
            <span>MEDIA TRAINING PRESIDENCIAL • 1º DEBATE DA REDE BANDEIRANTES</span>
            <span>DOCUMENTO CONFIDENCIAL</span>
            <span>PÁGINA {page_num:02d} DE 21</span>
          </div>
        </div>
        """
        html_parts.append(scene_html)

    html_parts.append("</body></html>")

    output_html_path = r"roteiros_respostas\storyboard_debate_band.html"
    full_html = "\n".join(html_parts)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"HTML regenerated: {output_html_path} ({len(full_html)} bytes)")

if __name__ == "__main__":
    generate_refined_storyboard()
