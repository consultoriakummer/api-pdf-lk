import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

W, H = A4
CREME        = colors.HexColor("#FAF6F0")
BEGE_MEDIO   = colors.HexColor("#EDE3D5")
BEGE_ESCURO  = colors.HexColor("#C9B99A")
MARROM       = colors.HexColor("#6B4F35")
MARROM_CLARO = colors.HexColor("#8B6A4A")
TEXTO_ESCURO = colors.HexColor("#3A2E28")
TEXTO_MEDIO  = colors.HexColor("#5C4A3A")
BRANCO       = colors.white

def draw_bg(c):
    c.setFillColor(CREME)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_rect(c, x, y, w, h, fill=BEGE_MEDIO):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=0)

def rodape(c, num):
    c.setFillColor(BEGE_ESCURO)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 10*mm, f"Luis Kummer Personal  •  MFIT Personal  •  {num}/6")

def linha_div(c, y):
    c.setStrokeColor(BEGE_ESCURO)
    c.setLineWidth(0.8)
    c.line(20*mm, y, W-20*mm, y)

def wrap(c, texto, x, y, larg, size=10, cor=TEXTO_ESCURO):
    st = ParagraphStyle("s", fontName="Helvetica", fontSize=size,
                        textColor=cor, leading=15, alignment=TA_JUSTIFY)
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
    if p is None or a is None:
        return None
    if a > 3:
        a = a / 100
    if a == 0:
        return None
    return round(p / (a * a), 1)

def class_imc(imc):
    v = to_float(imc)
    if v is None:
        return "Não calculado"
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
        "definicao": "Definição muscular",
        "definir e tonificar": "Definição e tonificação",
    }
    return m.get(str(o).lower().strip(), str(o) if o else "Não informado")

def safe(val, sufixo=""):
    if val is None or str(val).strip() == "":
        return "Não informado"
    return f"{val}{sufixo}"

# ── PÁGINA 1 — CAPA ──────────────────────────────────────────────────────────
def pag_capa(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-55*mm, W, 55*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W/2, H-28*mm, "DIAGNOSTICO PERSONALIZADO")
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H-40*mm, "Luis Kummer Personal  |  MFIT Personal")

    nome = d.get("nome") or "Aluno(a)"
    c.setFillColor(MARROM)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W/2, H-80*mm, f"Ola, {nome}!")

    c.setFillColor(TEXTO_MEDIO)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H-93*mm, "Preparamos este diagnostico exclusivo com base nas suas respostas.")

    linha_div(c, H-105*mm)

    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    caixas = [
        ("Objetivo",     obj_texto(d.get("objetivo", ""))),
        ("IMC",          safe(imc_val)),
        ("Compromisso",  f"{safe(d.get('compro'))}/10"),
    ]
    cw = (W-40*mm)/3
    for i, (lbl, val) in enumerate(caixas):
        cx = 20*mm + i*cw
        draw_rect(c, cx, H-165*mm, cw-5*mm, 40*mm)
        c.setFillColor(MARROM)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx+(cw-5*mm)/2, H-133*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(cx+(cw-5*mm)/2, H-148*mm, str(val)[:25])

    draw_rect(c, 20*mm, H-240*mm, W-40*mm, 55*mm)
    c.setFillColor(MARROM)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W/2, H-197*mm, "Sua transformacao comeca com um passo.")
    wrap(c,
         "Este diagnostico foi elaborado por Luis Kummer com base no seu perfil individual. "
         "Cada protocolo e criado do zero, respeitando seu corpo, sua rotina e seus objetivos.",
         25*mm, H-213*mm, W-50*mm)

    rodape(c, 1)
    c.showPage()

