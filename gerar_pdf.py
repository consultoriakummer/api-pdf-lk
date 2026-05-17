import io, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

W, H = A4
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOJI_DIR = os.path.join(BASE_DIR, "emojis")

# ── EMOJI HELPER ──────────────────────────────────────────────────────────────
def draw_emoji(c, nome, x, y, size=5):
    """Desenha emoji como imagem PNG. size em mm."""
    path = os.path.join(EMOJI_DIR, f"{nome}.png")
    if os.path.exists(path):
        s = size * mm
        c.drawImage(path, x, y - s, width=s, height=s,
                    preserveAspectRatio=True, mask='auto')
        return s
    return 0

# ── PALETA ────────────────────────────────────────────────────────────────────
FUNDO_ESCURO  = colors.HexColor("#0D1F0F")
CARD_ESCURO   = colors.HexColor("#152918")
CARD_MEDIO_E  = colors.HexColor("#1E3D22")

FUNDO_CLARO   = colors.HexColor("#F5F9F5")
CARD_CLARO    = colors.HexColor("#E8F5EC")
CARD_VERDE    = colors.HexColor("#D4EDD9")

VERDE_LIMA    = colors.HexColor("#5BBF2A")
VERDE_ESCURO  = colors.HexColor("#2D5A1B")
VERDE_MEDIO   = colors.HexColor("#4A8C5C")
VERDE_CLARO   = colors.HexColor("#A8D5B5")
BRANCO        = colors.white
TEXTO_ESCURO  = colors.HexColor("#1A2E12")
TEXTO_MEDIO   = colors.HexColor("#3A5C27")
CINZA_TEXTO   = colors.HexColor("#5A6B5A")
DOURADO       = colors.HexColor("#C8A84B")
LARANJA       = colors.HexColor("#E07B00")
AZUL          = colors.HexColor("#3A7BBF")
VERMELHO      = colors.HexColor("#C0392B")
AMARELO       = colors.HexColor("#F0C040")

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def _registrar_fontes():
    base = os.path.dirname(os.path.abspath(__file__))
    try:
        pdfmetrics.registerFont(TTFont("DVSans",     os.path.join(base, "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DVSans-Bold",os.path.join(base, "DejaVuSans-Bold.ttf")))
        return "DVSans", "DVSans-Bold"
    except:
        return "Helvetica", "Helvetica-Bold"

FONT_N, FONT_B = _registrar_fontes()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def draw_bg_dark(c):
    c.setFillColor(FUNDO_ESCURO)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_bg_light(c):
    c.setFillColor(FUNDO_CLARO)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_card(c, x, y, w, h, fill=CARD_CLARO, radius=5):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

# FIX: header aumentado para 38mm e subtítulo reposicionado
def draw_header_light(c, emoji_nome, titulo, subtitulo=None):
    HEADER_H = 38*mm
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)
    c.setFillColor(VERDE_LIMA)
    c.rect(0, H - HEADER_H, W, 3*mm, fill=1, stroke=0)
    title_y = H - 18*mm
    # emoji como imagem à esquerda do título
    emoji_size = 7*mm
    title_text_w = len(titulo) * 5  # estimativa largura
    start_x = W/2 - title_text_w/2 - emoji_size - 2*mm
    draw_emoji(c, emoji_nome, start_x, title_y + emoji_size*0.15, size=7)
    c.setFillColor(BRANCO)
    c.setFont(FONT_B, 17)
    c.drawCentredString(W/2 + emoji_size/2, title_y, titulo)
    if subtitulo:
        c.setFillColor(VERDE_CLARO)
        c.setFont(FONT_N, 11)
        c.drawCentredString(W/2, title_y - 12*mm, subtitulo)

HEADER_BOTTOM = lambda: H - 38*mm  # y onde o header termina

def rodape(c, num, total=8, dark=False):
    bg = CARD_ESCURO if dark else VERDE_ESCURO
    c.setFillColor(bg)
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(VERDE_LIMA)
    c.setFont(FONT_N, 8)
    c.drawString(20*mm, 4*mm, "Luis Kummer Personal Trainer")
    c.setFillColor(VERDE_CLARO)
    c.drawRightString(W-20*mm, 4*mm, f"{num} / {total}")

def wrap(c, texto, x, y, larg, size=10, cor=TEXTO_ESCURO, leading=14, align=TA_JUSTIFY):
    st = ParagraphStyle("s", fontName=FONT_N, fontSize=size,
                        textColor=cor, leading=leading, alignment=align)
    p = Paragraph(texto, st)
    p.wrapOn(c, larg, 999)
    p.drawOn(c, x, y - p.height)
    return y - p.height

def to_float(val):
    try: return float(str(val).replace(",","."))
    except: return None

def calc_imc(peso, altura):
    p = to_float(peso); a = to_float(altura)
    if not p or not a: return None
    if a > 3: a = a/100
    if a == 0: return None
    return round(p/(a*a), 1)

def class_imc(imc):
    v = to_float(imc)
    if v is None: return "Não calculado"
    if v < 18.5: return "Abaixo do peso"
    if v < 25:   return "Peso normal"
    if v < 30:   return "Sobrepeso"
    if v < 35:   return "Obesidade I"
    if v < 40:   return "Obesidade II"
    return "Obesidade III"

# FIX: cor baseada no IMC
def cor_imc(imc):
    v = to_float(imc)
    if v is None: return CINZA_TEXTO
    if v < 18.5: return AZUL          # abaixo do peso → azul
    if v < 25:   return VERDE_ESCURO  # normal → verde
    if v < 30:   return AMARELO       # sobrepeso → amarelo
    if v < 35:   return LARANJA       # obesidade I → laranja
    return VERMELHO                    # obesidade II/III → vermelho

# FIX: cor baseada no status OMS
def cor_oms(status):
    return {
        "excelente":    VERDE_ESCURO,
        "adequado":     VERDE_LIMA,
        "parcial":      LARANJA,
        "insuficiente": VERMELHO,
    }.get(status, VERDE_MEDIO)

def obj_texto(o):
    m = {"perder_peso":"Perda de peso","ganhar_massa":"Ganho de massa",
         "qualidade_vida":"Qualidade de vida","definição":"Definição muscular",
         "definir e tonificar":"Definição e tonificação",
         "ganhar massa":"Ganho de massa","perder peso":"Perda de peso"}
    return m.get(str(o).lower().strip() if o else "", str(o) if o else "Não informado")

def safe(val, sufixo=""):
    if val is None or str(val).strip() in ["","None"]: return "Não informado"
    return f"{val}{sufixo}"

