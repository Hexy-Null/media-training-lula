import os
import re
import base64
from PIL import Image

def get_base64_image(filename):
    path = os.path.join('assets/images', filename)
    with open(path, 'rb') as f:
        data = f.read()
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"

# Ensure thumbs exist
thumbs = {}
for name in ['lula.jpg', 'flavio.jpg', 'adriana.jpg', 'oinegue.jpg']:
    orig = os.path.join('assets/images', name)
    thumb_path = os.path.join('assets/images', 'thumb_' + name)
    if not os.path.exists(thumb_path) and os.path.exists(orig):
        img = Image.open(orig)
        img.thumbnail((300, 300))
        img.save(thumb_path, quality=85)
    thumbs[name] = get_base64_image('thumb_' + name if os.path.exists(thumb_path) else name)

# Read markdown
with open('roteiros_respostas/como_lula_deveria_ter_respondido_no_debate_da_band.md', encoding='utf-8') as f:
    text = f.read()

blocks = re.split(r'(?=# BLOCO \d)', text)

scenes = []
current_block = 'BLOCO 1'

tactical_insights = [
    "Assume coragem sem hipocrisia para crimes hediondos e vira a pauta para o investimento comprovado na Educação e no Pé-de-Meia.",
    "Conecta direto com a dona de casa, contrasta os 56% de inflação de Bolsonaro com os 13% atuais e destaca isenção de IR até R$ 5 mil.",
    "O único voto contra de Flávio entre 49 deputados — expõe a hipocrisia de quem diz defender a família mas retira direitos das mães.",
    "Corte cirúrgico — recusa a cortina de fumaça pessoal, retoma a ofensiva da licença-maternidade e empareda o adversário com o voto contra as mulheres.",
    "Inversão total — expõe que a investigação é da PF do governo Lula e confronta a mansão de R$ 6 milhões e as rachadinhas.",
    "Desmonte da CPI do INSS e denúncia da traição à pátria de quem foi aos EUA conspirar contra a soberania do próprio país.",
    "As 43 reuniões e o empréstimo de R$ 134 milhões no BRB — expõe o patrocinador secreto de Flávio e o banco Master.",
    "O suor do trabalhador que acorda às 5h vs. a mansão de R$ 6 milhões financiada com juros de pai para filho.",
    "Olhando nos olhos da mãe trabalhadora — solidariedade humana e recusa à covardia armada contra inocentes.",
    "O projeto para blindar milícias apagando numeração de balas — a ligação direta com Adriano da Nóbrega e a família.",
    "A falsa conversão exposta: quem nunca pegou ônibus lotado na vida e foi contra o fim da escala 6x1.",
    "O tesouraço de verdade corta comida e remédio — desmascara a farsa do modelo argentino de desmonte social.",
    "'Padrão Einstein' para quem tem plano de luxo do Estado vs. o escândalo dos hospitais federais do Rio com leitos trancados.",
    "'Teatrinho pra rede social' — 5 presídios federais de segurança máxima construídos pelo PT contra 0 de Bolsonaro.",
    "Quem defende o pobre sou eu: reajuste acima da inflação todo ano, isenção até R$ 5 mil e não deixa o trabalhador na pele e osso.",
    "'Fingir arrependimento' — expõe a pilantragem nos hospitais do Rio e exige pedido de perdão ao povo fluminense.",
    "O fruto não cai longe da árvore — parar de vender matéria-prima a preço de banana e investir na Nova Indústria Brasil.",
    "A loja de chocolates onde o lucro é maior que o faturamento e o deboche da palavra 'corrupto' escrita na própria mão.",
    "O plano do Cebolinha, o facão na mão e o contraste moral entre Geraldo Alckmin e o vice acusado de estupro.",
    "A síntese da escolha histórica e o apelo emocional do último mandato para colher os frutos de tudo que foi reconstruído."
]

