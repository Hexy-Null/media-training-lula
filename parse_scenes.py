import os
import re
import base64

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        ext = os.path.splitext(image_path)[1].lower()
        mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
        return f"data:{mime};base64,{encoded}"

def clean_markdown_quotes(text):
    if not text:
        return ""
    text = text.replace(r'\*', '*').replace(r'\"', '"').replace(r'\_', '_')
    lines = []
    for line in text.split("\n"):
        l = line.strip()
        if l in ["---", "***", "___"]:
            continue
        if l.startswith(">"):
            l = l[1:].strip()
        lines.append(l)
    cleaned = "\n".join(lines).strip()

    while True:
        original = cleaned
        cleaned = cleaned.strip()
        if (cleaned.startswith('*') and cleaned.endswith('*')) or (cleaned.startswith('_') and cleaned.endswith('_')):
            cleaned = cleaned[1:-1].strip()
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith('“') and cleaned.endswith('”')):
            cleaned = cleaned[1:-1].strip()
        if (cleaned.startswith('*') and cleaned.endswith('*')) or (cleaned.startswith('_') and cleaned.endswith('_')):
            cleaned = cleaned[1:-1].strip()
        if cleaned == original:
            break

    return cleaned

def format_speech_html(text):
    raw = text.replace(r'\*', '*').replace(r'\"', '"').replace(r'\_', '_')
    lines = []
    for line in raw.split('\n'):
        l = line.strip()
        if l in ['---', '***', '___']:
            continue
        if l.startswith('>'):
            l = l[1:].strip()
        
        m_dir = re.match(r'^\*?\((.*?)\)\*?$', l)
        if m_dir:
            lines.append(f'\n\n[CENICA: {m_dir.group(1)}]\n\n')
            continue
        lines.append(l)
    
    joined = '\n'.join(lines).strip()
    paras = [p.strip() for p in joined.split('\n\n') if p.strip()]
    formatted = []
    
    for p in paras:
        if p.startswith('[CENICA: ') and p.endswith(']'):
            cue = p[9:-1].strip()
            formatted.append(f'<div class="screenplay-parenthetical">🎬 <em>({cue})</em></div>')
            continue
            
        p = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p)
        p = p.strip('*').strip('_').strip('"').strip("'").strip('“').strip('”').strip('*').strip('_').strip()
        p = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', p)
        p = re.sub(r'\_(.*?)\_', r'<em>\1</em>', p)
        formatted.append(f'<p>{p}</p>')
        
    return ''.join(formatted)

