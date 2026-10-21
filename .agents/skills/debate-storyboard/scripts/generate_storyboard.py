#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Storyboard Audiovisual para Media Training de Debates
Gera HTML autossuficiente e compila em PDF A4 via Microsoft Edge headless.
"""

import os
import sys
import re
import base64
import subprocess
import argparse
from pathlib import Path
from pypdf import PdfReader

def get_base64_image(image_path: str) -> str:
    """Converte arquivo de imagem local em string Data URI base64."""
    if not os.path.exists(image_path):
        return ""
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

def parse_debate_scenes(md_path: str):
    """Extrai as cenas e metadados estruturados do arquivo markdown de roteiro."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_scenes = re.split(r'\n(?=### Cena \d+:)', content)
    scenes = []

    for raw in raw_scenes:
        if not raw.strip().startswith('### Cena'):
            continue

        lines = raw.strip().split('\n')
        header_line = lines[0].strip()
        idx_match = re.search(r'### Cena (\d+): (.*)', header_line)
        if not idx_match:
            continue
        scene_idx = int(idx_match.group(1))
        scene_title = idx_match.group(2).strip()

        tc_match = re.search(r'\*\*TC:\*\*\s*\[(.*?)\]', raw)
        tc = tc_match.group(1) if tc_match else "00:00"

        block_match = re.search(r'\*\*Bloco:\*\*\s*(.*?)(?:\n|$)', raw)
        block = block_match.group(1).strip() if block_match else "Bloco Geral"

        dur_match = re.search(r'\*\*Duração da Resposta:\*\*\s*(.*?)(?:\n|$)', raw)
        dur = dur_match.group(1).strip() if dur_match else "1 min"

        direct_match = re.search(r'\*\*Confronto Direto:\*\*\s*(Sim|Não)', raw, re.IGNORECASE)
        is_direct = direct_match.group(1).lower() == "sim" if direct_match else True

        # Oponente
        opp_name = "Flávio Bolsonaro"
        opp_role = "Senador da República / Opositor"
        opp_key = "flavio"

        if "Adriana Araújo" in raw or "Adriana" in scene_title:
            opp_name = "Adriana Araújo"
            opp_role = "Mediadora / Jornalista Band"
            opp_key = "adriana"
        elif "Eduardo Oinegue" in raw or "Oinegue" in scene_title:
            opp_name = "Eduardo Oinegue"
            opp_role = "Mediador / Jornalista Band"
            opp_key = "oinegue"

        # Extração de Seções
        attack_text = ""
        attack_m = re.search(r'#### 1\. O Ataque de Flávio.*?\n(.*?)(?=\n#### 2\.|\Z)', raw, re.DOTALL)
        if not attack_m:
            attack_m = re.search(r'#### 1\. A Pergunta da Mediadora.*?\n(.*?)(?=\n#### 2\.|\Z)', raw, re.DOTALL)
        if not attack_m:
            attack_m = re.search(r'#### 1\. A Pergunta do Mediador.*?\n(.*?)(?=\n#### 2\.|\Z)', raw, re.DOTALL)
        if attack_m:
            attack_text = attack_m.group(1).strip()

        lula_text = ""
        lula_m = re.search(r'#### 2\. Resposta Recomendada.*?\n(.*?)(?=\n#### 3\.|\Z)', raw, re.DOTALL)
        if lula_m:
            lula_text = lula_m.group(1).strip()

        direction_text = ""
        dir_m = re.search(r'#### 3\. Direção de Palco.*?\n(.*?)(?=\n#### 4\.|\Z)', raw, re.DOTALL)
        if dir_m:
            direction_text = dir_m.group(1).strip()

        takeaway_text = ""
        take_m = re.search(r'#### 4\. Objetivo Tático.*?\n(.*?)(?=\n###|\Z)', raw, re.DOTALL)
        if take_m:
            takeaway_text = take_m.group(1).strip()

        # Normalização do ataque
        clean_attack_html = format_attack_html(attack_text)

        scenes.append({
            "index": scene_idx,
            "title": scene_title,
            "tc": tc,
            "block": block,
            "dur": dur,
            "is_direct": is_direct,
            "opp_name": opp_name,
            "opp_role": opp_role,
            "opp_key": opp_key,
            "attack_raw": attack_text,
            "clean_attack_html": clean_attack_html,
            "lula_text": lula_text,
            "direction": direction_text,
            "takeaway": takeaway_text
        })

    return sorted(scenes, key=lambda s: s["index"])