def data_hoje():
    meses = ["janeiro","fevereiro","marco","abril","maio","junho",
             "julho","agosto","setembro","outubro","novembro","dezembro"]
    d = datetime.now()
    return f"{d.day} de {meses[d.month-1]} de {d.year}"

def avaliar_oms(exercicio, tempo_treino, cardio, tempo_cardio):
    es = str(exercicio or "").lower(); ts = str(tempo_treino or "").lower()
    cs = str(cardio or "").lower();   ct = str(tempo_cardio or "").lower()
    freq = 0
    if "1x" in es: freq=1
    elif "2x" in es or "2-3" in es: freq=2
    elif "3x" in es or "3-4" in es: freq=3
    elif "4x" in es or "4-5" in es: freq=4
    elif "5x" in es or "todos" in es: freq=5
    mt = 0
    if "menos de 30" in ts: mt=20
    elif "30" in ts and "45" in ts: mt=37
    elif "45" in ts: mt=52
    elif "60" in ts: mt=60
    elif "mais de 60" in ts: mt=75
    mc = 0
    if "não" not in cs and cs not in ["","none","não informado"]:
        if "menos de 20" in ct: mc=30
        elif "20" in ct: mc=40
        elif "30" in ct: mc=60
        elif "45" in ct: mc=90
        elif "60" in ct: mc=120
    total = freq*mt + mc
    if total == 0:    st="insuficiente"
    elif total < 75:  st="insuficiente"
    elif total < 150: st="parcial"
    elif total<=300:  st="adequado"
    else:             st="excelente"
    return total, st

def meta_personalizada(dados):
    objetivo = str(dados.get("objetivo") or "").lower()
    peso     = to_float(dados.get("peso"))
    peso_obj = to_float(dados.get("peso_obj"))
    imc      = to_float(dados.get("imc")) or calc_imc(dados.get("peso"),dados.get("altura"))
    exerc    = str(dados.get("exercicio") or "").lower()
    estresse = to_float(dados.get("estresse")) or 5
    sexo     = str(dados.get("sexo") or "").lower()
    eh_emag  = ("perder" in objetivo or "peso" in objetivo or
                (peso and peso_obj and peso-peso_obj > 2))
    eh_massa = "massa" in objetivo or "ganhar" in objetivo
    eh_def   = "defin" in objetivo or "tonic" in objetivo
    if eh_emag and peso and peso_obj:
        diff = peso - peso_obj
        if diff <= 0: return {"tipo":"emag_ok"}
        imc_v = to_float(imc) or 25
        if imc_v < 25: taxa=0.3
        elif imc_v < 30: taxa=0.5
        elif imc_v < 35: taxa=0.75
        elif imc_v < 40: taxa=1.0
        else: taxa=1.2
        meses = max(1, round((diff/taxa)/4.3))
        return {"tipo":"emagrecimento","diff":round(diff,1),"taxa":taxa,
                "meses":meses,"imc":imc_v,"peso_atual":peso,"peso_obj":peso_obj}
    elif eh_massa:
        if any(x in exerc for x in ["4x","5x","todos"]): gmin=0.1;gmax=0.3
        elif any(x in exerc for x in ["3x","2-3","3-4"]): gmin=0.3;gmax=0.5
        else: gmin=0.5;gmax=0.8
        if "mascul" in sexo or "homem" in sexo:
            gmin=round(gmin*1.5,1);gmax=round(gmax*1.5,1)
        return {"tipo":"massa","g3min":round(gmin*3,1),"g3max":round(gmax*3,1),
                "g6min":round(gmin*6,1),"g6max":round(gmax*6,1)}
    elif eh_def:
        freq=0
        for x,v in [("1x",1),("2x",2),("3x",3),("4x",4),("5x",5)]:
            if x in exerc: freq=v; break
        return {"tipo":"definicao","freq_atual":freq,"freq_meta":min(freq+2,5),
                "estresse_atual":int(estresse),"estresse_meta":max(int(estresse)-3,2)}
    else:
        freq=0
        for x,v in [("1x",1),("2x",2),("3x",3),("4x",4),("5x",5)]:
            if x in exerc: freq=v; break
        return {"tipo":"qualidade","freq_atual":freq,"freq_meta":min(freq+2,5),
                "estresse_atual":int(estresse),"estresse_meta":max(int(estresse)-2,2)}

# ── PÁGINA 1 — CAPA (escura) ──────────────────────────────────────────────────
def pag_capa(c, d):
    draw_bg_dark(c)
    nome = d.get("nome") or "Aluno"
    obj  = obj_texto(d.get("objetivo",""))
    imc_val = d.get("imc") or calc_imc(d.get("peso"),d.get("altura"))
    meta = meta_personalizada(d)

    c.setFillColor(VERDE_LIMA)
    c.rect(0, H-4*mm, W, 4*mm, fill=1, stroke=0)

    base = BASE_DIR
    logo_path = os.path.join(base, "logo_sem_fundo.png")
    if os.path.exists(logo_path):
        lw = 70*mm; lh = 70*mm
        c.drawImage(logo_path, W/2 - lw/2, H-78*mm,
                    width=lw, height=lh, preserveAspectRatio=True, mask='auto')

    c.setFillColor(CARD_MEDIO_E)
    c.rect(0, H-82*mm, W, 3*mm, fill=1, stroke=0)

    c.setFillColor(VERDE_CLARO)
    c.setFont(FONT_B, 14)
    c.drawString(20*mm, H-95*mm, "CRIADO EXCLUSIVAMENTE PARA")
    c.setFillColor(BRANCO)
    c.setFont(FONT_B, 44)
    c.drawString(20*mm, H-126*mm, nome)

    c.setFillColor(VERDE_LIMA)
    c.setFont(FONT_B, 19)
    if meta.get("tipo") == "emagrecimento":
        c.drawString(20*mm, H-136*mm, f"Meta: Perder {meta['diff']} kg")
    elif meta.get("tipo") == "massa":
        c.drawString(20*mm, H-136*mm, f"Meta: Ganhar massa muscular")
    else:
        c.drawString(20*mm, H-136*mm, f"Meta: {obj}")

    c.setFont(FONT_N, 11)
    c.drawString(20*mm, H-152*mm, f"Baseado nas suas respostas  •  {data_hoje()}")

    c.setStrokeColor(CARD_MEDIO_E)
    c.setLineWidth(1)
    c.line(20*mm, H-155*mm, W-20*mm, H-155*mm)

    if meta.get("tipo") == "emagrecimento":
        cols = [
            (str(int(meta["peso_atual"])), "kg", "HOJE"),
            (str(int(meta["peso_obj"])),   "kg", "META"),
            (str(meta["meses"]),           "meses" if meta["meses"]>1 else "mes", "ESTIMATIVA"),
        ]
    elif meta.get("tipo") == "massa":
        cols = [
            (f"{meta['g3min']}-{meta['g3max']}", "kg", "3 MESES"),
            (f"{meta['g6min']}-{meta['g6max']}", "kg", "6 MESES"),
            (safe(d.get("compro")), "/10", "COMPROMISSO"),
        ]
    else:
        cols = [
            (safe(d.get("peso"), ""), "kg", "PESO ATUAL"),
            (str(imc_val or "–"), "",  "IMC"),
            (safe(d.get("compro")), "/10", "COMPROMISSO"),
        ]

    col_w = (W - 40*mm) / 3
    y_num = H - 167*mm
    for i, (num, unid, label) in enumerate(cols):
        cx = 20*mm + i * col_w
        if i > 0:
            c.setStrokeColor(CARD_MEDIO_E)
            c.setLineWidth(1)
            c.line(cx, y_num+5*mm, cx, y_num-35*mm)
        c.setFillColor(BRANCO)
        c.setFont(FONT_B, 38)
        c.drawCentredString(cx + col_w/2, y_num-16*mm, num)
        c.setFillColor(VERDE_CLARO)
        c.setFont(FONT_N, 11)
        c.drawCentredString(cx + col_w/2, y_num-28*mm, unid)
        c.setFillColor(VERDE_CLARO)
        c.setFont(FONT_B, 9)
        c.drawCentredString(cx + col_w/2, y_num-38*mm, label)

    c.setStrokeColor(CARD_MEDIO_E)
    c.setLineWidth(1)
    c.line(20*mm, H-210*mm, W-20*mm, H-210*mm)

    c.setFillColor(CINZA_TEXTO)
    c.setFont(FONT_N, 8)
    c.drawCentredString(W/2, H-218*mm,
        "Este diagnostico e baseado nas suas respostas e nao substitui avaliacao medica.")

    rodape(c, 1, dark=True)
    c.showPage()