for b in blocks:
    b_match = re.search(r'# (BLOCO \d)', b)
    if b_match:
        current_block = b_match.group(1)
    
    inter_list = re.split(r'\n(?=### Interação )', b)
    for inter in inter_list:
        if not inter.strip().startswith('### Interação'):
            continue
        
        lines = inter.strip().split('\n')
        title_raw = lines[0].replace('###', '').strip()
        
        # Timecode
        m_tc = re.search(r'\*\*Momento:\*\* (?:\[+)?([0-9:]+)', inter)
        timecode = m_tc.group(1) if m_tc else 'Debate'
        
        # Speaker determination
        if 'Adriana Araújo' in inter or 'Mediadora' in title_raw:
            speaker_name = 'Adriana Araújo'
            speaker_role = 'Jornalista & Mediadora da Band'
            speaker_avatar = thumbs['adriana.jpg']
            speaker_badge = 'PERGUNTA DA BANCADA'
            badge_color = '#38bdf8'
        elif 'Eduardo Oinegue' in inter or 'Oinegue' in title_raw or 'Pergunta do Mediador' in title_raw:
            speaker_name = 'Eduardo Oinegue'
            speaker_role = 'Âncora & Mediador da Band'
            speaker_avatar = thumbs['oinegue.jpg']
            speaker_badge = 'PERGUNTA DA BANCADA'
            badge_color = '#38bdf8'
        elif 'Considerações Finais' in title_raw:
            speaker_name = 'Mediação Band'
            speaker_role = 'Tempo de Encerramento (1 min 30s)'
            speaker_avatar = thumbs['oinegue.jpg']
            speaker_badge = 'ENCERRAMENTO DO DEBATE'
            badge_color = '#f59e0b'
        else:
            speaker_name = 'Flávio Bolsonaro'
            speaker_role = 'Senador & Candidato Adversário'
            speaker_avatar = thumbs['flavio.jpg']
            speaker_badge = 'CONFRONTO DIRETO / ATAQUE'
            badge_color = '#f43f5e'
            
        # Extract Question / Context text
        ctx_match = re.search(r'- \*\*(?:Contexto[^*]*|Pergunta[^*]*):\*\*\s*([\s\S]+?)(?=\n####|\Z)', inter)
        if ctx_match:
            ctx_text = ctx_match.group(1).strip()
        else:
            # Fallback
            sub1 = re.search(r'#### 1\. O que Flávio Bolsonaro falou[\s\S]+?(?=#### 2|\Z)', inter)
            if sub1:
                ctx_text = sub1.group(0).replace('#### 1. O que Flávio Bolsonaro falou exatamente (em dois momentos):', '').strip()
            else:
                ctx_text = "Confronto direto com o candidato adversário sobre temas estratégicos de governo e realizações."
                
        # Clean markdown formatting in ctx_text
        ctx_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', ctx_text)
        ctx_text = ctx_text.replace('\n', '<br>')
        
        # Extract Lula Ideal Response
        resp_match = re.search(r'#### ✍️ Sua Resposta Ideal[^\n]*\n+([\s\S]+?)(?=\n---|---|\Z)', inter)
        resp_text = ""
        acting_cue = "Olhar firme nos olhos do adversário, autoridade moral e postura presidencial."
        
        if resp_match:
            raw_resp = resp_match.group(1).strip()
            # check for cue like *(Olhando para a câmera)*
            cue_match = re.search(r'[\*_]\((.*?)\)[\*_]', raw_resp)
            if cue_match:
                acting_cue = cue_match.group(1)
                raw_resp = raw_resp.replace(cue_match.group(0), '')
            
            # clean quote markers
            lines_resp = [l.strip('> ').strip() for l in raw_resp.split('\n') if l.strip('> ').strip()]
            
            # format paragraphs
            paras = []
            for lp in lines_resp:
                # bold convert
                lp_fmt = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', lp)
                lp_fmt = re.sub(r'\"(.*?)\"', r'“\1”', lp_fmt)
                lp_fmt = lp_fmt.strip('*_')
                if lp_fmt.strip():
                    paras.append(f"<p>{lp_fmt}</p>")
            resp_text = "".join(paras)
            
        sc_idx = len(scenes)
        insight = tactical_insights[sc_idx] if sc_idx < len(tactical_insights) else "Confronto de propostas e afirmação de autoridade."

        scenes.append({
            'block': current_block,
            'title': title_raw,
            'timecode': timecode,
            'speaker_name': speaker_name,
            'speaker_role': speaker_role,
            'speaker_avatar': speaker_avatar,
            'speaker_badge': speaker_badge,
            'badge_color': badge_color,
            'question_text': ctx_text,
            'lula_avatar': thumbs['lula.jpg'],
            'acting_cue': acting_cue,
            'lula_response': resp_text,
            'insight': insight
        })