def format_attack_html(attack_raw: str) -> str:
    """Formata o texto de ataque/pergunta para exibição limpa no box azul."""
    lines = attack_raw.split('\n')
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        moment_m = re.match(r'-\s*\*\*(\d+º Momento.*?)\*\*:\s*(.*)', line)
        if moment_m:
            m_title = moment_m.group(1)
            m_desc = moment_m.group(2).strip().strip('"').strip('“').strip('”')
            formatted.append(f'<p style="margin:0 0 4px 0;"><span class="sub-moment-header">⏱ {m_title}</span> <em>"{m_desc}"</em></p>')
            continue
        cleaned = line.strip('>').strip().strip('"').strip('“').strip('”')
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', cleaned)
        formatted.append(f'<p style="margin:0 0 4px 0;">"{cleaned}"</p>')
    return "".join(formatted)

def format_speech_html(speech_raw: str) -> str:
    """Formata falas com divisões cênicas de parentéticas (itálico entre parênteses)."""
    blocks = re.split(r'\n\s*\n', speech_raw)
    html_paragraphs = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        block = block.strip('>').strip()
        parts = re.split(r'(\*\(.*?\)\*)', block)
        p_acc = []
        for p in parts:
            if not p:
                continue
            parenthetical_match = re.match(r'\*\((.*?)\)\*', p.strip())
            if parenthetical_match:
                cue = parenthetical_match.group(1).strip()
                p_acc.append(f'<div class="screenplay-parenthetical">🎬 <em>({cue})</em></div>')
            else:
                txt = p.strip()
                txt = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', txt)
                txt = re.sub(r'\*(.*?)\*', r'<em>\1</em>', txt)
                p_acc.append(txt)
        inner_content = " ".join(p_acc)
        html_paragraphs.append(f'<p class="speech-p">"{inner_content}"</p>')
    return "".join(html_paragraphs)