# ── PÁGINA 2 — DADOS BIOMÉTRICOS ─────────────────────────────────────────────
def pag_bio(c, d):
    draw_bg_light(c)
    draw_header_light(c, "barras", "SEÇÃO 1 — Seu Diagnóstico",
                      "Análise completa dos seus dados biométricos")

    imc_val = d.get("imc") or calc_imc(d.get("peso"),d.get("altura"))
    imc_f   = to_float(imc_val)
    COR_IMC = cor_imc(imc_f)

    # FIX: começar cards logo abaixo do header (38mm) com margem de 5mm
    y_start = HEADER_BOTTOM() - 5*mm

    # 4 cards superiores
    campos = [
        ("balanca", safe(d.get("peso"),"kg"), "PESO ATUAL"),
        ("regua", safe(d.get("altura"),"cm"), "ALTURA"),
        ("bolo", safe(d.get("idade")," anos"), "IDADE"),
        ("alvo", safe(d.get("peso_obj"),"kg"), "PESO OBJETIVO"),
    ]
    cw = (W-44*mm)/2
    for i,(emoji,val,lbl) in enumerate(campos):
        col=i%2; row=i//2
        cx=22*mm+col*cw; cy=y_start - row*30*mm
        draw_card(c, cx, cy-26*mm, cw-4*mm, 27*mm, fill=CARD_CLARO)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(cx, cy, cw-4*mm, 3*mm, 2, fill=1, stroke=0)
        draw_emoji(c, emoji, cx+3*mm, cy-4*mm, size=6)
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 14)
        c.drawString(cx+12*mm, cy-10*mm, str(val))
        c.setFillColor(CINZA_TEXTO)
        c.setFont(FONT_N, 10)
        c.drawString(cx+3*mm, cy-21*mm, lbl)

    # ── BARRA IMC ──
    # FIX: posicionado logo abaixo dos 4 cards (2 linhas × 30mm + gap)
    y_imc = y_start - 60*mm - 8*mm
    draw_card(c, 20*mm, y_imc-52*mm, W-40*mm, 56*mm, fill=CARD_CLARO)
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 13)
    c.drawString(24*mm, y_imc-7*mm, "ÍNDICE DE MASSA CORPORAL (IMC)")

    segs = [
        (4.5, colors.HexColor("#5B9BD5"), "BAIXO"),
        (6.5, colors.HexColor("#70AD47"), "NORMAL"),
        (5.0, colors.HexColor("#FFC000"), "SOBREPESO"),
        (5.0, colors.HexColor("#FF7C00"), "OBESO"),
        (4.0, colors.HexColor("#FF0000"), "OB.III"),
    ]
    total_s = sum(s[0] for s in segs)
    bw = W-50*mm; bh = 10*mm; y_bar = y_imc-24*mm; xp = 25*mm
    for vs,cs,ls in segs:
        sw = bw*vs/total_s
        c.setFillColor(cs)
        c.rect(xp, y_bar, sw, bh, fill=1, stroke=0)
        if sw > 14*mm:
            c.setFillColor(BRANCO)
            c.setFont(FONT_B, 7)
            c.drawCentredString(xp+sw/2, y_bar+3*mm, ls)
        xp += sw
    c.setStrokeColor(VERDE_ESCURO); c.setLineWidth(1)
    c.roundRect(25*mm, y_bar, bw, bh, 3, fill=0, stroke=1)

    # FIX: marcador IMC abaixo da barra, triângulo apontando para cima
    if imc_f:
        ratio = (min(max(imc_f,15.0),42.0)-15.0)/27.0
        mx = 25*mm + bw*ratio
        # triângulo apontando para cima, abaixo da barra
        path = c.beginPath()
        path.moveTo(mx, y_bar - 2*mm)
        path.lineTo(mx - 3*mm, y_bar - 7*mm)
        path.lineTo(mx + 3*mm, y_bar - 7*mm)
        path.close()
        c.setFillColor(COR_IMC); c.drawPath(path, fill=1, stroke=0)
        c.setFillColor(COR_IMC); c.setFont(FONT_B, 9)
        c.drawCentredString(mx, y_bar - 10*mm, f"Você: {imc_f}")

    # classificação abaixo da barra com cor dinâmica
    c.setFillColor(COR_IMC); c.setFont(FONT_B, 13)
    c.drawString(24*mm, y_imc-41*mm, class_imc(imc_val))
    c.setFillColor(CINZA_TEXTO); c.setFont(FONT_N, 10)
    c.drawString(24*mm, y_imc-49*mm, "Ideal: 18,5 a 24,9")

    # ── CARD META ──
    y_meta = y_imc - 62*mm
    meta = meta_personalizada(d)
    tipo = meta.get("tipo","")

    if tipo == "emagrecimento":
        draw_card(c, 20*mm, y_meta-55*mm, W-40*mm, 58*mm, fill=VERDE_ESCURO)
        draw_emoji(c, "musculo", W/2 - 42*mm, y_meta-1*mm, size=5)
        c.setFillColor(VERDE_LIMA); c.setFont(FONT_B, 9)
        c.drawString(W/2 - 34*mm, y_meta-6*mm, "SUA META DE EMAGRECIMENTO")
        cdata = [
            (str(int(meta["peso_atual"])), "kg", "HOJE"),
            (str(int(meta["peso_obj"])), "kg", "META"),
            (f"{meta['meses']}", "meses", "ESTIMATIVA"),
        ]
        cw3 = (W-40*mm)/3
        for i,(v,u,l) in enumerate(cdata):
            cx3 = 20*mm + i*cw3
            if i>0:
                c.setStrokeColor(CARD_MEDIO_E); c.setLineWidth(0.5)
                c.line(cx3, y_meta-15*mm, cx3, y_meta-50*mm)
            c.setFillColor(BRANCO); c.setFont(FONT_B, 26)
            c.drawCentredString(cx3+cw3/2, y_meta-30*mm, v)
            c.setFillColor(VERDE_CLARO); c.setFont(FONT_N, 9)
            c.drawCentredString(cx3+cw3/2, y_meta-39*mm, u)
            c.setFillColor(colors.HexColor("#888888")); c.setFont(FONT_B, 7)
            c.drawCentredString(cx3+cw3/2, y_meta-48*mm, l)
        c.setFillColor(VERDE_CLARO); c.setFont(FONT_N, 8)
        c.drawCentredString(W/2, y_meta-54*mm,
            f"Ritmo personalizado: {meta['taxa']} kg/semana baseado no seu IMC ({meta['imc']})")

    elif tipo == "massa":
        draw_card(c, 20*mm, y_meta-55*mm, W-40*mm, 58*mm, fill=VERDE_ESCURO)
        draw_emoji(c, "musculo", W/2 - 40*mm, y_meta-1*mm, size=5)
        c.setFillColor(VERDE_LIMA); c.setFont(FONT_B, 9)
        c.drawString(W/2 - 32*mm, y_meta-6*mm, "SUA META DE GANHO MUSCULAR")
        cdata = [
            (f"+{meta['g3min']}-{meta['g3max']}", "kg", "3 MESES"),
            (f"+{meta['g6min']}-{meta['g6max']}", "kg", "6 MESES"),
            (safe(d.get("compro")), "/10", "COMPROMISSO"),
        ]
        cw3 = (W-40*mm)/3
        for i,(v,u,l) in enumerate(cdata):
            cx3 = 20*mm+i*cw3
            if i>0:
                c.setStrokeColor(CARD_MEDIO_E); c.setLineWidth(0.5)
                c.line(cx3, y_meta-15*mm, cx3, y_meta-50*mm)
            c.setFillColor(BRANCO); c.setFont(FONT_B, 18)
            c.drawCentredString(cx3+cw3/2, y_meta-32*mm, v)
            c.setFillColor(VERDE_CLARO); c.setFont(FONT_N, 9)
            c.drawCentredString(cx3+cw3/2, y_meta-42*mm, u)
            c.setFillColor(colors.HexColor("#888888")); c.setFont(FONT_B, 7)
            c.drawCentredString(cx3+cw3/2, y_meta-50*mm, l)

    else:
        draw_card(c, 20*mm, y_meta-50*mm, W-40*mm, 53*mm, fill=VERDE_ESCURO)
        c.setFillColor(VERDE_LIMA); c.setFont(FONT_B, 9)
        c.drawCentredString(W/2, y_meta-6*mm, "SUAS METAS EM 60 DIAS")
        cdata = [
            (f"{meta.get('freq_atual',0)}x→{meta.get('freq_meta',0)}x", "/sem", "TREINOS"),
            (f"{meta.get('estresse_atual',5)}→{meta.get('estresse_meta',3)}", "/10", "ESTRESSE"),
            (safe(d.get("compro")), "/10", "COMPROMISSO"),
        ]
        cw3 = (W-40*mm)/3
        for i,(v,u,l) in enumerate(cdata):
            cx3 = 20*mm+i*cw3
            if i>0:
                c.setStrokeColor(CARD_MEDIO_E); c.setLineWidth(0.5)
                c.line(cx3, y_meta-15*mm, cx3, y_meta-48*mm)
            c.setFillColor(BRANCO); c.setFont(FONT_B, 16)
            c.drawCentredString(cx3+cw3/2, y_meta-30*mm, v)
            c.setFillColor(VERDE_CLARO); c.setFont(FONT_N, 8)
            c.drawCentredString(cx3+cw3/2, y_meta-40*mm, u)
            c.setFillColor(colors.HexColor("#888888")); c.setFont(FONT_B, 7)
            c.drawCentredString(cx3+cw3/2, y_meta-48*mm, l)

    # frase motivacional com emoji
    nome = d.get("nome") or "você"
    y_frase = y_meta - 60*mm
    draw_card(c, 20*mm, y_frase-20*mm, W-40*mm, 22*mm, fill=CARD_CLARO)
    frase_emoji = "sorriso" if tipo == "emagrecimento" else ("musculo" if tipo == "massa" else "brilho")
    if tipo == "emagrecimento":
        frase = f"{nome}, você tomou a decisão certa ao buscar um diagnóstico personalizado. Agora é só seguir o caminho!"
    elif tipo == "massa":
        frase = f"{nome}, com dedicacao e o protocolo certo você vai transformar seu corpo. Vamos juntos!"
    else:
        frase = f"{nome}, qualidade de vida comeca com pequenas mudancas consistentes. Você ja deu o primeiro passo!"
    draw_emoji(c, frase_emoji, 24*mm, y_frase-3*mm, size=5)
    wrap(c, frase, 31*mm, y_frase-4*mm, W-55*mm, size=11, cor=VERDE_ESCURO, leading=14, align=TA_LEFT)

    rodape(c, 2)
    c.showPage()