print(f"Total scenes loaded: {len(scenes)}")

# Build HTML
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Storyboard de Media Training — Debate Band</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@700;800&display=swap');

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        @page {{
            size: A4 portrait;
            margin: 8mm 10mm 8mm 10mm;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #080c14;
            color: #f1f5f9;
            line-height: 1.45;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        /* COVER PAGE */
        .cover-page {{
            page-break-after: always;
            break-after: page;
            height: 280mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: radial-gradient(circle at 50% 20%, #172554 0%, #090d16 65%, #04070d 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px 35px;
            position: relative;
            overflow: hidden;
        }}

        .cover-page::before {{
            content: '';
            position: absolute;
            top: -100px;
            left: 50%;
            transform: translateX(-50%);
            width: 500px;
            height: 300px;
            background: radial-gradient(ellipse, rgba(56, 189, 248, 0.25) 0%, transparent 70%);
            filter: blur(50px);
            pointer-events: none;
        }}

        .cover-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #b91c1c, #dc2626);
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 6px 16px;
            border-radius: 9999px;
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.4);
            margin-bottom: 20px;
        }}

        .cover-title {{
            font-family: 'Cinzel', serif;
            font-size: 32px;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: 0.5px;
            color: #ffffff;
            margin-bottom: 12px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
        }}

        .cover-title span {{
            color: #fbbf24;
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .cover-subtitle {{
            font-size: 14px;
            color: #94a3b8;
            max-width: 90%;
            line-height: 1.6;
        }}

        .cover-clash {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 25px;
            margin: 25px 0;
            padding: 22px 20px;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }}

        .clash-card {{
            text-align: center;
            flex: 1;
        }}

        .clash-avatar {{
            width: 105px;
            height: 105px;
            border-radius: 50%;
            object-fit: cover;
            margin: 0 auto 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }}

        .clash-lula {{
            border: 3px solid #dc2626;
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.4);
        }}

        .clash-flavio {{
            border: 3px solid #0284c7;
            box-shadow: 0 0 20px rgba(2, 132, 199, 0.4);
        }}

        .clash-name {{
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
        }}

        .clash-role {{
            font-size: 11px;
            color: #94a3b8;
            margin-top: 2px;
        }}

        .clash-vs {{
            font-family: 'Cinzel', serif;
            font-size: 24px;
            font-weight: 800;
            color: #fbbf24;
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.3);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .cover-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }}

        .stat-box {{
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 14px 12px;
            text-align: center;
        }}

        .stat-val {{
            font-size: 20px;
            font-weight: 800;
            color: #38bdf8;
        }}

        .stat-lbl {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            margin-top: 4px;
        }}

        .cover-footer {{
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: #64748b;
        }}

        /* SCENE PAGE (VERTICAL STORYBOARD CARD) */
        .scene-page {{
            page-break-after: always;
            break-after: page;
            height: 280mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 2px 0;
            box-sizing: border-box;
        }}

        .scene-container {{
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            height: 100%;
        }}

        /* SCENE HEADER */
        .scene-header {{
            background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .scene-tag-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .scene-badge-num {{
            background: #dc2626;
            color: #ffffff;
            font-size: 10px;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }}

        .scene-timecode {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #38bdf8;
            font-size: 10.5px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
        }}

        .scene-title {{
            font-size: 12px;
            font-weight: 700;
            color: #f8fafc;
            max-width: 65%;
            text-align: right;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* SCENE BODY */
        .scene-body {{
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            flex: 1;
            justify-content: space-between;
        }}

        /* CHALLENGER CARD (TOP) */
        .actor-card {{
            display: flex;
            gap: 12px;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 10px 14px;
        }}

        .actor-card.challenger {{
            border-left: 4px solid #64748b;
        }}

        .actor-avatar-wrap {{
            flex-shrink: 0;
            text-align: center;
        }}

        .actor-avatar {{
            width: 52px;
            height: 52px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }}

        .actor-info {{
            flex: 1;
        }}

        .actor-meta {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 4px;
        }}

        .actor-name {{
            font-size: 12px;
            font-weight: 800;
            color: #f8fafc;
        }}

        .actor-role {{
            font-size: 9.5px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .actor-speech {{
            font-size: 10.5px;
            color: #cbd5e1;
            line-height: 1.45;
            background: rgba(0, 0, 0, 0.2);
            padding: 8px 10px;
            border-radius: 6px;
            border-left: 2px solid rgba(255, 255, 255, 0.1);
        }}

        /* CAMERA TRANSITION DIVIDER */
        .camera-cut {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 2px 0;
        }}

        .cut-line {{
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(220, 38, 38, 0.4), transparent);
        }}

        .cut-label {{
            font-size: 9px;
            font-weight: 800;
            color: #fbbf24;
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.25);
            padding: 2px 10px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }}

        /* LULA RESPONSE CARD (MAIN FOCUS) */
        .lula-card {{
            display: flex;
            gap: 14px;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1.5px solid rgba(220, 38, 38, 0.35);
            border-left: 5px solid #dc2626;
            border-radius: 14px;
            padding: 13px 15px;
            box-shadow: 0 8px 24px rgba(220, 38, 38, 0.12);
            flex: 1;
        }}

        .lula-avatar-wrap {{
            flex-shrink: 0;
            text-align: center;
        }}

        .lula-avatar {{
            width: 62px;
            height: 62px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #fbbf24;
            box-shadow: 0 0 16px rgba(251, 191, 36, 0.3);
        }}

        .lula-seal {{
            display: inline-block;
            background: #dc2626;
            color: #ffffff;
            font-size: 8px;
            font-weight: 800;
            padding: 2px 5px;
            border-radius: 4px;
            text-transform: uppercase;
            margin-top: 4px;
            letter-spacing: 0.5px;
        }}

        .lula-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .lula-cue-box {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.2);
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 9.5px;
            font-weight: 700;
            color: #fde68a;
            margin-bottom: 7px;
        }}

        .lula-dialogue {{
            font-size: 11px;
            color: #f8fafc;
            line-height: 1.5;
            flex: 1;
        }}

        .lula-dialogue p {{
            margin-bottom: 5px;
        }}

        .lula-dialogue p:last-child {{
            margin-bottom: 0;
        }}

        .lula-dialogue strong {{
            color: #fbbf24;
            font-weight: 700;
        }}

        /* TACTICAL INSIGHT CARD */
        .insight-card {{
            background: rgba(251, 191, 36, 0.05);
            border: 1px solid rgba(251, 191, 36, 0.2);
            border-radius: 8px;
            padding: 6px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 10px;
            color: #fde68a;
        }}

        .insight-badge {{
            background: #fbbf24;
            color: #000000;
            font-size: 8.5px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            text-transform: uppercase;
            flex-shrink: 0;
        }}

        /* FOOTER BRANDING */
        .scene-footer {{
            background: #090d16;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding: 6px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 9px;
            color: #64748b;
        }}

        .brand-band {{
            color: #38bdf8;
            font-weight: 700;
        }}
    </style>