def extract_clean_attack(raw):
    # Context part is everything before Lula's ideal response
    split_lula = re.split(r'#### ✍️ Sua Resposta Ideal|#### .*?Resposta Ideal', raw)
    context_part = split_lula[0]
    
    # Remove #### Resposta Original de Lula... and anything after it
    attack_only = re.split(r'#### \d*\.?\s*Resposta Original de Lula|#### \d*\.?\s*O que Lula respondeu', context_part)[0]
    
    lines = attack_only.split('\n')
    filtered = []
    for l in lines:
        l_s = l.strip()
        if l_s.startswith('###') or l_s.startswith('- **Momento') or l_s.startswith('#### 1. O que Flávio'):
            continue
        filtered.append(l)
    text_clean = '\n'.join(filtered).strip()
    
    text_clean = re.sub(r'^\s*-\s*\*\*Contexto[^\:]*\:\*\*\s*', '', text_clean)
    text_clean = re.sub(r'^\s*-\s*\*\*Pergunta[^\:]*\:\*\*\s*', '', text_clean)
    
    def format_moment(m):
        mom_title = m.group(1).replace('[[', '[').replace(']]', ']').rstrip(':')
        return f'<div class="sub-moment-tag">⏱ <strong>{mom_title}</strong></div>'
    
    # Clean sub-moments like - **1º Momento de Flávio [[15:34] — A Fuga e o Escudo Familiar]:**
    text_clean = re.sub(r'-\s*\*\*(\d+º Momento[^\*]+)\*\*:?', format_moment, text_clean)
    text_clean = re.sub(r'-\s*\*\*Flávio Bolsonaro:\*\*', '<strong>Flávio Bolsonaro:</strong>', text_clean)
    text_clean = re.sub(r'-\s*\*\*Dinâmica:\*\*', '<em>Dinâmica:</em>', text_clean)
    
    cleaned_lines = []
    for line in text_clean.split('\n'):
        l = line.strip()
        if l.startswith('>'):
            l = l[1:].strip()
        cleaned_lines.append(l)
    res = '\n'.join(cleaned_lines).strip()
    res = res.strip('*').strip('_').strip('"').strip()
    
    # Format paragraphs
    paragraphs = [p.strip() for p in res.split('\n\n') if p.strip()]
    formatted = []
    for p in paragraphs:
        if p.startswith('<div class="sub-moment-tag"'):
            formatted.append(p)
            continue
        p = p.replace(r'\*', '*').replace(r'\"', '"').replace(r'\_', '_')
        p = p.strip().strip('*').strip('_').strip('"').strip("'").strip('“').strip('”').strip('*').strip('_').strip()
        p = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p)
        p = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', p)
        p = re.sub(r'\_(.*?)\_', r'<em>\1</em>', p)
        formatted.append(f'<p>{p}</p>')
    return ''.join(formatted)

