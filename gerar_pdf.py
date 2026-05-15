import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

W, H = A4

# ── PALETA — VERDE LIMA (tom da logo) ────────────────────────────────────────
VERDE_LIMA    = colors.HexColor("#5BBF2A")   # verde da logo
VERDE_ESCURO  = colors.HexColor("#2D5A1B")   # escuro para headers
VERDE_MEDIO   = colors.HexColor("#4A9422")   # médio
VERDE_CLARO   = colors.HexColor("#B8E896")   # claro para detalhes
VERDE_BG      = colors.HexColor("#EEF7E8")   # fundo dos cards
CREME         = colors.HexColor("#F6FAF3")   # fundo das páginas
TEXTO_ESCURO  = colors.HexColor("#1A2E12")
TEXTO_MEDIO   = colors.HexColor("#3A5C27")
BRANCO        = colors.white
DOURADO       = colors.HexColor("#C8A84B")
CINZA_CLARO   = colors.HexColor("#E0E0E0")
LARANJA       = colors.HexColor("#E07B00")
AZUL_INFO     = colors.HexColor("#3A7BBF")

FONT_N = "Helvetica"
FONT_B = "Helvetica-Bold"

# ── HELPERS ──────────────────────────────────────────────────────────────────
def draw_bg(c):
    c.setFillColor(CREME)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_rect(c, x, y, w, h, fill=VERDE_BG, radius=4):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

