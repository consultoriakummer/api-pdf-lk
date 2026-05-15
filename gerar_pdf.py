import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

W, H = A4

# ── PALETA VERDE ─────────────────────────────────────────────────────────────
CREME         = colors.HexColor("#F4FAF4")
VERDE_ESCURO  = colors.HexColor("#2D5A3D")
VERDE_MEDIO   = colors.HexColor("#4A8C5C")
VERDE_CLARO   = colors.HexColor("#A8D5B5")
VERDE_BG      = colors.HexColor("#E8F5EC")
TEXTO_ESCURO  = colors.HexColor("#1A2E22")
TEXTO_MEDIO   = colors.HexColor("#3A5C47")
BRANCO        = colors.white
DOURADO       = colors.HexColor("#C8A84B")
CINZA_CLARO   = colors.HexColor("#E0E0E0")

def draw_bg(c):
    c.setFillColor(CREME)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_rect(c, x, y, w, h, fill=VERDE_BG, radius=4):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

def draw_header_bar(c, titulo, subtitulo=None):
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, H-34*mm, W, 34*mm, fill=1, stroke=0)
    c.setFillColor(VERDE_MEDIO)
    c.rect(0, H-34*mm, W, 6*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W/2, H-22*mm, titulo)
    if subtitulo:
        c.setFillColor(VERDE_CLARO)
        c.setFont("Helvetica", 9)
        c.drawCentredString(W/2, H-30*mm, subtitulo)

def rodape(c, num):
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
    c.setFillColor(VERDE_CLARO)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 5*mm, f"Luis Kummer Personal  •  MFIT Personal  •  {num}/6")

def linha_div(c, y):
    c.setStrokeColor(VERDE_CLARO)
    c.setLineWidth(0.8)
    c.line(20*mm, y, W-20*mm, y)

def wrap(c, texto, x, y, larg, size=10, cor=TEXTO_ESCURO, leading=15):
    st = ParagraphStyle("s", fontName="Helvetica", fontSize=size,
                        textColor=cor, leading=leading, alignment=TA_JUSTIFY)
    p = Paragraph(texto, st)
    p.wrapOn(c, larg, 999)
    p.drawOn(c, x, y - p.height)
    return y - p.height

def wrap_left(c, texto, x, y, larg, size=10, cor=TEXTO_ESCURO, leading=14):
    st = ParagraphStyle("s", fontName="Helvetica", fontSize=size,
                        textColor=cor, leading=leading, alignment=TA_LEFT)
    p = Paragraph(texto, st)
    p.wrapOn(c, larg, 999)
    p.drawOn(c, x, y - p.height)
    return y - p.height

def to_float(val):
    try:
        return float(str(val).replace(",", "."))
    except:
        return None

def calc_imc(peso, altura):
    p = to_float(peso)
    a = to_float(altura)
    if not p or not a:
        return None
    if a > 3:
        a = a / 100
    if a == 0:
        return None
    return round(p / (a * a), 1)

def class_imc(imc):
    v = to_float(imc)
    if v is None: return "Nao calculado"
    if v < 18.5: return "Abaixo do peso"
    if v < 25:   return "Peso normal"
    if v < 30:   return "Sobrepeso"
    if v < 35:   return "Obesidade grau I"
    if v < 40:   return "Obesidade grau II"
    return "Obesidade grau III"

def obj_texto(o):
    m = {
        "perder_peso": "Perda de peso",
        "ganhar_massa": "Ganho de massa muscular",
        "qualidade_vida": "Qualidade de vida",
        "definicao": "Definicao muscular",
        "definir e tonificar": "Definicao e tonificacao",
        "ganhar massa": "Ganho de massa muscular",
        "perder peso": "Perda de peso",
    }
    o_str = str(o).lower().strip() if o else ""
    return m.get(o_str, str(o) if o else "Nao informado")

def safe(val, sufixo=""):
    if val is None or str(val).strip() in ["", "None"]:
        return "Nao informado"
    return f"{val}{sufixo}"

