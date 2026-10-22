#!/usr/bin/env python3
"""Gerador de storyboard audiovisual para media training de debates.

Lê um roteiro em Markdown no formato ``### Cena N: Título`` e produz um HTML
autossuficiente e um PDF A4 (uma cena por página) via Microsoft Edge headless.
"""

import argparse
import base64
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

LIMITE_RESPOSTA_LONGA = 1400
LIMITE_RESPOSTA_MUITO_LONGA = 2000
CAMINHO_TEMA_CSS = Path(__file__).parent.parent / "resources" / "storyboard_theme.css"
CAMINHO_EDGE_PADRAO = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


@dataclass
class ConfiguracaoDebate:
    emissora: str
    subtitulo: str
    descricao: str
    rodape: str
    mediador_nome: str
    mediador_cargo: str
    mediador_imagem: str
    destaque_numero: str
    destaque_rotulo: str


def carregar_imagem_base64(caminho_imagem: str) -> str:
    if not caminho_imagem or not os.path.exists(caminho_imagem):
        return ""
    extensao = os.path.splitext(caminho_imagem)[1].lower()
    tipo_mime = "image/jpeg" if extensao in (".jpg", ".jpeg") else "image/png"
    with open(caminho_imagem, "rb") as arquivo:
        conteudo = base64.b64encode(arquivo.read()).decode("utf-8")
    return f"data:{tipo_mime};base64,{conteudo}"


def converter_enfase_markdown(texto: str) -> str:
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    return re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", texto)


def remover_marcador_citacao(texto: str) -> str:
    linhas = [re.sub(r"^\s*>\s?", "", linha) for linha in texto.split("\n")]
    return "\n".join(linhas).strip()


def extrair_secao(conteudo_cena: str, padrao_titulo: str) -> str:
    correspondencia = re.search(
        rf"#### {padrao_titulo}[^\n]*\n(.*?)(?=\n####|\n### |\Z)", conteudo_cena, re.DOTALL
    )
    return correspondencia.group(1).strip() if correspondencia else ""


def extrair_metadado(conteudo_cena: str, rotulo: str, padrao_valor: str = r"(.*?)") -> str:
    correspondencia = re.search(rf"\*\*{rotulo}:\*\*\s*{padrao_valor}(?:\n|$)", conteudo_cena)
    return correspondencia.group(1).strip() if correspondencia else ""


def formatar_ataque_html(texto_ataque: str) -> str:
    paragrafos_html = []
    for linha in remover_marcador_citacao(texto_ataque).split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        momento = re.match(r"-\s*\*\*(\d+º Momento.*?)\*\*:?\s*(.*)", linha)
        if momento:
            rotulo_momento = momento.group(1)
            fala = converter_enfase_markdown(momento.group(2).strip())
            paragrafos_html.append(
                f'<p style="margin:0 0 4px 0;"><span class="sub-moment-header">⏱ {rotulo_momento}</span> {fala}</p>'
            )
            continue
        paragrafos_html.append(f'<p style="margin:0 0 4px 0;">{converter_enfase_markdown(linha)}</p>')
    return "".join(paragrafos_html)


def formatar_fala_html(texto_fala: str) -> str:
    blocos = re.split(r"\n\s*\n", remover_marcador_citacao(texto_fala))
    paragrafos_html = []
    for bloco in blocos:
        bloco = " ".join(linha.strip() for linha in bloco.split("\n") if linha.strip())
        if not bloco:
            continue
        indicacao_cenica = re.fullmatch(r"\*\((.*?)\)\*", bloco)
        if indicacao_cenica:
            paragrafos_html.append(
                f'<div class="screenplay-parenthetical">🎬 <em>({indicacao_cenica.group(1).strip()})</em></div>'
            )
            continue
        paragrafos_html.append(f'<p class="speech-p">{converter_enfase_markdown(bloco)}</p>')
    return "".join(paragrafos_html)