def parse_all_scenes():
    md_path = r'roteiros_respostas\como_lula_deveria_ter_respondido_no_debate_da_band.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    scenes_raw = re.split(r'\n(?=### Intera[çc][ãa]o \d+\.\d+)', content)[1:]
    scenes = []

    stage_directions = {
        1: "Olhar firme nos olhos da mediadora e transição suave para a lente central. Postura ereta e tom pedagógico de autoridade de Estado ao diferenciar escola integral de encarceramento em massa.",
        2: "Olhar para a câmera 1, falando diretamente ao trabalhador e à dona de casa. Tom calmo, seguro e didático ao explicar a inflação de alimentos sem jargões burocráticos.",
        3: "Olhar penetrante nos olhos de Flávio Bolsonaro. Expressão grave e protetiva ao defender os direitos das mulheres trabalhadoras, demonstrando contraste ético irremediável.",
        4: "Sorriso irônico sereno e postura relaxada no púlpito. Não entrar na provocação sobre familiares; desmontar com elegância citando o histórico da rachadinha e os 1.512 depósitos na loja de chocolates.",
        5: "Tom solene de indignação moral sincera. Olhar direto na câmera para expor o 'teatrinho de rede social' do oponente, cobrando a abertura mútua de sigilos bancários e fiscais.",
        6: "Postura de estadista imperturbável. Desmontar a falsa alegação de 'fuga' de parentes com dados da PF e devolver o questionamento com a investigação oficial do Ministério Público.",
        7: "Expressão cirúrgica de seriedade. Listar as 43 mentiras contadas pelo adversário com frieza documental, demonstrando domínio absoluto dos fatos e desarmando a fake news do Banco Master.",
        8: "Postura de juiz moral no confronto direto. Cobrar frontalmente a explicação sobre a Mansão financiada pelo BRB e o boné do banqueiro. Desmontar a encenação do adversário sem elevar o tom.",
        9: "Expressão paternal e respeitosa em relação às forças de segurança. Olhar para a câmera ao reafirmar a valorização do policial da base, diferenciando o dever do Estado da exploração política.",
        10: "Gesto firme de comando. Olhar direto para Flávio ao expor o voto contra o rastreamento de munições, conectando as armas desviadas à violência urbana que atinge o cidadão comum.",
        11: "Tom de indignação legítima e defesa dos trabalhadores. Olhar para o público de TV ao desmascarar a hipocrisia do adversário sobre a escala 6x1 e a precarização do emprego.",
        12: "Expressão lúcida e pedagógica. Desmontar o modelo ultraliberal argentino mostrando o salto da pobreza e a destruição da classe média, reafirmando o compromisso com a soberania nacional.",
        13: "Postura de governante construtor. Olhar firme para os mediadores ao defender o financiamento público de habitação e saneamento, demonstrando que responsabilidade fiscal se faz com inclusão social.",
        14: "Olhar de serenidade inabalável. Responder com dados irrefutáveis de geração de empregos e valorização do salário mínimo, esvaziando a narrativa catastrófica da oposição.",
        15: "Voz firme e cadenciada. Demonstrar autoridade técnica sobre o controle da inflação e o poder de compra da cesta básica, apontando a irresponsabilidade do teto de gastos do governo anterior.",
        16: "Ataque incisivo com domínio moral. Perguntar diretamente sobre o controle político dos hospitais federais do Rio, deixando o adversário sem espaço para narrativas ensaiadas.",
        17: "Visão estratégica de futuro. Olhar para a câmera ao articular indústria verde, transição energética e reindustrialização nacional, elevando o nível do debate para além do bate-boca.",
        18: "Tom patriótico e resoluto. Defender a riqueza das terras raras e minerais estratégicos como patrimônio inegociável do povo brasileiro contra a subserviência internacional.",
        19: "Ironia fina ao mencionar o 'plano do Cebolinha' e o facão na mão. Em seguida, corte para gravidade absoluta ao questionar a coerência moral do adversário e do seu vice.",
        20: "Olhar direto nos olhos do povo brasileiro através da lente principal. Tom afetuoso, humilde e histórico. Pedir um pacto de confiança para coroar o último mandato de sua vida pública com um país sem fome."
    }

    tactical_takeaways = {
        1: "Desarma o discurso punitivista populista ao provar que o investimento em educação em tempo integral (Pé-de-Meia) devolve R$ 3,49 à sociedade para cada R$ 1 investido.",
        2: "Conecta a política macroeconômica à mesa do trabalhador, transformando a discussão de juros em defesa do poder de compra e da geração de empregos com carteira assinada.",
        3: "Isola Flávio Bolsonaro perante o eleitorado feminino ao expor seu voto solitário contra a ampliação da licença-maternidade em 2009.",
        4: "Neutraliza ilações sobre familiares ao contra-atacar com fatos judiciais incontestáveis: a loja de chocolates da Kopenhagen e as 43 mentiras catalogadas.",
        5: "Liquida o show de palco sobre o 'Careca do INSS' ao desafiar Flávio a abrir imediatamente seus sigilos bancários e fiscais em rede nacional.",
        6: "Exibe a falsidade da acusação sobre familiares no exterior e expõe o contraste moral com os envolvidos em investigações reais da Polícia Federal.",
        7: "Destrói a narrativa de Vorcaro e Banco Master com documentação precisa, expondo a tentativa desesperada do oponente de criar um falso escândalo.",
        8: "Ponto alto do confronto direto: desmonta a farsa da Mansão do BRB, expõe os 1.512 depósitos em dinheiro vivo e desarticula a moralidade de fachada da oposição.",
        9: "Neutraliza a tentativa do adversário de monopolizar a segurança pública, acolhendo os policiais honestos e separando-os da milícia e do crime organizado.",
        10: "Desmascara o discurso armamentista ao provar que o adversário votou para raspar o número de munições, favorecendo facções que compram armas desviadas.",
        11: "Atrai os trabalhadores precarizados e a juventude que sofre na escala 6x1, expondo o histórico anti-trabalhador da família Bolsonaro.",
        12: "Enterra o modelo Milei ao mostrar que o 'choque liberal' dobrou a pobreza na Argentina, enquanto o Brasil recuperou emprego e dignidade.",
        13: "Reafirma a função social do BNDES e dos bancos públicos como motores do Minha Casa Minha Vida e do saneamento básico para a população carente.",
        14: "Substitui o terrorismo econômico do adversário pela realidade palpável: queda do desemprego, recorde de contratações formais e menor inflação acumulada.",
        15: "Desmonta a falácia do teto de gastos e demonstra que quem controla o preço da comida é o apoio à agricultura familiar e o estoque regulador da Conab.",
        16: "Encurrala Flávio na crise da saúde pública do Rio de Janeiro, evidenciando o loteamento político dos hospitais federais e a decadência do atendimento.",
        17: "Projeta estatura de estadista internacional, posicionando o Brasil na vanguarda da inteligência artificial, transição ecológica e inovação.",
        18: "Defende a soberania nacional e a industrialização local das reservas minerais, contrapondo o projeto entreguista do oponente.",
        19: "Liquida a falsa 'castração química' ao ridicularizar o 'plano do Cebolinha' e expor o telhado de vidro do oponente com o histórico de seu próprio vice.",
        20: "Fechamento magistral e emocionante: resgata o legado de tirar o Brasil da fome, projeta reconciliação e sela o compromisso de vida no último mandato."
    }

    for i, raw in enumerate(scenes_raw, 1):
        header_m = re.match(r'### Intera[çc][ãa]o (\d+\.\d+)\s*—\s*([^\n]+)', raw)
        num_str = header_m.group(1) if header_m else f"{i}"
        title = header_m.group(2).strip() if header_m else f"Interação {i}"

        tc_m = re.search(r'\[\[?(\d{2}:\d{2})\]?', raw)
        tc = tc_m.group(1) if tc_m else "00:00"

        if i <= 12:
            block = "BLOCO 1"
        elif i <= 16:
            block = "BLOCO 2"
        else:
            block = "BLOCO 3"

        is_direct = "Confronto Direto" in title or "Considerações Finais" in title
        if "Adriana" in raw or "Adriana Araújo" in title or "1.1" in num_str or "2.1" in num_str:
            opp_name = "Adriana Araújo"
            opp_role = "Mediadora / Jornalista Band"
            opp_key = "adriana"
        elif "Oinegue" in raw or "Eduardo Oinegue" in title or "1.2" in num_str or "3.1" in num_str:
            opp_name = "Eduardo Oinegue"
            opp_role = "Mediador / Jornalista Band"
            opp_key = "oinegue"
        else:
            opp_name = "Flávio Bolsonaro"
            opp_role = "Senador da República / Opositor"
            opp_key = "flavio"

        # Clean attack / question
        clean_attack_html = extract_clean_attack(raw)

        # Lula Response
        lula_m = re.search(r'#### ✍️ Sua Resposta Ideal[^\n]*\n\n(.*?)(?=\n####|\n###|\Z)', raw, re.DOTALL)
        if not lula_m:
            lula_m = re.search(r'#### .*?Resposta Ideal[^\n]*\n\n(.*?)(?=\n####|\n###|\Z)', raw, re.DOTALL)
        
        lula_text = lula_m.group(1).strip() if lula_m else ""

        dur_m = re.search(r'\[(.*?)\]', raw)
        dur = dur_m.group(1) if dur_m else "02:00"

        scenes.append({
            "index": i,
            "num_str": num_str,
            "title": title,
            "block": block,
            "tc": tc,
            "opp_name": opp_name,
            "opp_role": opp_role,
            "opp_key": opp_key,
            "is_direct": is_direct,
            "clean_attack_html": clean_attack_html,
            "lula_text": lula_text,
            "direction": stage_directions.get(i, "Olhar firme nos olhos do interlocutor. Postura presidencial de autoridade moral e voz serena."),
            "takeaway": tactical_takeaways.get(i, "Desarticula a tese do adversário com fatos objetivos e linguagem popular de TV."),
            "dur": dur
        })

    return scenes