# ── PÁGINA 3 — META E HÁBITOS ─────────────────────────────────────────────────
def pag_meta(c, d):
    draw_bg_light(c)
    draw_header_light(c, "lista", "SEÇÃO 2 — Meta e Hábitos",
                      "Seu estilo de vida e rotina atual")
    itens = [
        ("alvo", "Objetivo principal",  obj_texto(d.get("objetivo",""))),
        ("salada", "Alimentação",         safe(d.get("alimentacao"))),
        ("correr", "Exercício atual",     safe(d.get("exercicio"))),
        ("relogio", "Tempo de treino",     safe(d.get("tempo_treino"))),
        ("bike", "Cardio",              safe(d.get("cardio"))),
        ("alarme", "Tempo de cardio",     safe(d.get("tempo_cardio"))),
        ("raiva", "Nível de estresse",   safe(d.get("estresse"))),
        ("musculo", "Comprometimento",     f"{safe(d.get('compro'))}/10"),
        ("aviso", "Limitações",          safe(d.get("limitacao"))),
    ]
    # FIX: y inicial logo abaixo do header
    y = HEADER_BOTTOM() - 8*mm
    for emoji, lbl, val in itens:
        # FIX: altura do card aumentada para 20mm, com wrap no valor
        card_h = 20*mm
        draw_card(c, 20*mm, y-card_h, W-40*mm, card_h, fill=CARD_CLARO)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(20*mm, y-card_h, 5*mm, card_h, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        draw_emoji(c, emoji, 28*mm, y-2*mm, size=6)
        c.setFont(FONT_B, 10)
        c.drawString(36*mm, y-8*mm, lbl.upper()+":")
        # FIX: wrap no valor para não sair da linha
        wrap(c, str(val)[:80], 105*mm, y-4*mm, W-130*mm,
             size=10, cor=TEXTO_ESCURO, leading=12, align=TA_LEFT)
        y -= card_h + 3*mm
    rodape(c, 3)
    c.showPage()

# ── PÁGINA 4 — ANALISE VISUAL ─────────────────────────────────────────────────
def pag_perfil(c, d):
    draw_bg_light(c)
    draw_header_light(c, "lupa", "SEÇÃO 3 — Leitura do seu perfil",
                      "Como este diagnóstico interpreta suas respostas")

    nome     = d.get("nome") or "Aluno"
    obj      = obj_texto(d.get("objetivo",""))
    comp_raw = to_float(d.get("compro")) or 0
    imc_val  = d.get("imc") or calc_imc(d.get("peso"),d.get("altura"))
    lim      = str(d.get("limitacao") or "Nenhuma")
    med      = str(d.get("medicamentos") or "Nenhum")
    alim     = safe(d.get("alimentacao"))
    exerc    = safe(d.get("exercicio"))
    estresse = safe(d.get("estresse"))
    COR_IMC  = cor_imc(to_float(imc_val))

    # FIX: título logo abaixo do header
    y_titulo = HEADER_BOTTOM() - 8*mm
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 13)
    c.drawCentredString(W/2, y_titulo, f"Aqui está o que identificamos sobre {nome}:")

    # 4 cards visuais
    card_w = (W-46*mm)/2; card_h = 40*mm
    cards = [
        ("alvo", "FOCO INICIAL", obj, f"Compromisso: {int(comp_raw)}/10", VERDE_ESCURO),
        ("barras", "PERFIL FÍSICO", class_imc(imc_val), f"IMC: {imc_val or '–'}", COR_IMC),
        ("correr", "ROTINA ATUAL", exerc, f"Treino: {safe(d.get('tempo_treino'))}", VERDE_ESCURO),
        ("salada", "ALIMENTACAO", alim, f"Estresse: {estresse}/10", VERDE_MEDIO),
    ]
    y_c = y_titulo - 8*mm
    for i,(emoji,tit,val,det,cor) in enumerate(cards):
        col=i%2; row=i//2
        cx=22*mm+col*(card_w+4*mm); cy=y_c-row*(card_h+5*mm)
        draw_card(c, cx, cy-card_h, card_w, card_h, fill=CARD_CLARO)
        c.setFillColor(cor)
        c.roundRect(cx, cy-6*mm, card_w, 6*mm, 2, fill=1, stroke=0)
        # emoji + título na faixa colorida
        draw_emoji(c, emoji, cx + card_w/2 - len(tit)*2.5 - 6*mm, cy - 0.5*mm, size=5)
        c.setFillColor(BRANCO); c.setFont(FONT_B, 9)
        c.drawString(cx + card_w/2 - len(tit)*2.5 + 1*mm, cy-4*mm, tit)
        c.setFillColor(TEXTO_ESCURO); c.setFont(FONT_B, 12)
        c.drawCentredString(cx+card_w/2, cy-19*mm, str(val)[:28])
        c.setFillColor(CINZA_TEXTO); c.setFont(FONT_N, 10)
        c.drawCentredString(cx+card_w/2, cy-29*mm, str(det)[:36])

    # barra comprometimento
    y_comp = y_c - 2*(card_h+5*mm) - 8*mm
    draw_card(c, 20*mm, y_comp-22*mm, W-40*mm, 26*mm, fill=CARD_CLARO)
    draw_emoji(c, "musculo", 24*mm, y_comp-0.5*mm, size=5)
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 10)
    c.drawString(31*mm, y_comp-2*mm, "Nível de comprometimento:")
    bw=W-80*mm; bx=24*mm; by=y_comp-16*mm
    c.setFillColor(colors.HexColor("#DDDDDD"))
    c.roundRect(bx, by, bw, 8*mm, 4, fill=1, stroke=0)
    pct = min(comp_raw/10.0,1.0)
    c.setFillColor(VERDE_LIMA if pct>=0.7 else colors.HexColor("#FFC000"))
    c.roundRect(bx, by, bw*pct, 8*mm, 4, fill=1, stroke=0)
    if pct>0.15:
        c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B,9)
        c.drawString(bx+3*mm, by+2*mm, f"{int(comp_raw)}/10")
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B,9)
    label_c = "Excelente!" if pct>=0.8 else ("Ótimo!" if pct>=0.6 else "Vamos lá!")
    c.drawString(bx+bw+3*mm, by+2*mm, label_c)

    # alertas
    y_obs = y_comp - 30*mm
    obs = []
    if lim.lower() not in ["nenhuma","não","none","","não informado"]:
        obs.append(("aviso", "Limitação física", lim, LARANJA))
    if med.lower() not in ["nenhum","não","none","","não informado"]:
        obs.append(("remedio", "Medicamento em uso", med, AZUL))
    for emoji_o, tit_o, val_o, cor_o in obs:
        draw_card(c, 20*mm, y_obs-18*mm, W-40*mm, 20*mm, fill=CARD_CLARO)
        c.setFillColor(cor_o)
        c.roundRect(20*mm, y_obs-18*mm, 5*mm, 20*mm, 2, fill=1, stroke=0)
        draw_emoji(c, emoji_o, 28*mm, y_obs-2*mm, size=5)
        c.setFillColor(cor_o); c.setFont(FONT_B,10)
        c.drawString(36*mm, y_obs-6*mm, tit_o+":")
        wrap(c, str(val_o), 90*mm, y_obs-3*mm, W-115*mm,
             size=10, cor=TEXTO_ESCURO, leading=12, align=TA_LEFT)
        y_obs -= 24*mm

    # nota final
    draw_card(c, 20*mm, y_obs-18*mm, W-40*mm, 20*mm, fill=CARD_CLARO)
    draw_emoji(c, "medico", 24*mm, y_obs-3*mm, size=5)
    wrap(c, "Este diagnóstico não substitui consulta medica ou nutricional. Ele organiza os principais sinais do seu perfil para você entender por onde começar.",
         31*mm, y_obs-4*mm, W-55*mm, size=9, cor=CINZA_TEXTO, leading=12, align=TA_LEFT)

    rodape(c, 4)
    c.showPage()