def identificar_interlocutor(conteudo_cena: str, configuracao: ConfiguracaoDebate) -> dict:
    if re.search(r"#### 1\. A Pergunta d[oa] Mediador", conteudo_cena):
        return {
            "nome": configuracao.mediador_nome,
            "cargo": configuracao.mediador_cargo,
            "chave": "mediador",
            "camera": "CAM 03",
        }
    return {
        "nome": "Flávio Bolsonaro",
        "cargo": "Senador da República / Opositor",
        "chave": "flavio",
        "camera": "CAM 02",
    }


def interpretar_cenas(caminho_roteiro: str, configuracao: ConfiguracaoDebate) -> list[dict]:
    with open(caminho_roteiro, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    cenas = []
    for trecho in re.split(r"\n(?=### Cena \d+:)", conteudo):
        cabecalho = re.match(r"### Cena (\d+):\s*(.*)", trecho.strip())
        if not cabecalho:
            continue
        resposta_lula = extrair_secao(trecho, r"2\. Resposta Recomendada")
        if not resposta_lula:
            raise ValueError(f"Cena {cabecalho.group(1)} sem a seção '#### 2. Resposta Recomendada'.")
        confronto = extrair_metadado(trecho, "Confronto Direto", r"(Sim|Não)")
        cenas.append({
            "indice": int(cabecalho.group(1)),
            "titulo": cabecalho.group(2).strip(),
            "tc": extrair_metadado(trecho, "TC", r"\[(.*?)\]") or "00:00",
            "bloco": extrair_metadado(trecho, "Bloco") or "BLOCO GERAL",
            "duracao": extrair_metadado(trecho, "Duração da Resposta") or "1 min",
            "confronto_direto": confronto.lower() == "sim",
            "interlocutor": identificar_interlocutor(trecho, configuracao),
            "ataque_html": formatar_ataque_html(extrair_secao(trecho, r"1\. ")),
            "resposta_lula": resposta_lula,
            "direcao": converter_enfase_markdown(extrair_secao(trecho, r"3\. Direção de Palco")),
            "objetivo": converter_enfase_markdown(extrair_secao(trecho, r"4\. Objetivo Tático")),
        })
    if not cenas:
        raise ValueError(f"Nenhuma cena no formato '### Cena N:' encontrada em {caminho_roteiro}.")
    return sorted(cenas, key=lambda cena: cena["indice"])


def classe_tamanho_resposta(texto_resposta: str) -> str:
    if len(texto_resposta) > LIMITE_RESPOSTA_MUITO_LONGA:
        return "is-very-long"
    if len(texto_resposta) > LIMITE_RESPOSTA_LONGA:
        return "is-long"
    return ""


def montar_monitor(classe_cor: str, camera: str, rotulo_rec: str, imagem: str, nome: str, cargo: str,
                   classe_extra: str = "", classe_tela: str = "monitor-screen") -> str:
    cor = "blue" if classe_cor == "monitor-blue" else "red"
    return f"""
        <div class="broadcast-monitor {classe_cor} {classe_extra}">
          <div class="monitor-topbar">
            <span><span class="dot-{cor}"></span> {rotulo_rec}</span>
            <span>{camera}</span>
          </div>
          <div class="{classe_tela}">
            <img src="{imagem}" alt="{nome}">
            <div class="lower-third-gc gc-{cor}">
              <div class="gc-name">{nome.upper()}</div>
              <div class="gc-role">{cargo.upper()}</div>
            </div>
          </div>
        </div>"""


def montar_capa(cenas: list[dict], configuracao: ConfiguracaoDebate, imagens: dict) -> str:
    total_paginas = len(cenas) + 1
    total_blocos = len({cena["bloco"] for cena in cenas})
    monitor_flavio = montar_monitor("monitor-blue", "CAM 02 • FLÁVIO", "REC 00:00:00", imagens["flavio_capa"],
                                    "Flávio Bolsonaro", "Senador da República / Opositor",
                                    "cover-monitor", "cover-screen")
    monitor_lula = montar_monitor("monitor-red", "CAM 01 • LULA", "REC 00:00:00", imagens["lula_capa"],
                                  "Luiz Inácio Lula da Silva", "Presidente da República",
                                  "cover-monitor", "cover-screen")
    return f"""
    <div class="page-container cover-page">
      <div class="cover-top-badge">
        <span class="cover-seal">CONFIDENCIAL • MEDIA TRAINING DE PALCO • ELEIÇÕES 2026</span>
        <span class="cover-band-tag">{configuracao.emissora}</span>
      </div>
      <div class="cover-main-header">
        <div class="cover-pretitle">ROTEIRO AUDIOVISUAL &amp; DIREÇÃO DE TV</div>
        <h1 class="cover-title">STORYBOARD DO DEBATE</h1>
        <div class="cover-subtitle">{configuracao.subtitulo}</div>
        <div class="cover-desc">{configuracao.descricao}</div>
      </div>
      <div class="cover-duel-container">
        {monitor_flavio}
        <div class="cover-vs-badge-container">
          <div class="cover-vs-circle">VS</div>
          <div class="cover-vs-label">CONFRONTO DIRETO</div>
          <div class="cover-vs-sub">MEDIAÇÃO {configuracao.mediador_nome.upper()}</div>
        </div>
        {monitor_lula}
      </div>
      <div class="cover-stats-grid">
        <div class="cover-stat-card"><div class="stat-number">{len(cenas)} CENAS</div><div class="stat-label">Confrontos Simulados</div></div>
        <div class="cover-stat-card"><div class="stat-number">{total_blocos} BLOCOS</div><div class="stat-label">Estrutura do Debate</div></div>
        <div class="cover-stat-card"><div class="stat-number">100% ORAL</div><div class="stat-label">Linguagem Direta de TV</div></div>
        <div class="cover-stat-card"><div class="stat-number">{configuracao.destaque_numero}</div><div class="stat-label">{configuracao.destaque_rotulo}</div></div>
      </div>
      <div class="cover-pillars-box">
        <div class="pillars-title">🎯 PILARES ESTRATÉGICOS DE MEDIA TRAINING APLICADOS</div>
        <div class="pillars-grid">
          <div class="pillar-item"><strong>1. Desarme Imediato de Provocações:</strong> Não entrar em ataques pessoais; desarmar em 15 segundos e devolver com fato documentado.</div>
          <div class="pillar-item"><strong>2. Domínio Cênico &amp; Expressão:</strong> Postura de autoridade de Estado, respeito ao mediador e ao tempo, e olhar para a Câmera 1 sem demonstrar irritação.</div>
          <div class="pillar-item"><strong>3. Foco na Mesa do Trabalhador:</strong> Conectar cada tema (comida, emprego, saúde, segurança) à vida real do eleitor.</div>
          <div class="pillar-item"><strong>4. O Contraste Histórico:</strong> Evidenciar a diferença entre quem entrega resultado e quem foge das perguntas.</div>
        </div>
      </div>
      <div class="cover-footer">
        <span>DOCUMENTO DE USO INTERNO E EXCLUSIVO DE PREPARAÇÃO</span>
        <span>ASSESSORIA DE COMUNICAÇÃO ESTRATÉGICA</span>
        <span>PÁGINA 01 DE {total_paginas:02d}</span>
      </div>
    </div>"""


def montar_pagina_cena(cena: dict, total_cenas: int, configuracao: ConfiguracaoDebate, imagens: dict) -> str:
    interlocutor = cena["interlocutor"]
    imagem_interlocutor = imagens.get(interlocutor["chave"]) or imagens["flavio"]
    enquadramento = "SPLIT-SCREEN &amp; CLOSE-UP" if cena["confronto_direto"] else "PLANO DE BANCADA &amp; CLOSE-UP"
    monitor_interlocutor = montar_monitor(
        "monitor-blue", f'{interlocutor["camera"]} • {interlocutor["nome"].split()[0].upper()}',
        f'REC {cena["tc"]}:00', imagem_interlocutor, interlocutor["nome"], interlocutor["cargo"])
    monitor_lula = montar_monitor("monitor-red", "CAM 01 • LULA [AO VIVO]", f'REC {cena["tc"]}:25',
                                  imagens["lula"], "Luiz Inácio Lula da Silva", "Presidente da República")
    return f"""
    <div class="page-container scene-page {classe_tamanho_resposta(cena["resposta_lula"])}">
      <div class="scene-header">
        <div class="scene-meta-row">
          <div class="scene-badges">
            <span class="scene-num-badge">CENA {cena["indice"]:02d} / {total_cenas:02d}</span>
            <span class="scene-block-badge">{cena["bloco"]}</span>
            <span class="scene-tc-badge">⏱ TC {cena["tc"]}</span>
          </div>
          <span class="scene-shot-type">{enquadramento}</span>
        </div>
        <h2 class="scene-title">{cena["titulo"]}</h2>
      </div>
      <div class="dialogue-row row-opponent">
        <div class="monitor-column">{monitor_interlocutor}</div>
        <div class="speech-column">
          <div class="opponent-speech-box">
            <div class="speech-header-row header-blue">
              <span class="speaker-badge-blue">🎙️ {interlocutor["nome"].upper()}</span>
              <span class="speaker-type-tag">SIMULAÇÃO • QUESTIONAMENTO / ATAQUE</span>
            </div>
            <div class="opponent-content-text">{cena["ataque_html"]}</div>
          </div>
        </div>
      </div>
      <div class="camera-cut-divider">
        <span class="cut-line"></span>
        <span class="cut-badge">⚡ CORTE DE TRANSMISSÃO ➔ CÂMERA 1 • LULA [CLOSE-UP FRONTAL]</span>
        <span class="cut-line"></span>
      </div>
      <div class="dialogue-row row-lula">
        <div class="monitor-column">
          {monitor_lula}
          <div class="stage-direction-card">
            <div class="stage-direction-title">🎬 DIREÇÃO DE PALCO</div>
            <div>{cena["direcao"]}</div>
          </div>
        </div>
        <div class="speech-column">
          <div class="lula-speech-box">
            <div class="speech-header-row header-red">
              <span class="speaker-badge-red">🗣️ LUIZ INÁCIO LULA DA SILVA (PRESIDENTE)</span>
              <span class="speaker-type-tag">RESPOSTA RECOMENDADA • ⏱ {cena["duracao"]}</span>
            </div>
            <div class="lula-speech-content">{formatar_fala_html(cena["resposta_lula"])}</div>
          </div>
          <div class="tactical-takeaway-box">
            <div class="tactical-title">🎯 OBJETIVO TÁTICO &amp; PONTOS DESMONTADOS</div>
            <div>{cena["objetivo"]}</div>
          </div>
        </div>
      </div>
      <div class="scene-footer">
        <span>{configuracao.rodape}</span>
        <span>DOCUMENTO CONFIDENCIAL</span>
        <span>PÁGINA {cena["indice"] + 1:02d} DE {total_cenas + 1:02d}</span>
      </div>
    </div>"""


def carregar_imagens(diretorio_imagens: str, configuracao: ConfiguracaoDebate) -> dict:
    def imagem(nome_arquivo: str) -> str:
        return carregar_imagem_base64(os.path.join(diretorio_imagens, nome_arquivo))

    imagens = {
        "lula": imagem("crop_lula.jpg"),
        "flavio": imagem("crop_flavio.jpg"),
        "mediador": carregar_imagem_base64(configuracao.mediador_imagem),
    }
    imagens["lula_capa"] = imagem("crop_lula_cover.jpg") or imagens["lula"]
    imagens["flavio_capa"] = imagem("crop_flavio_cover.jpg") or imagens["flavio"]
    ausentes = [chave for chave in ("lula", "flavio", "mediador") if not imagens[chave]]
    if ausentes:
        raise FileNotFoundError(f"Imagens não encontradas para: {', '.join(ausentes)}.")
    return imagens


def compilar_pdf(caminho_html: str, caminho_pdf: str) -> None:
    executavel_edge = CAMINHO_EDGE_PADRAO if os.path.exists(CAMINHO_EDGE_PADRAO) else "msedge"
    # Perfil temporário exclusivo por execução evita o erro 32 (arquivo bloqueado) do Edge no Windows.
    perfil_temporario = os.path.join(os.environ.get("TEMP", "."), f"edge_storyboard_{os.getpid()}")
    subprocess.run([
        executavel_edge, "--headless", "--disable-gpu", f"--user-data-dir={perfil_temporario}",
        f"--print-to-pdf={os.path.abspath(caminho_pdf)}", "--no-pdf-header-footer",
        os.path.abspath(caminho_html),
    ], check=True)


def gerar_storyboard(caminho_roteiro: str, caminho_html: str, caminho_pdf: str,
                     diretorio_imagens: str, configuracao: ConfiguracaoDebate) -> None:
    cenas = interpretar_cenas(caminho_roteiro, configuracao)
    imagens = carregar_imagens(diretorio_imagens, configuracao)
    with open(CAMINHO_TEMA_CSS, "r", encoding="utf-8") as arquivo:
        css_tema = arquivo.read()

    paginas = [montar_capa(cenas, configuracao, imagens)]
    paginas += [montar_pagina_cena(cena, len(cenas), configuracao, imagens) for cena in cenas]
    documento = (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        f"<title>Storyboard do Debate — {configuracao.subtitulo}</title>"
        f"<style>{css_tema}</style></head><body>{''.join(paginas)}</body></html>"
    )
    os.makedirs(os.path.dirname(os.path.abspath(caminho_html)), exist_ok=True)
    with open(caminho_html, "w", encoding="utf-8") as arquivo:
        arquivo.write(documento)
    print(f"HTML gerado: {caminho_html} ({len(cenas)} cenas)")

    compilar_pdf(caminho_html, caminho_pdf)
    total_paginas = len(PdfReader(caminho_pdf).pages)
    paginas_esperadas = len(cenas) + 1
    print(f"PDF gerado: {caminho_pdf} — {total_paginas} páginas (esperado: {paginas_esperadas})")
    if total_paginas != paginas_esperadas:
        raise RuntimeError(
            f"Contagem de páginas divergente ({total_paginas} != {paginas_esperadas}): "
            "alguma cena transbordou; reduza o texto ou ajuste os limites de resposta longa."
        )


def ler_argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(description="Gerador de storyboard audiovisual para debates")
    analisador.add_argument("--input", "-i", required=True, help="Roteiro Markdown no formato '### Cena N:'")
    analisador.add_argument("--output-html", "-o", required=True, help="Caminho de saída do HTML")
    analisador.add_argument("--output-pdf", "-p", required=True, help="Caminho de saída do PDF")
    analisador.add_argument("--assets", "-a", default="assets/images", help="Diretório com crop_lula/crop_flavio")
    analisador.add_argument("--emissora", required=True, help="Selo da capa, ex.: 'REDE GLOBO • 2º TURNO'")
    analisador.add_argument("--subtitulo", required=True, help="Subtítulo da capa")
    analisador.add_argument("--descricao", required=True, help="Parágrafo descritivo da capa")
    analisador.add_argument("--rodape", required=True, help="Texto do rodapé das cenas")
    analisador.add_argument("--mediador-nome", required=True)
    analisador.add_argument("--mediador-cargo", required=True)
    analisador.add_argument("--mediador-imagem", required=True, help="Caminho do recorte 320x360 do mediador")
    analisador.add_argument("--destaque-numero", default="100% SIMULADO")
    analisador.add_argument("--destaque-rotulo", default="Material de Preparação")
    return analisador.parse_args()


if __name__ == "__main__":
    argumentos = ler_argumentos()
    gerar_storyboard(
        argumentos.input, argumentos.output_html, argumentos.output_pdf, argumentos.assets,
        ConfiguracaoDebate(
            emissora=argumentos.emissora,
            subtitulo=argumentos.subtitulo,
            descricao=argumentos.descricao,
            rodape=argumentos.rodape,
            mediador_nome=argumentos.mediador_nome,
            mediador_cargo=argumentos.mediador_cargo,
            mediador_imagem=argumentos.mediador_imagem,
            destaque_numero=argumentos.destaque_numero,
            destaque_rotulo=argumentos.destaque_rotulo,
        ),
    )