def draw_header_bar(c, titulo, subtitulo=None):
    altura = 40*mm if subtitulo else 28*mm
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, H-altura, W, altura, fill=1, stroke=0)
    # faixa lima na base do header
    c.setFillColor(VERDE_LIMA)
    c.rect(0, H-altura, W, 4*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont(FONT_B, 16)
    if subtitulo:
        c.drawCentredString(W/2, H-16*mm, titulo)
        c.setFillColor(VERDE_CLARO)
        c.setFont(FONT_N, 9)
        c.drawCentredString(W/2, H-27*mm, subtitulo)
    else:
        c.drawCentredString(W/2, H-16*mm, titulo)

def rodape(c, num):
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
    c.setFillColor(VERDE_LIMA)
    c.rect(0, 13*mm, W, 1*mm, fill=1, stroke=0)
    c.setFillColor(VERDE_CLARO)
    c.setFont(FONT_N, 8)
    c.drawCentredString(W/2, 5*mm, f"Luis Kummer Personal  •  MFIT Personal  •  {num}/6")

def linha_div(c, y):
    c.setStrokeColor(VERDE_CLARO)
    c.setLineWidth(0.8)
    c.line(20*mm, y, W-20*mm, y)

def wrap(c, texto, x, y, larg, size=10, cor=TEXTO_ESCURO, leading=15):
    st = ParagraphStyle("s", fontName=FONT_N, fontSize=size,
                        textColor=cor, leading=leading, alignment=TA_JUSTIFY)
    p = Paragraph(texto, st)
    p.wrapOn(c, larg, 999)
    p.drawOn(c, x, y - p.height)
    return y - p.height

def wrap_left(c, texto, x, y, larg, size=10, cor=TEXTO_ESCURO, leading=14):
    st = ParagraphStyle("s", fontName=FONT_N, fontSize=size,
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
    if not p or not a: return None
    if a > 3: a = a / 100
    if a == 0: return None
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

# ── LÓGICA OMS ───────────────────────────────────────────────────────────────
def avaliar_oms(exercicio, tempo_treino, cardio, tempo_cardio):
    """
    Estima minutos semanais de atividade e compara com OMS:
    150-300 min/semana moderado OU 75-150 min/semana vigoroso.
    Retorna (minutos_estimados, status, mensagem)
    """
    exercicio_str  = str(exercicio or "").lower()
    treino_str     = str(tempo_treino or "").lower()
    cardio_str     = str(cardio or "").lower()
    cardio_t_str   = str(tempo_cardio or "").lower()

    # estimar frequência semanal de treino
    freq = 0
    if "1x" in exercicio_str or "1-2" in exercicio_str: freq = 1
    elif "2x" in exercicio_str or "2-3" in exercicio_str: freq = 2
    elif "3x" in exercicio_str or "3-4" in exercicio_str: freq = 3
    elif "4x" in exercicio_str or "4-5" in exercicio_str: freq = 4
    elif "5x" in exercicio_str or "todos" in exercicio_str: freq = 5
    elif "nao" in exercicio_str or "sedent" in exercicio_str: freq = 0

    # estimar minutos por sessao de treino
    min_treino = 0
    if "menos de 30" in treino_str: min_treino = 20
    elif "30" in treino_str and "45" in treino_str: min_treino = 37
    elif "45" in treino_str and "60" in treino_str: min_treino = 52
    elif "60" in treino_str or "1 hora" in treino_str: min_treino = 60
    elif "mais de 60" in treino_str or "mais de 1" in treino_str: min_treino = 75

    # estimar minutos de cardio por semana
    min_cardio = 0
    freq_cardio = 2  # padrão
    if "nao" not in cardio_str and cardio_str not in ["", "none", "nao informado"]:
        if "menos de 20" in cardio_t_str: min_cardio = 15 * freq_cardio
        elif "20" in cardio_t_str: min_cardio = 20 * freq_cardio
        elif "30" in cardio_t_str: min_cardio = 30 * freq_cardio
        elif "45" in cardio_t_str: min_cardio = 45 * freq_cardio
        elif "60" in cardio_t_str: min_cardio = 60 * freq_cardio

    total_min = (freq * min_treino) + min_cardio

    # avaliar
    if total_min == 0:
        status = "insuficiente"
        msg = "Voce esta sedentario. A OMS recomenda ao menos 150 min/semana de atividade moderada."
    elif total_min < 75:
        status = "insuficiente"
        msg = f"Voce realiza aprox. {total_min} min/semana. A OMS recomenda ao menos 150 min/semana."
    elif total_min < 150:
        status = "parcial"
        msg = f"Voce realiza aprox. {total_min} min/semana. Esta proximo da meta OMS (150 min/semana)!"
    elif total_min <= 300:
        status = "adequado"
        msg = f"Parabens! Voce realiza aprox. {total_min} min/semana — dentro da recomendacao da OMS!"
    else:
        status = "excelente"
        msg = f"Excelente! Voce realiza aprox. {total_min} min/semana — acima da recomendacao da OMS!"

    return total_min, status, msg

# ── ESTIMATIVA DE PRAZO PARA META DE PESO ────────────────────────────────────
def estimar_prazo(peso_atual, peso_obj, objetivo):
    p = to_float(peso_atual)
    po = to_float(peso_obj)
    if not p or not po: return None
    diff = p - po
    obj_str = str(objetivo or "").lower()
    eh_emagrecimento = (
        "perder" in obj_str or "emag" in obj_str or
        "peso" in obj_str or diff > 2
    )
    if not eh_emagrecimento or diff <= 0: return None
    # deficit de ~0.5kg/semana = ritmo saudavel
    semanas = diff / 0.5
    meses = round(semanas / 4.3)
    if meses < 1: meses = 1
    return diff, meses

# ── PÁGINA 1 — CAPA ──────────────────────────────────────────────────────────
def pag_capa(c, d):
    draw_bg(c)

    # ── HEADER: fundo escuro, logo centralizada, sem sobreposição ──
    HEADER_H = 85*mm
    c.setFillColor(VERDE_ESCURO)
    c.rect(0, H-HEADER_H, W, HEADER_H, fill=1, stroke=0)
    # faixa lima na base do header
    c.setFillColor(VERDE_LIMA)
    c.rect(0, H-HEADER_H, W, 3*mm, fill=1, stroke=0)

    # logo centralizada — ocupa a parte superior do header
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_luis_transparente.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_luis.png")
    if os.path.exists(logo_path):
        logo_w = 55*mm
        logo_h = 55*mm
        logo_x = W/2 - logo_w/2
        logo_y = H - 68*mm   # topo da logo a 13mm do topo da página
        c.drawImage(logo_path, logo_x, logo_y,
                    width=logo_w, height=logo_h,
                    preserveAspectRatio=True, mask='auto')

    # subtítulo bem abaixo da logo, antes da faixa lima
    c.setFillColor(VERDE_CLARO)
    c.setFont(FONT_N, 9)
    c.drawCentredString(W/2, H-HEADER_H+8*mm, "MFIT Personal  |  Diagnostico Personalizado")

    # ── CORPO: fundo creme ──
    nome = d.get("nome") or "Aluno(a)"
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 22)
    c.drawCentredString(W/2, H-HEADER_H-12*mm, f"Ola, {nome}!")
    c.setFillColor(TEXTO_MEDIO)
    c.setFont(FONT_N, 10)
    c.drawCentredString(W/2, H-HEADER_H-23*mm,
        "Preparamos este diagnostico exclusivo com base nas suas respostas.")
    linha_div(c, H-HEADER_H-30*mm)

    # 3 caixas resumo
    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    caixas = [
        ("Objetivo",    obj_texto(d.get("objetivo", ""))),
        ("IMC",         safe(imc_val)),
        ("Compromisso", f"{safe(d.get('compro'))}/10"),
    ]
    y_caixas = H - HEADER_H - 35*mm
    cw = (W - 44*mm) / 3
    for i, (lbl, val) in enumerate(caixas):
        cx = 22*mm + i * cw
        draw_rect(c, cx, y_caixas-48*mm, cw-4*mm, 48*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(cx, y_caixas-2*mm, cw-4*mm, 4*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 9)
        c.drawCentredString(cx+(cw-4*mm)/2, y_caixas-13*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO)
        c.setFont(FONT_B, 11)
        c.drawCentredString(cx+(cw-4*mm)/2, y_caixas-30*mm, str(val)[:22])

    # caixa motivacional
    y_mot = y_caixas - 58*mm
    draw_rect(c, 20*mm, y_mot-62*mm, W-40*mm, 62*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_LIMA)
    c.roundRect(20*mm, y_mot-2*mm, W-40*mm, 4*mm, 2, fill=1, stroke=0)
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 12)
    c.drawCentredString(W/2, y_mot-14*mm, "Sua transformacao comeca com um passo.")
    wrap(c,
         "Este diagnostico foi elaborado por Luis Kummer com base no seu perfil individual. "
         "Cada protocolo e criado do zero, respeitando seu corpo, sua rotina e seus objetivos. "
         "Vamos juntos nessa jornada!",
         25*mm, y_mot-28*mm, W-50*mm, size=10)

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
        col = i % 2; row = i // 2
        cx = 22*mm + col * cw
        cy = H - 46*mm - row * 36*mm
        draw_rect(c, cx, cy-28*mm, cw-5*mm, 30*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(cx, cy, cw-5*mm, 4*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_MEDIO)
        c.setFont(FONT_B, 8)
        c.drawString(cx+4*mm, cy-10*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO)
        c.setFont(FONT_B, 14)
        c.drawString(cx+4*mm, cy-22*mm, str(val)[:28])

    # barra IMC com marcador
    y_b = H - 210*mm
    draw_rect(c, 20*mm, y_b-28*mm, W-40*mm, 52*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 10)
    c.drawString(24*mm, y_b+18*mm, "Faixa de IMC:")

    segs = [
        (4.5, colors.HexColor("#5B9BD5"), "< 18.5"),
        (6.5, colors.HexColor("#70AD47"), "18.5-25"),
        (5.0, colors.HexColor("#FFC000"), "25-30"),
        (5.0, colors.HexColor("#FF7C00"), "30-35"),
        (4.0, colors.HexColor("#FF0000"), "> 35"),
    ]
    total = sum(s[0] for s in segs)
    bw = W - 50*mm; bh = 10*mm
    y_barra = y_b + 4*mm
    xpos = 25*mm
    for val_s, cor_s, label_s in segs:
        sw = bw * val_s / total
        c.setFillColor(cor_s)
        c.rect(xpos, y_barra, sw, bh, fill=1, stroke=0)
        if sw > 16*mm:
            c.setFillColor(BRANCO)
            c.setFont(FONT_B, 7)
            c.drawCentredString(xpos + sw/2, y_barra + 3*mm, label_s)
        xpos += sw
    c.setStrokeColor(VERDE_ESCURO)
    c.setLineWidth(1)
    c.roundRect(25*mm, y_barra, bw, bh, 3, fill=0, stroke=1)

    imc_f = to_float(imc_val)
    if imc_f is not None:
        imc_capped = min(max(imc_f, 15.0), 42.0)
        ratio = (imc_capped - 15.0) / 27.0
        mx = 25*mm + bw * ratio
        tri_y = y_barra + bh + 1*mm
        tri_h = 4*mm; tri_w = 3*mm
        path = c.beginPath()
        path.moveTo(mx, tri_y)
        path.lineTo(mx - tri_w, tri_y + tri_h)
        path.lineTo(mx + tri_w, tri_y + tri_h)
        path.close()
        c.setFillColor(VERDE_ESCURO)
        c.drawPath(path, fill=1, stroke=0)
        c.setStrokeColor(VERDE_ESCURO)
        c.setLineWidth(1.5)
        c.setDash(2, 2)
        c.line(mx, y_barra, mx, y_barra + bh)
        c.setDash()
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 8)
        c.drawCentredString(mx, tri_y + tri_h + 2*mm, f"Voce: {imc_f}")

    # meta de peso
    resultado_prazo = estimar_prazo(d.get("peso"), d.get("peso_obj"), d.get("objetivo"))
    if resultado_prazo:
        diff_kg, meses = resultado_prazo
        y_meta = y_b - 36*mm
        draw_rect(c, 20*mm, y_meta-18*mm, W-40*mm, 22*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(20*mm, y_meta+2*mm, W-40*mm, 4*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 10)
        c.drawString(24*mm, y_meta-5*mm, "Meta de peso:")
        c.setFillColor(TEXTO_ESCURO)
        c.setFont(FONT_N, 10)
        c.drawString(60*mm, y_meta-5*mm,
            f"Perder {diff_kg:.1f} kg em aprox. {meses} {"mes" if meses == 1 else "meses"} "
            f"(ritmo saudavel de 0,5 kg/semana)")

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
        ("Tempo de cardio",     safe(d.get("tempo_cardio"))),
        ("Nivel de estresse",   safe(d.get("estresse"))),
        ("Comprometimento",     f"{safe(d.get('compro'))}/10"),
        ("Limitacoes",          safe(d.get("limitacao"))),
    ]
    y = H - 44*mm
    for lbl, val in itens:
        draw_rect(c, 20*mm, y-14*mm, W-40*mm, 16*mm, fill=VERDE_BG)
        c.setFillColor(VERDE_LIMA)
        c.roundRect(20*mm, y-14*mm, 5*mm, 16*mm, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_MEDIO)
        c.setFont(FONT_B, 9)
        c.drawString(29*mm, y-5*mm, lbl.upper() + ":")
        c.setFillColor(TEXTO_ESCURO)
        c.setFont(FONT_N, 10)
        c.drawString(90*mm, y-5*mm, str(val)[:55])
        y -= 20*mm
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
    c.setFont(FONT_B, 12)
    c.drawCentredString(W/2, H-42*mm, f"Aqui esta o que identificamos sobre {nome}:")

    # 4 cards
    card_w = (W - 46*mm) / 2
    card_h = 36*mm
    cards = [
        ("OBJETIVO",      obj,              f"Compromisso: {int(comp_raw)}/10", VERDE_ESCURO),
        ("PERFIL FISICO", class_imc(imc_f), f"IMC: {imc_val or '–'}",          VERDE_MEDIO),
        ("ROTINA",        exerc,            f"Treino: {safe(d.get('tempo_treino'))}", VERDE_ESCURO),
        ("ALIMENTACAO",   alim,             f"Estresse: {estresse}/10",          VERDE_MEDIO),
    ]
    y_cards = H - 50*mm
    for i, (tit, val, det, cor) in enumerate(cards):
        col = i % 2; row = i // 2
        cx = 22*mm + col * (card_w + 4*mm)
        cy = y_cards - row * (card_h + 5*mm)
        draw_rect(c, cx, cy-card_h, card_w, card_h, fill=VERDE_BG)
        c.setFillColor(cor)
        c.roundRect(cx, cy-5*mm, card_w, 5*mm, 2, fill=1, stroke=0)
        c.setFillColor(BRANCO)
        c.setFont(FONT_B, 8)
        c.drawCentredString(cx+card_w/2, cy-3*mm, tit)
        c.setFillColor(TEXTO_ESCURO)
        c.setFont(FONT_B, 10)
        c.drawCentredString(cx+card_w/2, cy-17*mm, str(val)[:30])
        c.setFillColor(TEXTO_MEDIO)
        c.setFont(FONT_N, 8)
        c.drawCentredString(cx+card_w/2, cy-27*mm, str(det)[:38])

    # barra comprometimento
    y_comp = H - 148*mm
    draw_rect(c, 20*mm, y_comp-20*mm, W-40*mm, 28*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 10)
    c.drawString(24*mm, y_comp+3*mm, "Nivel de comprometimento:")
    bar_w = W - 80*mm; bar_x = 24*mm; bar_y = y_comp - 14*mm
    c.setFillColor(CINZA_CLARO)
    c.roundRect(bar_x, bar_y, bar_w, 8*mm, 4, fill=1, stroke=0)
    pct = min(comp_raw / 10.0, 1.0)
    fill_cor = VERDE_LIMA if pct >= 0.7 else colors.HexColor("#FFC000")
    c.setFillColor(fill_cor)
    c.roundRect(bar_x, bar_y, bar_w * pct, 8*mm, 4, fill=1, stroke=0)
    if pct > 0.15:
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 9)
        c.drawString(bar_x + 3*mm, bar_y + 2*mm, f"{int(comp_raw)}/10")
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 9)
    label_comp = "Excelente!" if pct >= 0.8 else ("Otimo!" if pct >= 0.6 else "Vamos la!")
    c.drawString(bar_x + bar_w + 3*mm, bar_y + 2*mm, label_comp)

    # alertas
    y_obs = y_comp - 28*mm
    obs_items = []
    if lim.lower() not in ["nenhuma","nao","none","","nao informado"]:
        obs_items.append(("Limitacao fisica", lim, LARANJA))
    if med.lower() not in ["nenhum","nao","none","","nao informado"]:
        obs_items.append(("Medicamento em uso", med, AZUL_INFO))
    for tit_obs, val_obs, cor_obs in obs_items:
        draw_rect(c, 20*mm, y_obs-14*mm, W-40*mm, 16*mm, fill=VERDE_BG)
        c.setFillColor(cor_obs)
        c.roundRect(20*mm, y_obs-14*mm, 5*mm, 16*mm, 2, fill=1, stroke=0)
        c.setFillColor(cor_obs)
        c.setFont(FONT_B, 9)
        c.drawString(29*mm, y_obs-5*mm, tit_obs.upper() + ":")
        c.setFillColor(TEXTO_ESCURO)
        c.setFont(FONT_N, 10)
        c.drawString(78*mm, y_obs-5*mm, str(val_obs)[:58])
        y_obs -= 20*mm

    rodape(c, 4)
    c.showPage()