# ── PÁGINA 1 — CAPA ──────────────────────────────────────────────────────────
def pag_capa(c, d):
    draw_bg(c)
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, H-65*mm, W, 65*mm, fill=1, stroke=0)
    c.setFillColor(VERDE_MEDIO)
    c.rect(0, H-65*mm, W, 6*mm, fill=1, stroke=0)
    c.setStrokeColor(VERDE_CLARO)
    c.setLineWidth(0.5)
    c.setDash(3, 3)
    c.line(15*mm, H-20*mm, 55*mm, H-20*mm)
    c.line(W-55*mm, H-20*mm, W-15*mm, H-20*mm)
    c.setDash()
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W/2, H-32*mm, "DIAGNOSTICO PERSONALIZADO")
    c.setFillColor(VERDE_CLARO)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H-44*mm, "Luis Kummer Personal  |  MFIT Personal")
    c.setFillColor(DOURADO)
    c.circle(W/2, H-56*mm, 3*mm, fill=1, stroke=0)

    nome = d.get("nome") or "Aluno(a)"
    c.setFillColor(VERDE_ESCURO)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, H-85*mm, f"Ola, {nome}!")
    c.setFillColor(TEXTO_MEDIO)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H-96*mm, "Preparamos este diagnostico exclusivo com base nas suas respostas.")
    linha_div(c, H-103*mm)

    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    caixas = [
        ("Objetivo",    obj_texto(d.get("objetivo", ""))),
        ("IMC",         safe(imc_val)),
        ("Compromisso", f"{safe(d.get('compro'))}/10"),
    ]
    cw = (W - 44*mm) / 3
    for i, (lbl, val) in enumerate(caixas):
        cx = 22*mm + i * cw
        draw_rect(c, cx, H-168*mm, cw-4*mm, 48*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(cx, H-122*mm, cw-4*mm, 4*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx+(cw-4*mm)/2, H-134*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(cx+(cw-4*mm)/2, H-150*mm, str(val)[:22])

    draw_rect(c, 20*mm, H-252*mm, W-40*mm, 62*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.roundRect(20*mm, H-192*mm, W-40*mm, 4*mm, 2, fill=1, stroke=0)
    c.setFillColor(VERDE_ESCURO)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W/2, H-205*mm, "Sua transformacao comeca com um passo.")
    wrap(c, "Este diagnostico foi elaborado por Luis Kummer com base no seu perfil individual. "
         "Cada protocolo e criado do zero, respeitando seu corpo, sua rotina e seus objetivos. "
         "Vamos juntos nessa jornada!",
         25*mm, H-218*mm, W-50*mm, size=10)
    rodape(c, 1)
    c.showPage()

# ── PÁGINA 2 — BIOMÉTRICO ────────────────────────────────────────────────────
def pag_bio(c, d):
    draw_bg(c)
    draw_header_bar(c, "DADOS BIOMETRICOS", "Seu perfil fisico completo")

    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    campos = [
        ("Peso atual",    safe(d.get("peso"), " kg")),
        ("Altura",        safe(d.get("altura"), " cm")),
        ("Idade",         safe(d.get("idade"), " anos")),
        ("Peso objetivo", safe(d.get("peso_obj"), " kg")),
        ("IMC",           safe(imc_val)),
        ("Classificacao", class_imc(imc_val)),
    ]
    cw = (W - 44*mm) / 2
    for i, (lbl, val) in enumerate(campos):
        col = i % 2
        row = i // 2
        cx = 22*mm + col * cw
        cy = H - 46*mm - row * 36*mm
        draw_rect(c, cx, cy-28*mm, cw-5*mm, 30*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(cx, cy, cw-5*mm, 4*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_MEDIO)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(cx+4*mm, cy-10*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(cx+4*mm, cy-22*mm, str(val)[:28])

    # ── BARRA IMC COM MARCADOR ──
    y_b = H - 210*mm
    draw_rect(c, 20*mm, y_b-28*mm, W-40*mm, 52*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(24*mm, y_b+18*mm, "Faixa de IMC:")

    segs = [
        (4.5,  colors.HexColor("#5B9BD5"), "< 18.5"),
        (6.5,  colors.HexColor("#70AD47"), "18.5-25"),
        (5.0,  colors.HexColor("#FFC000"), "25-30"),
        (5.0,  colors.HexColor("#FF7C00"), "30-35"),
        (4.0,  colors.HexColor("#FF0000"), "> 35"),
    ]
    total = sum(s[0] for s in segs)
    bw = W - 50*mm
    bh = 10*mm
    y_barra = y_b + 4*mm
    xpos = 25*mm
    for val_s, cor_s, label_s in segs:
        sw = bw * val_s / total
        c.setFillColor(cor_s)
        c.rect(xpos, y_barra, sw, bh, fill=1, stroke=0)
        if sw > 16*mm:
            c.setFillColor(BRANCO)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(xpos + sw/2, y_barra + 3*mm, label_s)
        xpos += sw
    c.setStrokeColor(VERDE_ESCURO)
    c.setLineWidth(1)
    c.roundRect(25*mm, y_barra, bw, bh, 3, fill=0, stroke=1)

    # marcador
    imc_f = to_float(imc_val)
    if imc_f is not None:
        imc_capped = min(max(imc_f, 15.0), 42.0)
        imc_pos_ratio = (imc_capped - 15.0) / 27.0
        marker_x = 25*mm + bw * imc_pos_ratio

        # triangulo apontando para baixo na barra
        tri_y_top = y_barra + bh + 1*mm
        tri_h = 4*mm
        tri_w = 3*mm
        path = c.beginPath()
        path.moveTo(marker_x, tri_y_top)
        path.lineTo(marker_x - tri_w, tri_y_top + tri_h)
        path.lineTo(marker_x + tri_w, tri_y_top + tri_h)
        path.close()
        c.setFillColor(VERDE_ESCURO)
        c.drawPath(path, fill=1, stroke=0)

        # linha vertical na barra
        c.setStrokeColor(VERDE_ESCURO)
        c.setLineWidth(1.5)
        c.setDash(2, 2)
        c.line(marker_x, y_barra, marker_x, y_barra + bh)
        c.setDash()

        # label
        c.setFillColor(VERDE_ESCURO)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(marker_x, tri_y_top + tri_h + 2*mm, f"Voce: {imc_f}")

    rodape(c, 2)
    c.showPage()

# ── PÁGINA 3 — META E HÁBITOS ────────────────────────────────────────────────
def pag_meta(c, d):
    draw_bg(c)
    draw_header_bar(c, "META E HABITOS", "Seu estilo de vida e rotina atual")
    itens = [
        ("Objetivo principal",  obj_texto(d.get("objetivo", ""))),
        ("Alimentacao",         safe(d.get("alimentacao"))),
        ("Exercicio atual",     safe(d.get("exercicio"))),
        ("Tempo de treino",     safe(d.get("tempo_treino"))),
        ("Cardio",              safe(d.get("cardio"))),
        ("Nivel de estresse",   safe(d.get("estresse"))),
        ("Comprometimento",     f"{safe(d.get('compro'))}/10"),
        ("Limitacoes",          safe(d.get("limitacao"))),
    ]
    y = H - 44*mm
    for lbl, val in itens:
        draw_rect(c, 20*mm, y-15*mm, W-40*mm, 17*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(20*mm, y-15*mm, 5*mm, 17*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_MEDIO)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(29*mm, y-5*mm, lbl.upper() + ":")
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica", 10)
        c.drawString(90*mm, y-5*mm, str(val)[:55])
        y -= 22*mm
    rodape(c, 3)
    c.showPage()

# ── PÁGINA 4 — ANÁLISE VISUAL DO PERFIL ─────────────────────────────────────
def pag_perfil(c, d):
    draw_bg(c)
    draw_header_bar(c, "ANALISE DO SEU PERFIL", "O que seus dados revelam sobre voce")

    nome     = d.get("nome") or "Aluno(a)"
    obj      = obj_texto(d.get("objetivo", ""))
    comp_raw = to_float(d.get("compro")) or 0
    imc_val  = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    imc_f    = to_float(imc_val)
    lim      = str(d.get("limitacao") or "Nenhuma")
    med      = str(d.get("medicamentos") or "Nenhum")
    alim     = safe(d.get("alimentacao"))
    exerc    = safe(d.get("exercicio"))
    estresse = safe(d.get("estresse"))

    c.setFillColor(VERDE_ESCURO)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W/2, H-42*mm, f"Aqui esta o que identificamos sobre {nome}:")

    # 4 cards visuais 2x2
    card_w = (W - 46*mm) / 2
    card_h = 38*mm
    cards = [
        ("OBJETIVO",      obj,                    f"Compromisso: {int(comp_raw)}/10", VERDE_ESCURO),
        ("PERFIL FISICO", class_imc(imc_f),       f"IMC atual: {imc_val or '–'}",    VERDE_MEDIO),
        ("ROTINA",        exerc,                  f"Treino: {safe(d.get('tempo_treino'))}", VERDE_ESCURO),
        ("ALIMENTACAO",   alim,                   f"Estresse: {estresse}/10",         VERDE_MEDIO),
    ]
    y_cards = H - 52*mm
    for i, (tit, val, det, cor) in enumerate(cards):
        col = i % 2
        row = i // 2
        cx = 22*mm + col * (card_w + 4*mm)
        cy = y_cards - row * (card_h + 5*mm)
        draw_rect(c, cx, cy-card_h, card_w, card_h, fill=VERDE_BG)
        c.setFillColor(cor)
        c.roundRect(cx, cy-5*mm, card_w, 5*mm, 2, fill=1, stroke=0)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx+card_w/2, cy-3*mm, tit)
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(cx+card_w/2, cy-18*mm, str(val)[:30])
        c.setFillColor(TEXTO_MEDIO)
        c.setFont("Helvetica", 8)
        c.drawCentredString(cx+card_w/2, cy-28*mm, str(det)[:38])

    # barra de comprometimento
    y_comp = H - 148*mm
    draw_rect(c, 20*mm, y_comp-20*mm, W-40*mm, 28*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(24*mm, y_comp+3*mm, "Nivel de comprometimento:")
    bar_w = W - 80*mm
    bar_x = 24*mm
    bar_y = y_comp - 14*mm
    c.setFillColor(CINZA_CLARO)
    c.roundRect(bar_x, bar_y, bar_w, 8*mm, 4, fill=1, stroke=0)
    pct = min(comp_raw / 10.0, 1.0)
    fill_cor = VERDE_ESCURO if pct >= 0.7 else colors.HexColor("#FFC000")
    c.setFillColor(fill_cor)
    c.roundRect(bar_x, bar_y, bar_w * pct, 8*mm, 4, fill=1, stroke=0)
    if pct > 0.15:
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(bar_x + 3*mm, bar_y + 2*mm, f"{int(comp_raw)}/10")
    c.setFillColor(VERDE_ESCURO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(bar_x + bar_w + 3*mm, bar_y + 2*mm,
                 "Excelente!" if pct >= 0.8 else ("Otimo!" if pct >= 0.6 else "Vamos la!"))

    # alertas limitacao / medicamento
    y_obs = y_comp - 28*mm
    obs_items = []
    if lim.lower() not in ["nenhuma","nao","none","","nao informado"]:
        obs_items.append(("Limitacao fisica", lim, colors.HexColor("#E07B00")))
    if med.lower() not in ["nenhum","nao","none","","nao informado"]:
        obs_items.append(("Medicamento em uso", med, colors.HexColor("#5B9BD5")))
    for tit_obs, val_obs, cor_obs in obs_items:
        draw_rect(c, 20*mm, y_obs-14*mm, W-40*mm, 16*mm, fill=VERDE_BG)
        c.setFillColor(cor_obs)
        c.roundRect(20*mm, y_obs-14*mm, 5*mm, 16*mm, 2, fill=1, stroke=0)
        c.setFillColor(cor_obs)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(29*mm, y_obs-5*mm, tit_obs.upper() + ":")
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica", 10)
        c.drawString(78*mm, y_obs-5*mm, str(val_obs)[:58])
        y_obs -= 20*mm

    rodape(c, 4)
    c.showPage()

# ── PÁGINA 5 — OFERTA / PLANOS ───────────────────────────────────────────────
def pag_oferta(c, d):
    draw_bg(c)
    draw_header_bar(c, "SEU PROTOCOLO PERSONALIZADO", "Escolha o plano ideal para voce")

    nome     = d.get("nome") or "voce"
    obj      = obj_texto(d.get("objetivo", ""))
    comp_raw = to_float(d.get("compro")) or 0

    if comp_raw >= 8:
        nivel_txt = "seu alto nivel de comprometimento"
    elif comp_raw >= 5:
        nivel_txt = "seu comprometimento"
    else:
        nivel_txt = "seu potencial"

    draw_rect(c, 20*mm, H-68*mm, W-40*mm, 26*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.roundRect(20*mm, H-44*mm, W-40*mm, 4*mm, 2, fill=1, stroke=0)
    texto_p = (
        f"Com base no seu objetivo de <b>{obj}</b> e em {nivel_txt} ({int(comp_raw)}/10), "
        f"selecionamos os protocolos abaixo. Cada um e montado do zero pelo Luis Kummer, "
        f"com exercicios em video, suporte direto e plano alimentar adaptado ao seu perfil."
    )
    wrap(c, texto_p, 25*mm, H-50*mm, W-50*mm, size=10)

    planos = [
        ("Individual  -  1 Protocolo", "60 dias de acompanhamento", "R$ 119",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636"),
        ("Dupla  -  1 Protocolo", "60 dias para voce + 1 pessoa", "R$ 207",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112637&page=112636"),
        ("Individual  -  3 Protocolos", "180 dias de acompanhamento", "R$ 297",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112638&page=112636"),
        ("Dupla  -  3 Protocolos", "180 dias para voce + 1 pessoa", "R$ 479",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112639&page=112636"),
    ]
    ph = 44*mm
    gap = 4*mm
    y_start = H - 75*mm
    for i, (titulo, desc, preco, url) in enumerate(planos):
        y = y_start - i*(ph+gap)
        draw_rect(c, 20*mm, y-ph, W-40*mm, ph, fill=VERDE_BG)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(20*mm, y-ph, 6*mm, ph, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30*mm, y-12*mm, titulo)
        c.setFillColor(TEXTO_MEDIO)
        c.setFont("Helvetica", 10)
        c.drawString(30*mm, y-22*mm, desc)
        c.setFillColor(DOURADO)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(30*mm, y-36*mm, preco)
        bx = W-72*mm; bw = 48*mm; bh = 11*mm
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(bx, y-ph+10*mm, bw, bh, 3, fill=1, stroke=0)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(bx+bw/2, y-ph+15*mm, "Quero este plano ->")
        c.linkURL(url, (bx, y-ph+10*mm, bx+bw, y-ph+21*mm), relative=0)

    rodape(c, 5)
    c.showPage()

# ── PÁGINA 6 — DEPOIMENTOS ───────────────────────────────────────────────────
def pag_depoimentos(c, d):
    draw_bg(c)
    draw_header_bar(c, "RESULTADOS REAIS", "Quem ja transformou a vida com o protocolo Luis Kummer")
    deps = [
        ("Ana Paula, 34 anos",
         "Perdi 8kg em 60 dias seguindo o protocolo do Luis. O acompanhamento pelo app fez toda a diferenca!"),
        ("Marcos e Juliana",
         "Fizemos o plano dupla e foi incrivel! Nos motivamos juntos e os resultados vieram muito rapido."),
        ("Fernanda, 28 anos",
         "Nunca pensei que conseguiria manter uma rotina de treinos. O protocolo e pratico e super eficiente!"),
        ("Cristiane, 41 anos",
         "Com duas filhas e trabalho nao sobrava tempo. O Luis montou um treino perfeito para minha realidade."),
    ]
    y = H - 46*mm
    for nome, dep in deps:
        h_box = 36*mm
        draw_rect(c, 20*mm, y-h_box, W-40*mm, h_box, fill=VERDE_BG)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(20*mm, y-h_box, 6*mm, h_box, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_CLARO)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(30*mm, y-8*mm, '"')
        c.setFillColor(VERDE_ESCURO)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(42*mm, y-9*mm, nome)
        wrap_left(c, dep, 30*mm, y-16*mm, W-54*mm, size=10, cor=TEXTO_ESCURO)
        y -= h_box + 6*mm
    rodape(c, 6)
    c.showPage()

# ── FUNÇÃO PRINCIPAL ─────────────────────────────────────────────────────────
def gerar_pdf_diagnostico(dados):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Diagnostico Personalizado - Luis Kummer")
    if not dados.get("imc"):
        imc_calc = calc_imc(dados.get("peso"), dados.get("altura"))
        if imc_calc:
            dados["imc"] = imc_calc
    pag_capa(c, dados)
    pag_bio(c, dados)
    pag_meta(c, dados)
    pag_perfil(c, dados)
    pag_oferta(c, dados)
    pag_depoimentos(c, dados)
    c.save()
    buf.seek(0)
    return buf.read()

if __name__ == "__main__":
    dados_teste = {
        "nome": "Samara",
        "objetivo": "perder_peso",
        "sexo": "Feminino",
        "peso": "72", "altura": "163", "idade": "32", "peso_obj": "62",
        "imc": None, "limitacao": "joelho", "medicamentos": "nenhum",
        "exercicio": "treina 2x/semana", "tempo_treino": "30 a 45 min",
        "cardio": "caminhada", "alimentacao": "alimentacao razoavel",
        "compro": "9", "estresse": "6",
    }
    pdf_bytes = gerar_pdf_diagnostico(dados_teste)
    with open("/mnt/user-data/outputs/diagnostico_v2.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("OK")