# ── PÁGINA 2 — BIOMÉTRICO ────────────────────────────────────────────────────
def pag_bio(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-30*mm, W, 30*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W/2, H-20*mm, "DADOS BIOMETRICOS")

    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))

    campos = [
        ("Peso atual",    safe(d.get("peso"), " kg")),
        ("Altura",        safe(d.get("altura"), " cm")),
        ("Idade",         safe(d.get("idade"), " anos")),
        ("Peso objetivo", safe(d.get("peso_obj"), " kg")),
        ("IMC",           safe(imc_val)),
        ("Classificacao", class_imc(imc_val)),
    ]
    cw = (W-40*mm)/2
    for i, (lbl, val) in enumerate(campos):
        col = i % 2
        row = i // 2
        cx = 20*mm + col*cw
        cy = H-70*mm - row*32*mm
        draw_rect(c, cx, cy-24*mm, cw-6*mm, 26*mm)
        c.setFillColor(MARROM_CLARO)
        c.setFont("Helvetica", 9)
        c.drawString(cx+4*mm, cy-8*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(cx+4*mm, cy-19*mm, str(val)[:30])

    rodape(c, 2)
    c.showPage()

# ── PÁGINA 3 — META E HÁBITOS ────────────────────────────────────────────────
def pag_meta(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-30*mm, W, 30*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W/2, H-20*mm, "META E HABITOS")

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
    y = H-45*mm
    for lbl, val in itens:
        draw_rect(c, 20*mm, y-14*mm, W-40*mm, 16*mm)
        c.setFillColor(MARROM_CLARO)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(24*mm, y-5*mm, lbl.upper() + ":")
        c.setFillColor(TEXTO_ESCURO)
        c.setFont("Helvetica", 10)
        c.drawString(80*mm, y-5*mm, str(val)[:60])
        y -= 20*mm

    rodape(c, 3)
    c.showPage()

# ── PÁGINA 4 — ANÁLISE DO PERFIL ─────────────────────────────────────────────
def pag_perfil(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-30*mm, W, 30*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W/2, H-20*mm, "ANALISE DO SEU PERFIL")

    nome = d.get("nome") or "voce"
    obj  = obj_texto(d.get("objetivo", ""))
    comp = safe(d.get("compro"))
    alim = safe(d.get("alimentacao"))
    lim  = str(d.get("limitacao") or "nenhuma limitacao relatada")
    med  = str(d.get("medicamentos") or "nenhum")

    texto = (
        f"{nome}, com base nas suas respostas, identificamos que seu principal objetivo e "
        f"<b>{obj}</b>. Seu nivel de comprometimento declarado e <b>{comp}/10</b> — isso ja "
        f"mostra que voce esta pronto(a) para comecar. Sua alimentacao atual e descrita como "
        f"<b>{alim}</b>, o que nos ajuda a calibrar a intensidade e o tipo de protocolo ideal. "
    )
    if lim.lower() not in ["nenhuma", "nao", "none", "", "nenhuma limitacao relatada", "não informado"]:
        texto += f"Registramos a seguinte limitacao fisica: <b>{lim}</b> — isso sera respeitado no seu protocolo. "
    if med.lower() not in ["nenhum", "nao", "none", "", "não informado"]:
        texto += f"Sobre medicamentos: <b>{med}</b> — esse dado e considerado na montagem do plano. "
    texto += (
        "Seu protocolo sera montado do zero, com exercicios em video, acompanhamento direto "
        "e suporte pelo app. Vamos juntos transformar sua rotina!"
    )

    draw_rect(c, 20*mm, H-210*mm, W-40*mm, 165*mm)
    wrap(c, texto, 25*mm, H-52*mm, W-50*mm, size=11)

    rodape(c, 4)
    c.showPage()

# ── PÁGINA 5 — OFERTA / PLANOS ───────────────────────────────────────────────
def pag_oferta(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-30*mm, W, 30*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W/2, H-20*mm, "SEU PROTOCOLO PERSONALIZADO")

    c.setFillColor(TEXTO_MEDIO)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H-38*mm, "Escolha o plano ideal para comecar sua transformacao:")

    planos = [
        ("Individual - 1 Protocolo", "60 dias de acompanhamento", "R$ 119",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636"),
        ("Dupla - 1 Protocolo", "60 dias para voce + 1 pessoa", "R$ 207",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112637&page=112636"),
        ("Individual - 3 Protocolos", "180 dias de acompanhamento", "R$ 297",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112638&page=112636"),
        ("Dupla - 3 Protocolos", "180 dias para voce + 1 pessoa", "R$ 479",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112639&page=112636"),
    ]

    ph = 50*mm
    gap = 5*mm
    y_start = H - 50*mm

    for i, (titulo, desc, preco, url) in enumerate(planos):
        y = y_start - i*(ph+gap)
        draw_rect(c, 20*mm, y-ph, W-40*mm, ph)
        c.setFillColor(MARROM)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(25*mm, y-10*mm, titulo)
        c.setFillColor(TEXTO_MEDIO)
        c.setFont("Helvetica", 10)
        c.drawString(25*mm, y-20*mm, desc)
        c.setFillColor(MARROM)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(25*mm, y-34*mm, preco)
        bx = W-75*mm
        bw = 50*mm
        bh = 10*mm
        c.setFillColor(MARROM)
        c.roundRect(bx, y-ph+8*mm, bw, bh, 3, fill=1, stroke=0)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(bx+bw/2, y-ph+13*mm, "Quero este plano ->")
        c.linkURL(url, (bx, y-ph+8*mm, bx+bw, y-ph+18*mm), relative=0)

    rodape(c, 5)
    c.showPage()

# ── PÁGINA 6 — DEPOIMENTOS ───────────────────────────────────────────────────
def pag_depoimentos(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-30*mm, W, 30*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W/2, H-20*mm, "RESULTADOS REAIS")

    deps = [
        ("Ana Paula, 34 anos",
         "Perdi 8kg em 60 dias seguindo o protocolo do Luis. O acompanhamento pelo app fez toda a diferenca!"),
        ("Marcos e Juliana",
         "Fizemos o plano dupla e foi incrivel! Nos motivamos juntos e os resultados vieram rapido."),
        ("Fernanda, 28 anos",
         "Nunca pensei que conseguiria manter uma rotina de treinos. O protocolo e pratico e eficiente!"),
        ("Cristiane, 41 anos",
         "Com duas filhas e trabalho nao sobrava tempo. O Luis montou um treino perfeito para minha realidade."),
    ]

    y = H-45*mm
    for nome, dep in deps:
        h_box = 38*mm
        draw_rect(c, 20*mm, y-h_box, W-40*mm, h_box)
        c.setFillColor(MARROM)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(25*mm, y-8*mm, nome)
        wrap(c, dep, 25*mm, y-18*mm, W-50*mm, size=10)
        y -= h_box + 5*mm

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