# ── PÁGINA 5 — LAUDO OMS ─────────────────────────────────────────────────────
def pag_oms(c, d):
    draw_bg(c)
    draw_header_bar(c, "LAUDO DE ATIVIDADE FISICA", "Comparativo com as recomendacoes da OMS")

    exerc     = d.get("exercicio", "")
    t_treino  = d.get("tempo_treino", "")
    cardio    = d.get("cardio", "")
    t_cardio  = d.get("tempo_cardio", "")
    total_min, status, msg_oms = avaliar_oms(exerc, t_treino, cardio, t_cardio)

    # cor do status
    cor_status = {
        "insuficiente": colors.HexColor("#C0392B"),
        "parcial":      colors.HexColor("#E07B00"),
        "adequado":     VERDE_LIMA,
        "excelente":    VERDE_ESCURO,
    }.get(status, VERDE_MEDIO)

    label_status = {
        "insuficiente": "NIVEL INSUFICIENTE",
        "parcial":      "QUASE LA!",
        "adequado":     "DENTRO DA META OMS",
        "excelente":    "ACIMA DA META OMS",
    }.get(status, "")

    # card de status grande
    draw_rect(c, 20*mm, H-95*mm, W-40*mm, 48*mm, fill=VERDE_BG)
    c.setFillColor(cor_status)
    c.roundRect(20*mm, H-49*mm, W-40*mm, 5*mm, 2, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont(FONT_B, 11)
    c.drawCentredString(W/2, H-55*mm, label_status)
    c.setFillColor(cor_status)
    c.setFont(FONT_B, 32)
    c.drawCentredString(W/2, H-74*mm, f"{total_min} min/semana")
    c.setFillColor(TEXTO_MEDIO)
    c.setFont(FONT_N, 9)
    c.drawCentredString(W/2, H-86*mm, "atividade fisica estimada")

    # mensagem OMS
    draw_rect(c, 20*mm, H-126*mm, W-40*mm, 24*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_LIMA)
    c.roundRect(20*mm, H-104*mm, W-40*mm, 4*mm, 2, fill=1, stroke=0)
    wrap(c, msg_oms, 25*mm, H-110*mm, W-50*mm, size=10, cor=TEXTO_ESCURO)

    # recomendacao OMS
    y_rec = H - 138*mm
    draw_rect(c, 20*mm, y_rec-50*mm, W-40*mm, 54*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 11)
    c.drawString(24*mm, y_rec-6*mm, "Recomendacao da OMS para adultos:")

    recs = [
        ("Atividade moderada", "150 a 300 min/semana", "(caminhada, bike leve, natacao)"),
        ("Atividade vigorosa",  "75 a 150 min/semana",  "(corrida, HIIT, musculacao intensa)"),
    ]
    y_r = y_rec - 18*mm
    for tipo, meta, ex in recs:
        draw_rect(c, 24*mm, y_r-14*mm, W-48*mm, 16*mm,
                  fill=VERDE_ESCURO if "moderada" in tipo.lower() else VERDE_MEDIO)
        c.setFillColor(BRANCO)
        c.setFont(FONT_B, 9)
        c.drawString(28*mm, y_r-5*mm, tipo + ":")
        c.setFont(FONT_B, 10)
        c.drawString(85*mm, y_r-5*mm, meta)
        c.setFont(FONT_N, 8)
        c.setFillColor(VERDE_CLARO)
        c.drawString(130*mm, y_r-5*mm, ex)
        y_r -= 20*mm

    # como a consultoria ajuda
    y_cons = y_rec - 60*mm
    draw_rect(c, 20*mm, y_cons-42*mm, W-40*mm, 46*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_LIMA)
    c.roundRect(20*mm, y_cons-42*mm, 5*mm, 46*mm, 2, fill=1, stroke=0)
    c.setFillColor(VERDE_ESCURO)
    c.setFont(FONT_B, 11)
    c.drawString(29*mm, y_cons-8*mm, "Como o protocolo Luis Kummer vai te ajudar:")

    if status in ["insuficiente", "parcial"]:
        texto_cons = (
            "Seu protocolo sera montado para aumentar progressivamente seu volume de treino, "
            "respeitando seu ritmo atual e chegando gradualmente a meta da OMS. "
            "Com acompanhamento personalizado, voce vai evoluir de forma segura e sustentavel."
        )
    else:
        texto_cons = (
            "Parabens por ja atingir as recomendacoes da OMS! Seu protocolo vai potencializar "
            "ainda mais seus resultados, otimizando a qualidade dos seus treinos, "
            "periodizando corretamente e garantindo recuperacao adequada para maxima evolucao."
        )
    wrap(c, texto_cons, 29*mm, y_cons-20*mm, W-54*mm, size=10)

    rodape(c, 5)
    c.showPage()

# ── PÁGINA 6 — OFERTA / PLANOS ───────────────────────────────────────────────
def pag_oferta(c, d):
    draw_bg(c)
    draw_header_bar(c, "SEU PROTOCOLO PERSONALIZADO", "Escolha o plano ideal para voce")

    nome     = d.get("nome") or "voce"
    obj      = obj_texto(d.get("objetivo", ""))
    comp_raw = to_float(d.get("compro")) or 0

    nivel_txt = "seu alto nivel de comprometimento" if comp_raw >= 8 else (
        "seu comprometimento" if comp_raw >= 5 else "seu potencial")

    draw_rect(c, 20*mm, H-68*mm, W-40*mm, 26*mm, fill=VERDE_BG)
    c.setFillColor(VERDE_LIMA)
    c.roundRect(20*mm, H-44*mm, W-40*mm, 4*mm, 2, fill=1, stroke=0)
    wrap(c,
         f"Com base no seu objetivo de <b>{obj}</b> e em {nivel_txt} ({int(comp_raw)}/10), "
         f"selecionamos os protocolos abaixo. Cada um e montado do zero pelo Luis Kummer, "
         f"com exercicios em video, suporte direto e plano adaptado ao seu perfil.",
         25*mm, H-50*mm, W-50*mm, size=10)

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
    ph = 44*mm; gap = 4*mm; y_start = H - 75*mm
    for i, (titulo, desc, preco, url) in enumerate(planos):
        y = y_start - i*(ph+gap)
        draw_rect(c, 20*mm, y-ph, W-40*mm, ph, fill=VERDE_BG)
        c.setFillColor(VERDE_ESCURO)
        c.roundRect(20*mm, y-ph, 6*mm, ph, 2, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 12)
        c.drawString(30*mm, y-12*mm, titulo)
        c.setFillColor(TEXTO_MEDIO)
        c.setFont(FONT_N, 10)
        c.drawString(30*mm, y-22*mm, desc)
        c.setFillColor(DOURADO)
        c.setFont(FONT_B, 18)
        c.drawString(30*mm, y-36*mm, preco)
        bx = W-72*mm; bw = 48*mm; bh = 11*mm
        c.setFillColor(VERDE_LIMA)
        c.roundRect(bx, y-ph+10*mm, bw, bh, 3, fill=1, stroke=0)
        c.setFillColor(VERDE_ESCURO)
        c.setFont(FONT_B, 9)
        c.drawCentredString(bx+bw/2, y-ph+15*mm, "Quero este plano ->")
        c.linkURL(url, (bx, y-ph+10*mm, bx+bw, y-ph+21*mm), relative=0)

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
    pag_oms(c, dados)
    pag_oferta(c, dados)
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
        "cardio": "caminhada", "tempo_cardio": "20 min",
        "alimentacao": "alimentacao razoavel",
        "compro": "9", "estresse": "6",
    }
    pdf_bytes = gerar_pdf_diagnostico(dados_teste)
    with open("/mnt/user-data/outputs/diagnostico_v3.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("OK")