</head>
<body>

    <!-- COVER PAGE -->
    <div class="cover-page">
        <div>
            <div class="cover-badge">Media Training • Documento Confidencial de Preparação</div>
            <h1 class="cover-title">STORYBOARD DO DEBATE<br><span>COMO LULA DEVERIA TER RESPONDIDO</span></h1>
            <p class="cover-subtitle">
                Reconstituição cena a cena do 1º Debate da Rede Bandeirantes em formato visual de storyboard vertical. 
                Cada cena confronta a pergunta ou ataque com a resposta ideal estratégica, desenhada com linguagem popular, autoridade presidencial e foco em desarmar narrativas.
            </p>
        </div>

        <div class="cover-clash">
            <div class="clash-card">
                <img src="{thumbs['lula.jpg']}" class="clash-avatar clash-lula" alt="Lula">
                <div class="clash-name">LUIZ INÁCIO LULA DA SILVA</div>
                <div class="clash-role">Presidente da República</div>
            </div>
            <div class="clash-vs">VS</div>
            <div class="clash-card">
                <img src="{thumbs['flavio.jpg']}" class="clash-avatar clash-flavio" alt="Flávio Bolsonaro">
                <div class="clash-name">FLÁVIO BOLSONARO</div>
                <div class="clash-role">Senador da República</div>
            </div>
        </div>

        <div>
            <div class="cover-stats">
                <div class="stat-box">
                    <div class="stat-val">20 CENAS</div>
                    <div class="stat-lbl">Confrontos Mapeados</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">3 BLOCOS</div>
                    <div class="stat-lbl">Estrutura Completa Band</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">100% ORALIDADE</div>
                    <div class="stat-lbl">Linguagem Popular de TV</div>
                </div>
            </div>

            <div class="cover-footer">
                <div>Rede Bandeirantes • Debate Presidencial</div>
                <div>Assessoria de Comunicação & Preparação de Palco</div>
            </div>
        </div>
    </div>