def build_storyboard(md_input: str, output_html: str, output_pdf: str, assets_dir: str):
    """Constrói o HTML completo e compila em PDF A4."""
    scenes = parse_debate_scenes(md_input)
    print(f"Carregadas {len(scenes)} cenas de {md_input}.")

    # Carregar imagens base64
    b64_lula = get_base64_image(os.path.join(assets_dir, "crop_lula.jpg"))
    b64_flavio = get_base64_image(os.path.join(assets_dir, "crop_flavio.jpg"))
    b64_adriana = get_base64_image(os.path.join(assets_dir, "crop_adriana.jpg"))
    b64_oinegue = get_base64_image(os.path.join(assets_dir, "crop_oinegue.jpg"))
    b64_lula_cover = get_base64_image(os.path.join(assets_dir, "crop_lula_cover.jpg")) or b64_lula
    b64_flavio_cover = get_base64_image(os.path.join(assets_dir, "crop_flavio_cover.jpg")) or b64_flavio

    b64_map = {
        "lula": b64_lula,
        "flavio": b64_flavio,
        "adriana": b64_adriana,
        "oinegue": b64_oinegue
    }

    # Carregar CSS modular do tema
    css_theme_path = Path(__file__).parent.parent / "resources" / "storyboard_theme.css"
    if css_theme_path.exists():
        with open(css_theme_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    else:
        raise FileNotFoundError(f"Arquivo de tema CSS não encontrado em {css_theme_path}")

    # Montagem do HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='pt-BR'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>Storyboard do Debate: Como Lula Deveria Ter Respondido</title>",
        f"<style>{css_content}</style>",
        "</head>",
        "<body>"
    ]

    # 1. CAPA
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
          <div class="cover-screen">
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
          <div class="cover-screen">
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
          <div class="stat-number">{len(scenes)} CENAS</div>
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
        <span>PÁGINA 01 DE {len(scenes) + 1:02d}</span>
      </div>
    </div>
    """
    html_parts.append(cover_html)

    # 2. PÁGINAS DE CENA (1 Cena por Página)
    for sc in scenes:
        idx = sc["index"]
        page_num = idx + 1
        opp_key = sc["opp_key"]
        opp_img = b64_map.get(opp_key, b64_flavio)
        shot_type = "SPLIT-SCREEN & CLOSE-UP" if sc["is_direct"] else "PLANO DE BANCADA & CLOSE-UP"

        resp_len = len(sc["lula_text"])
        long_class = ""
        if resp_len > 2000:
            long_class = "is-very-long"
        elif resp_len > 1400:
            long_class = "is-long"

        lula_html = format_speech_html(sc["lula_text"])

        scene_html = f"""
        <div class="page-container scene-page {long_class}">
          <!-- HEADER -->
          <div class="scene-header">
            <div class="scene-meta-row">
              <div class="scene-badges">
                <span class="scene-num-badge">CENA {idx:02d} / {len(scenes):02d}</span>
                <span class="scene-block-badge">{sc["block"]}</span>
                <span class="scene-tc-badge">⏱ TC {sc["tc"]}</span>
              </div>
              <span class="scene-shot-type">{shot_type}</span>
            </div>
            <h2 class="scene-title">{sc["title"]}</h2>
          </div>

          <!-- ROW 1: O QUESTIONAMENTO / ATAQUE (AZUL) -->
          <div class="dialogue-row row-opponent">
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

              <div class="stage-direction-card">
                <div class="stage-direction-title">🎬 DIREÇÃO DE PALCO</div>
                <div>{sc["direction"]}</div>
              </div>
            </div>

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
            <span>PÁGINA {page_num:02d} DE {len(scenes) + 1:02d}</span>
          </div>
        </div>
        """
        html_parts.append(scene_html)

    html_parts.append("</body></html>")

    # Salvar HTML
    os.makedirs(os.path.dirname(os.path.abspath(output_html)), exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    print(f"HTML gerado com sucesso: {output_html}")

    # Compilar PDF via Edge Headless
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        edge_exe = "msedge"

    temp_profile = os.path.join(os.environ.get("TEMP", "C:/Temp"), "edge_storyboard_session")
    pdf_cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        f"--user-data-dir={temp_profile}",
        f"--print-to-pdf={os.path.abspath(output_pdf)}",
        "--no-pdf-header-footer",
        os.path.abspath(output_html)
    ]

    print("Compilando PDF A4 via Microsoft Edge headless...")
    subprocess.run(pdf_cmd, check=True)

    # Validar total de páginas
    reader = PdfReader(output_pdf)
    expected_pages = len(scenes) + 1
    total_pages = len(reader.pages)
    print(f"PDF compilado com sucesso: {output_pdf}")
    print(f"Total de páginas: {total_pages} (Esperado: {expected_pages})")

    if total_pages != expected_pages:
        print(f"AVISO: Discrepância na contagem de páginas ({total_pages} != {expected_pages}). Verifique classes .is-long.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de Storyboard Audiovisual para Debates")
    parser.add_argument("--input", "-i", required=True, help="Arquivo markdown com o roteiro das cenas")
    parser.add_argument("--output-html", "-o", default="storyboard.html", help="Caminho de saída para o HTML")
    parser.add_argument("--output-pdf", "-p", default="storyboard.pdf", help="Caminho de saída para o PDF")
    parser.add_argument("--assets", "-a", default="assets/images", help="Diretório contendo imagens dos participantes")
    args = parser.parse_args()

    build_storyboard(args.input, args.output_html, args.output_pdf, args.assets)