# ── PÁGINA 5 — LAUDO OMS ──────────────────────────────────────────────────────
def pag_oms(c, d):
    draw_bg_light(c)
    draw_header_light(c, "correr", "SEÇÃO 4 — Laudo de Atividade Física",
                      "Comparativo com as recomendações da OMS")

    total, status = avaliar_oms(d.get("exercicio",""), d.get("tempo_treino",""),
                                d.get("cardio",""), d.get("tempo_cardio",""))
    # FIX: cor dinâmica baseada no status OMS
    cor_st = cor_oms(status)
    label_st = {
        "insuficiente": "NÍVEL INSUFICIENTE ",
        "parcial":      "QUASE LA! ",
        "adequado":     "DENTRO DA META OMS ",
        "excelente":    "ACIMA DA META OMS ",
    }.get(status,"")

    # FIX: card OMS começa logo abaixo do header
    y_card_top = HEADER_BOTTOM() - 5*mm
    card_h = 58*mm
    draw_card(c, 20*mm, y_card_top - card_h, W-40*mm, card_h, fill=cor_st)

    faixa_cor = {
        "insuficiente": colors.HexColor("#8B0000"),
        "parcial":      colors.HexColor("#A05500"),
        "adequado":     colors.HexColor("#3A8020"),
        "excelente":    colors.HexColor("#1A4010"),
    }.get(status, VERDE_ESCURO)

    label_emoji = {"insuficiente":"aviso","parcial":"fogo","adequado":"ok","excelente":"trofeu"}.get(status,"ok")
    label_txt   = {"insuficiente":"NÍVEL INSUFICIENTE","parcial":"QUASE LÁ!",
                   "adequado":"DENTRO DA META OMS","excelente":"ACIMA DA META OMS"}.get(status,"")

    c.setFillColor(faixa_cor)
    c.roundRect(20*mm, y_card_top - 12*mm, W-40*mm, 12*mm, 5, fill=1, stroke=0)
    draw_emoji(c, label_emoji, W/2 - len(label_txt)*2.8 - 5*mm, y_card_top - 1*mm, size=5)
    c.setFillColor(BRANCO); c.setFont(FONT_B, 11)
    c.drawString(W/2 - len(label_txt)*2.8 + 2*mm, y_card_top - 8*mm, label_txt)
    c.setFillColor(BRANCO); c.setFont(FONT_B, 36)
    c.drawCentredString(W/2, y_card_top - 30*mm, f"{total} min/semana")
    c.setFillColor(BRANCO); c.setFont(FONT_N, 10)
    c.drawCentredString(W/2, y_card_top - 42*mm, "atividade física estimada por semana")

    msg_emoji = {"insuficiente":"sorriso","parcial":"fogo","adequado":"ok","excelente":"trofeu"}.get(status,"ok")
    if status == "insuficiente":
        msg = "Você está abaixo da recomendação da OMS (150 min/semana). Não se preocupe — seu protocolo vai aumentar progressivamente seu volume de treino de forma segura e sustentavel."
    elif status == "parcial":
        msg = "Você está quase lá! Com pequenos ajustes na sua rotina você atinge fácilmente os 150 min/semana recomendados pela OMS. Seu protocolo vai te ajudar a chegar la."
    elif status == "adequado":
        msg = "Parabéns! Você ja atinge as recomendações da OMS. Seu protocolo vai potencializar ainda mais seus resultados, otimizando qualidade e periodizacao dos treinos."
    else:
        msg = "Excelente! Você está acima das recomendações da OMS. Seu protocolo vai garantir recuperação adequada e maximizar seus resultados sem risco de overtraining."

    y_msg = y_card_top - card_h - 5*mm
    draw_card(c, 20*mm, y_msg-26*mm, W-40*mm, 28*mm, fill=CARD_CLARO)
    draw_emoji(c, msg_emoji, 24*mm, y_msg-3*mm, size=5)
    wrap(c, msg, 31*mm, y_msg-4*mm, W-55*mm, size=10, cor=TEXTO_ESCURO, leading=13, align=TA_LEFT)

    y_rec = y_msg - 34*mm
    draw_emoji(c, "pino", 20*mm, y_rec+5*mm, size=5)
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 11)
    c.drawString(27*mm, y_rec, "Recomendação da OMS para adultos:")
    for tipo_r, meta_r, ex_r, cor_r in [
        ("Atividade moderada", "150 a 300 min/semana", "caminhada, bike, natacao", VERDE_MEDIO),
        ("Atividade vigorosa",  "75 a 150 min/semana",  "corrida, HIIT, musculacao intensa", VERDE_ESCURO),
    ]:
        y_rec -= 20*mm
        draw_card(c, 20*mm, y_rec-14*mm, W-40*mm, 16*mm, fill=cor_r)
        c.setFillColor(BRANCO); c.setFont(FONT_B, 10)
        c.drawString(24*mm, y_rec-5*mm, tipo_r+":")
        c.setFont(FONT_B, 10)
        c.drawString(85*mm, y_rec-5*mm, meta_r)
        c.setFillColor(VERDE_CLARO); c.setFont(FONT_N, 8)
        c.drawString(145*mm, y_rec-5*mm, f"({ex_r})")

    y_cons = y_rec - 28*mm
    draw_card(c, 20*mm, y_cons-50*mm, W-40*mm, 54*mm, fill=CARD_CLARO)
    c.setFillColor(VERDE_LIMA)
    c.roundRect(20*mm, y_cons-50*mm, 5*mm, 54*mm, 2, fill=1, stroke=0)
    draw_emoji(c, "halteres", 29*mm, y_cons-4*mm, size=5)
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 11)
    c.drawString(36*mm, y_cons-8*mm, "Como o protocolo Luis Kummer vai te ajudar:")
    if status in ["insuficiente","parcial"]:
        texto_c = "Seu protocolo sera montado para aumentar progressivamente seu volume de treino, respeitando seu ritmo atual e chegando gradualmente a meta da OMS, de forma segura e sustentavel."
    else:
        texto_c = "Seu protocolo vai potencializar seus resultados ja existentes, otimizando qualidade dos treinos, periodizando corretamente e garantindo recuperação adequada para maxima evolução."
    wrap(c, texto_c, 29*mm, y_cons-22*mm, W-54*mm, size=10, cor=TEXTO_ESCURO, leading=13)

    rodape(c, 5)
    c.showPage()