"""

# Add Scenes
for i, sc in enumerate(scenes, 1):
    html_content += f"""
    <!-- SCENE {i:02d} -->
    <div class="scene-page">
        <div class="scene-container">
            <!-- HEADER -->
            <div class="scene-header">
                <div class="scene-tag-group">
                    <span class="scene-badge-num">CENA {i:02d} / 20</span>
                    <span class="scene-timecode">⏱️ {sc['timecode']}</span>
                    <span style="font-size: 10px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">{sc['block']}</span>
                </div>
                <div class="scene-title">{sc['title']}</div>
            </div>

            <!-- BODY -->
            <div class="scene-body">
                <!-- TOP CARD (CHALLENGER / MODERATOR) -->
                <div class="actor-card challenger">
                    <div class="actor-avatar-wrap">
                        <img src="{sc['speaker_avatar']}" class="actor-avatar" alt="{sc['speaker_name']}">
                    </div>
                    <div class="actor-info">
                        <div class="actor-meta">
                            <div class="actor-name">{sc['speaker_name']}</div>
                            <div class="actor-role">{sc['speaker_role']}</div>
                        </div>
                        <div class="actor-speech">
                            {sc['question_text']}
                        </div>
                    </div>
                </div>

                <!-- CAMERA CUT -->
                <div class="camera-cut">
                    <div class="cut-line"></div>
                    <div class="cut-label">⚡ CORTE DE CÂMERA 1 • RESPOSTA PRESIDENCIAL</div>
                    <div class="cut-line"></div>
                </div>

                <!-- LULA RESPONSE CARD -->
                <div class="lula-card">
                    <div class="lula-avatar-wrap">
                        <img src="{sc['lula_avatar']}" class="lula-avatar" alt="Lula">
                        <div class="lula-seal">PRESIDENTE</div>
                    </div>
                    <div class="lula-content">
                        <div class="lula-cue-box">
                            🎬 DIREÇÃO CÊNICA: {sc['acting_cue']}
                        </div>
                        <div class="lula-dialogue">
                            {sc['lula_response']}
                        </div>
                    </div>
                </div>

                <!-- TACTICAL INSIGHT -->
                <div class="insight-card">
                    <span class="insight-badge">🎯 IMPACTO DE TV</span>
                    <span>{sc['insight']}</span>
                </div>
            </div>

            <!-- FOOTER -->
            <div class="scene-footer">
                <div>Debate Band • Media Training Estratégico</div>
                <div>Cena {i} de 20 • Formato Storyboard Vertical</div>
            </div>
        </div>
    </div>
"""

html_content += """
</body>
</html>
"""

# Save HTML
html_path = 'roteiros_respostas/storyboard_debate_band.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML saved to {html_path} ({os.path.getsize(html_path)} bytes)")