# ── PÁGINA 6 — APP E DIFERENCIAIS ────────────────────────────────────────────
def pag_app(c, d):
    draw_bg_light(c)
    draw_header_light(c, "celular", "SEÇÃO 5 — Seu App de Treinos",
                      "Tudo que você vai ter acesso no seu protocolo")

    nome = d.get("nome") or "você"

    # FIX: título abaixo do header
    y_titulo = HEADER_BOTTOM() - 8*mm
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 13)
    c.drawCentredString(W/2, y_titulo, f"{nome}, você vai ter tudo isso na palma da mão:")

    app1 = os.path.join(BASE_DIR, "app_print1.png")
    app2 = os.path.join(BASE_DIR, "app_print2.png")
    app_w = 42*mm; app_h = 72*mm; gap_app = 8*mm
    total_app_w = app_w*2 + gap_app
    app_x1 = W/2 - total_app_w/2
    app_x2 = app_x1 + app_w + gap_app
    app_y_top = y_titulo - 6*mm

    if os.path.exists(app1):
        c.drawImage(app1, app_x1, app_y_top-app_h,
                    width=app_w, height=app_h, preserveAspectRatio=True, mask="auto")
    if os.path.exists(app2):
        c.drawImage(app2, app_x2, app_y_top-app_h,
                    width=app_w, height=app_h, preserveAspectRatio=True, mask="auto")

    c.setFillColor(CINZA_TEXTO); c.setFont(FONT_N, 9)
    c.drawCentredString(W/2, app_y_top-app_h-4*mm, "Interface real do app MFIT Personal")

    diferenciais = [
        ("halteres", "Protocolo personalizado",     "Treinos montados do zero pelo Luis exclusivamente para o seu perfil e objetivo."),
        ("camera", "Videos de todos os exercícios","Cada exercício tem video do próprio Luis demonstrando a execução correta."),
        ("chat", "Suporte direto com o Luis",    "Atendimento personalizado via app e WhatsApp com quem montou seu treino."),
        ("meditacao", "Mobilidade e alongamento",     "Protocolos de mobilidade e alongamento inclusos para complementar os treinos."),
        ("bike", "Orientações de cardio",        "Guia personalizado de cardio baseado no seu objetivo e tempo disponível."),
        ("grafico", "Acompanhamento de evolução",   "Registre cargas e séries e veja seu progresso semana a semana."),
    ]
    cw_d = (W-46*mm)/2; ch_d = 28*mm
    y_d = app_y_top - app_h - 14*mm
    for i,(emoji,tit,desc) in enumerate(diferenciais):
        col = i%2; row = i//2
        cx_d = 22*mm + col*(cw_d+4*mm)
        cy_d = y_d - row*(ch_d+3*mm)
        draw_card(c, cx_d, cy_d-ch_d, cw_d, ch_d, fill=CARD_CLARO)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(cx_d, cy_d-ch_d, 4*mm, ch_d, 2, fill=1, stroke=0)
        draw_emoji(c, emoji, cx_d+6*mm, cy_d-3*mm, size=5)
        c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 10)
        c.drawString(cx_d+13*mm, cy_d-8*mm, tit)
        wrap(c, desc, cx_d+7*mm, cy_d-13*mm, cw_d-12*mm,
             size=8, cor=CINZA_TEXTO, leading=10, align=TA_LEFT)

    # FIX: botão removido desta página (movido para pág 7)

    rodape(c, 6)
    c.showPage()

# ── PÁGINA 7 — PLANOS ─────────────────────────────────────────────────────────
def pag_oferta(c, d):
    draw_bg_light(c)
    draw_header_light(c, "alvo", "SEÇÃO 6 — Seu Protocolo Personalizado",
                      "Escolha o plano ideal para começar sua transformação")

    nome     = d.get("nome") or "você"
    obj      = obj_texto(d.get("objetivo",""))
    comp_raw = to_float(d.get("compro")) or 0
    meta     = meta_personalizada(d)

    if meta.get("tipo") == "emagrecimento":
        frase_dest = f"{nome}, você tem tudo para perder {meta['diff']} kg."
    elif meta.get("tipo") == "massa":
        frase_dest = f"{nome}, você tem tudo para ganhar massa muscular de verdade."
    else:
        frase_dest = f"{nome}, você tem tudo para transformar sua qualidade de vida."

    # FIX: card frase começa logo abaixo do header
    y_frase = HEADER_BOTTOM() - 5*mm
    draw_card(c, 20*mm, y_frase-32*mm, W-40*mm, 34*mm, fill=VERDE_ESCURO)
    c.setFillColor(BRANCO); c.setFont(FONT_B, 14)
    c.drawCentredString(W/2, y_frase-12*mm, frase_dest)
    nivel = "seu alto nível de comprometimento" if comp_raw>=8 else "seu comprometimento"
    c.setFillColor(VERDE_CLARO); c.setFont(FONT_N, 9)
    c.drawCentredString(W/2, y_frase-22*mm, f"Com base no seu objetivo de {obj}")
    c.drawCentredString(W/2, y_frase-29*mm, f"e em {nivel} ({int(comp_raw)}/10)")

    planos = [
        ("Individual  —  1 Protocolo", "60 dias de acompanhamento", "R$ 119",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636"),
        ("Dupla  —  1 Protocolo", "60 dias para você + 1 pessoa", "R$ 207",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112637&page=112636"),
        ("Individual  —  3 Protocolos", "180 dias de acompanhamento", "R$ 297",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112638&page=112636"),
        ("Dupla  —  3 Protocolos", "180 dias para você + 1 pessoa", "R$ 479",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112639&page=112636"),
    ]
    ph=40*mm; gap=4*mm; y_s = y_frase - 36*mm
    for i,(tit,desc,preco,url) in enumerate(planos):
        y=y_s - i*(ph+gap)
        draw_card(c, 20*mm, y-ph, W-40*mm, ph, fill=CARD_CLARO)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(20*mm, y-ph, 6*mm, ph, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 13)
        c.drawString(30*mm, y-11*mm, tit)
        c.setFillColor(CINZA_TEXTO); c.setFont(FONT_N, 10)
        c.drawString(30*mm, y-20*mm, desc)
        c.setFillColor(DOURADO); c.setFont(FONT_B, 18)
        c.drawString(30*mm, y-33*mm, preco)
        # FIX: botão reposicionado e redimensionado
        bx=W-68*mm; bw=44*mm; bh=10*mm
        c.setFillColor(VERDE_LIMA)
        c.roundRect(bx, y-ph+15*mm, bw, bh, 3, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 8)
        c.drawCentredString(bx+bw/2, y-ph+20*mm, "Desbloquear →")
        c.linkURL(url, (bx, y-ph+15*mm, bx+bw, y-ph+25*mm), relative=0)

    # FIX: botão CTA principal ao final da página de oferta
    y_cta = y_s - 4*(ph+gap) - 6*mm
    bw_cta = W-40*mm; bh_cta = 16*mm; bx_cta = 20*mm
    c.setFillColor(VERDE_LIMA)
    c.roundRect(bx_cta, y_cta - bh_cta, bw_cta, bh_cta, 5, fill=1, stroke=0)
    draw_emoji(c, "foguete", bx_cta + bw_cta/2 - 45*mm, y_cta - 2*mm, size=6)
    c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 13)
    c.drawString(bx_cta + bw_cta/2 - 36*mm, y_cta - 10*mm, "Começar meu protocolo →")
    url_cta = "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636"
    c.linkURL(url_cta, (bx_cta, y_cta - bh_cta, bx_cta + bw_cta, y_cta), relative=0)

    rodape(c, 7)
    c.showPage()

# ── PÁGINA 8 — DEPOIMENTOS ────────────────────────────────────────────────────
def pag_depoimentos(c, d):
    draw_bg_light(c)
    draw_header_light(c, "estrela", "SEÇÃO 7 — Resultados Reais",
                      "Quem ja transformou a vida com o protocolo Luis Kummer")

    nome = d.get("nome") or "você"

    deps = [
        ("Ana Paula, 34 anos", "Perdi 8kg em 60 dias seguindo o protocolo. O acompanhamento pelo app fez toda a diferença! Nunca imaginei conseguir me comprometer tanto.", 5),
        ("Marcos e Juliana",   "Fizemos o plano dupla e foi incrível! Nos motivamos juntos e em 3 meses transformamos completamente nosso estilo de vida.", 5),
        ("Fernanda, 28 anos",  "Nunca pensei que conseguiria manter uma rotina de treinos. O protocolo e prático e se encaixa perfeitamente na minha rotina corrida.", 5),
        ("Cristiane, 41 anos", "Com duas filhas e trabalho não sobrava tempo. O Luis montou um treino perfeito para minha realidade e em 60 dias ja vi resultados.", 5),
        ("Roberto, 52 anos",   "Comecei com receio por causa da idade e de uma hernia. O protocolo foi totalmente adaptado e hoje me sinto mais disposto do que aos 40!", 5),
    ]

    # FIX: y inicial logo abaixo do header
    y = HEADER_BOTTOM() - 6*mm
    for nome_d, dep, nstars in deps:
        h_box = 30*mm
        draw_card(c, 20*mm, y-h_box, W-40*mm, h_box, fill=CARD_CLARO)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(20*mm, y-h_box, 6*mm, h_box, 2, fill=1, stroke=0)
        c.setFillColor(DOURADO); c.setFont(FONT_N, 10)
        c.drawString(30*mm, y-7*mm, "★"*nstars)
        c.setFillColor(VERDE_ESCURO); c.setFont(FONT_B, 11)
        c.drawString(62*mm, y-7*mm, nome_d)
        wrap(c, f'"{dep}"', 30*mm, y-12*mm, W-54*mm,
             size=9, cor=CINZA_TEXTO, leading=11, align=TA_LEFT)
        y -= h_box + 4*mm

    # FIX: card final sem botão CTA (movido para pág 7)
    y_cta = y - 4*mm
    draw_card(c, 20*mm, y_cta-18*mm, W-40*mm, 20*mm, fill=VERDE_ESCURO)
    c.setFillColor(BRANCO); c.setFont(FONT_B, 14)
    c.drawCentredString(W/2, y_cta-12*mm, f"{nome}, agora é a sua vez. ")

    rodape(c, 8)
    c.showPage()

# ── FUNÇÃO PRINCIPAL ──────────────────────────────────────────────────────────
def gerar_pdf_diagnostico(dados):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Diagnóstico Personalizado - Luis Kummer")
    if not dados.get("imc"):
        imc = calc_imc(dados.get("peso"), dados.get("altura"))
        if imc: dados["imc"] = imc
    pag_capa(c, dados)
    pag_bio(c, dados)
    pag_meta(c, dados)
    pag_perfil(c, dados)
    pag_oms(c, dados)
    pag_app(c, dados)
    pag_oferta(c, dados)
    pag_depoimentos(c, dados)
    c.save()
    buf.seek(0)
    return buf.read()

if __name__ == "__main__":
    dados = {
        "nome": "Teste 36", "objetivo": "ganhar_massa", "sexo": "Masculino",
        "peso": "97", "altura": "184", "idade": "32", "peso_obj": "85",
        "imc": None,
        "limitacao": "ombro/braço, joelho/tornozelo, coluna/hérnia",
        "medicamentos": "tireoide, antidepressivo/ansiedade, diabetes/glicemia",
        "exercicio": "treina 5x ou mais/semana",
        "tempo_treino": "45 a 60 min",
        "cardio": "danca, natacao, hiit, bike, corrida",
        "tempo_cardio": "20 a 30 min",
        "alimentacao": "alimentação razoável",
        "compro": "9", "estresse": "7",
    }
    pdf = gerar_pdf_diagnostico(dados)
    with open("/mnt/user-data/outputs/diagnostico_v2.pdf", "wb") as f:
        f.write(pdf)
    print("OK — 8 paginas")
