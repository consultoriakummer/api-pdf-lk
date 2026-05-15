import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

W, H = A4
CREME        = colors.HexColor("#FAF6F0")
BEGE_MEDIO   = colors.HexColor("#EDE3D5")
BEGE_ESCURO  = colors.HexColor("#C9B99A")
MARROM       = colors.HexColor("#6B4F35")
MARROM_CLARO = colors.HexColor("#8B6A4A")
TEXTO_ESCURO = colors.HexColor("#3A2E28")
TEXTO_MEDIO  = colors.HexColor("#5C4A3A")
BRANCO       = colors.white
VERDE_SUAVE  = colors.HexColor("#7A9E7E")
LARANJA_SUB  = colors.HexColor("#C8874A")

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

def calc_imc(peso, altura):
    try:
        p = float(str(peso).replace(",","."))
        a = float(str(altura).replace(",","."))
        if a > 3: a = a/100
        return round(p/(a*a), 1)
    except:
        return None

def class_imc(imc):
    if imc is None: return "–"
    if imc < 18.5: return "Abaixo do peso"
    if imc < 25:   return "Peso normal"
    if imc < 30:   return "Sobrepeso"
    if imc < 35:   return "Obesidade grau I"
    if imc < 40:   return "Obesidade grau II"
    return "Obesidade grau III"

def obj_texto(o):
    m = {"perder_peso":"Perda de peso","ganhar_massa":"Ganho de massa",
         "qualidade_vida":"Qualidade de vida","definicao":"Definição muscular"}
    return m.get(o, o or "Não informado")

# ── PÁGINA 1 ─ CAPA ──────────────────────────────────────────────────────────
def pag_capa(c, d):
    draw_bg(c)
    c.setFillColor(MARROM)
    c.rect(0, H-55*mm, W, 55*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W/2, H-28*mm, "DIAGNÓSTICO PERSONALIZADO")
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H-40*mm, "Luis Kummer Personal · MFIT Personal")

    nome = d.get("nome","Aluno(a)")
    c.setFillColor(MARROM)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W/2, H-80*mm, f"Olá, {nome}!")

    c.setFillColor(TEXTO_MEDIO)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H-93*mm, "Preparamos este diagnóstico exclusivo com base nas suas respostas.")

    linha_div(c, H-105*mm)

    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    caixas = [
        ("Objetivo",     obj_texto(d.get("objetivo",""))),
        ("IMC",          str(imc_val or "–")),
        ("Compromisso",  f"{d.get('compro','–')}/10"),
    ]
    cw = (W-40*mm)/3
    for i,(lbl,val) in enumerate(caixas):
        cx = 20*mm + i*cw
        draw_rect(c, cx, H-165*mm, cw-5*mm, 40*mm)
        c.setFillColor(MARROM); c.setFont("Helvetica-Bold",9)
        c.drawCentredString(cx+(cw-5*mm)/2, H-133*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO); c.setFont("Helvetica-Bold",12)
        c.drawCentredString(cx+(cw-5*mm)/2, H-148*mm, val)

    draw_rect(c, 20*mm, H-240*mm, W-40*mm, 55*mm)
    c.setFillColor(MARROM); c.setFont("Helvetica-Bold",12)
    c.drawCentredString(W/2, H-197*mm, "Sua transformação começa com um passo.")
    wrap(c, "Este diagnóstico foi elaborado por Luis Kummer com base no seu perfil individual. "
         "Cada protocolo é criado do zero, respeitando seu corpo, sua rotina e seus objetivos.",
         25*mm, H-213*mm, W-50*mm)

    rodape(c, 1); c.showPage()

# ── PÁGINA 2 ─ BIOMÉTRICO ────────────────────────────────────────────────────
def pag_bio(c, d):
    draw_bg(c)
    c.setFillColor(MARROM); c.rect(0,H-30*mm,W,30*mm,fill=1,stroke=0)
    c.setFillColor(BRANCO); c.setFont("Helvetica-Bold",15)
    c.drawCentredString(W/2, H-20*mm, "DADOS BIOMÉTRICOS")

    imc_val = d.get("imc") or calc_imc(d.get("peso"), d.get("altura"))
    campos = [
        ("Peso atual",    f"{d.get('peso','–')} kg"),
        ("Altura",        f"{d.get('altura','–')} cm"),
        ("Idade",         f"{d.get('idade','–')} anos"),
        ("Peso objetivo", f"{d.get('peso_obj','–')} kg"),
        ("IMC",           str(imc_val or "–")),
        ("Classificação", class_imc(imc_val)),
    ]
    cw = (W-40*mm)/2
    for i,(lbl,val) in enumerate(campos):
        col = i%2; row = i//2
        cx = 20*mm + col*cw
        cy = H-70*mm - row*32*mm
        draw_rect(c, cx, cy-24*mm, cw-6*mm, 26*mm)
        c.setFillColor(MARROM_CLARO); c.setFont("Helvetica",9)
        c.drawString(cx+4*mm, cy-8*mm, lbl.upper())
        c.setFillColor(TEXTO_ESCURO); c.setFont("Helvetica-Bold",13)
        c.drawString(cx+4*mm, cy-19*mm, val)

    rodape(c, 2); c.showPage()

# ── PÁGINA 3 ─ META E HÁBITOS ────────────────────────────────────────────────
def pag_meta(c, d):
    draw_bg(c)
    c.setFillColor(MARROM); c.rect(0,H-30*mm,W,30*mm,fill=1,stroke=0)
    c.setFillColor(BRANCO); c.setFont("Helvetica-Bold",15)
    c.drawCentredString(W/2, H-20*mm, "META E HÁBITOS")

    itens = [
        ("Objetivo principal",  obj_texto(d.get("objetivo",""))),
        ("Alimentação",         d.get("alimentacao","Não informado")),
        ("Exercício atual",     d.get("exercicio","Não informado")),
        ("Tempo de treino",     d.get("tempo_treino","Não informado")),
        ("Cardio",              d.get("cardio","Não informado")),
        ("Nível de estresse",   d.get("estresse","Não informado")),
        ("Comprometimento",     f"{d.get('compro','–')}/10"),
        ("Limitações",          d.get("limitacao","Nenhuma")),
    ]
    y = H-45*mm
    for lbl, val in itens:
        draw_rect(c, 20*mm, y-14*mm, W-40*mm, 16*mm)
        c.setFillColor(MARROM_CLARO); c.setFont("Helvetica-Bold",9)
        c.drawString(24*mm, y-5*mm, lbl.upper()+":")
        c.setFillColor(TEXTO_ESCURO); c.setFont("Helvetica",10)
        c.drawString(80*mm, y-5*mm, str(val)[:60])
        y -= 20*mm

    rodape(c, 3); c.showPage()

# ── PÁGINA 4 ─ ANÁLISE DO PERFIL ─────────────────────────────────────────────
def pag_perfil(c, d):
    draw_bg(c)
    c.setFillColor(MARROM); c.rect(0,H-30*mm,W,30*mm,fill=1,stroke=0)
    c.setFillColor(BRANCO); c.setFont("Helvetica-Bold",15)
    c.drawCentredString(W/2, H-20*mm, "ANÁLISE DO SEU PERFIL")

    nome = d.get("nome","você")
    obj  = obj_texto(d.get("objetivo",""))
    comp = d.get("compro","?")
    alim = d.get("alimentacao","não informada")
    lim  = d.get("limitacao","nenhuma limitação relatada")
    med  = d.get("medicamentos","nenhum")

    texto = (
        f"{nome}, com base nas suas respostas, identificamos que seu principal objetivo é <b>{obj}</b>. "
        f"Seu nível de comprometimento declarado é <b>{comp}/10</b> — isso já mostra que você está pronta para começar. "
        f"Sua alimentação atual é descrita como <b>{alim}</b>, o que nos ajuda a calibrar a intensidade e o tipo de protocolo ideal. "
    )
    if lim and lim.lower() not in ["nenhuma","não","nao","none",""]:
        texto += f"Registramos a seguinte limitação física: <b>{lim}</b> — isso será respeitado no seu protocolo. "
    if med and med.lower() not in ["nenhum","não","nao","none",""]:
        texto += f"Sobre medicamentos: <b>{med}</b> — esse dado é considerado na montagem do plano. "
    texto += (
        "Seu protocolo será montado do zero, com exercícios em vídeo, acompanhamento direto e suporte pelo app. "
        "Vamos juntos transformar sua rotina!"
    )

    draw_rect(c, 20*mm, H-200*mm, W-40*mm, 155*mm)
    wrap(c, texto, 25*mm, H-52*mm, W-50*mm, size=11)

    rodape(c, 4); c.showPage()

# ── PÁGINA 5 ─ OFERTA / PLANOS ───────────────────────────────────────────────
def pag_oferta(c, d):
    draw_bg(c)
    c.setFillColor(MARROM); c.rect(0,H-30*mm,W,30*mm,fill=1,stroke=0)
    c.setFillColor(BRANCO); c.setFont("Helvetica-Bold",15)
    c.drawCentredString(W/2, H-20*mm, "SEU PROTOCOLO PERSONALIZADO")

    c.setFillColor(TEXTO_MEDIO); c.setFont("Helvetica",10)
    c.drawCentredString(W/2, H-38*mm, "Escolha o plano ideal para começar sua transformação:")

    planos = [
        ("Individual · 1 Protocolo", "60 dias de acompanhamento", "R$ 119",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636"),
        ("Dupla · 1 Protocolo",      "60 dias para você + 1 pessoa", "R$ 207",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112637&page=112636"),
        ("Individual · 3 Protocolos","180 dias de acompanhamento", "R$ 297",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112638&page=112636"),
        ("Dupla · 3 Protocolos",     "180 dias para você + 1 pessoa","R$ 479",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112639&page=112636"),
    ]

    ph = 52*mm
    gap = 6*mm
    total_h = len(planos)*(ph+gap)
    y_start = H-50*mm - (H-50*mm-30*mm-total_h)/2

    for i,(titulo,desc,preco,url) in enumerate(planos):
        y = y_start - i*(ph+gap)
        draw_rect(c, 20*mm, y-ph, W-40*mm, ph, fill=BEGE_MEDIO)
        c.setFillColor(MARROM); c.setFont("Helvetica-Bold",13)
        c.drawString(25*mm, y-10*mm, titulo)
        c.setFillColor(TEXTO_MEDIO); c.setFont("Helvetica",10)
        c.drawString(25*mm, y-20*mm, desc)
        c.setFillColor(MARROM); c.setFont("Helvetica-Bold",18)
        c.drawString(25*mm, y-34*mm, preco)
        # botão
        bx = W-75*mm; bw = 50*mm; bh = 10*mm
        c.setFillColor(MARROM)
        c.roundRect(bx, y-ph+8*mm, bw, bh, 3, fill=1, stroke=0)
        c.setFillColor(BRANCO); c.setFont("Helvetica-Bold",9)
        c.drawCentredString(bx+bw/2, y-ph+13*mm, "Quero este plano →")
        c.linkURL(url, (bx, y-ph+8*mm, bx+bw, y-ph+18*mm), relative=0)

    rodape(c, 5); c.showPage()

# ── PÁGINA 6 ─ DEPOIMENTOS ───────────────────────────────────────────────────
def pag_depoimentos(c, d):
    draw_bg(c)
    c.setFillColor(MARROM); c.rect(0,H-30*mm,W,30*mm,fill=1,stroke=0)
    c.setFillColor(BRANCO); c.setFont("Helvetica-Bold",15)
    c.drawCentredString(W/2, H-20*mm, "RESULTADOS REAIS")

    deps = [
        ("Ana Paula, 34 anos",
         "Perdi 8kg em 60 dias seguindo o protocolo do Luis. O acompanhamento pelo app fez toda a diferença!"),
        ("Marcos e Juliana",
         "Fizemos o plano dupla e foi incrível! Nos motivamos juntos e os resultados vieram rápido."),
        ("Fernanda, 28 anos",
         "Nunca pensei que conseguiria manter uma rotina de treinos. O protocolo é prático e eficiente!"),
        ("Cristiane, 41 anos",
         "Com duas filhas e trabalho não sobrava tempo. O Luis montou um treino perfeito para minha realidade."),
    ]

    y = H-45*mm
    for nome, dep in deps:
        h_box = 38*mm
        draw_rect(c, 20*mm, y-h_box, W-40*mm, h_box, fill=BEGE_MEDIO)
        c.setFillColor(MARROM); c.setFont("Helvetica-Bold",10)
        c.drawString(25*mm, y-8*mm, f'"{nome}"')
        wrap(c, dep, 25*mm, y-18*mm, W-50*mm, size=10)
        y -= h_box + 5*mm

    rodape(c, 6); c.showPage()

# ── FUNÇÃO PRINCIPAL ─────────────────────────────────────────────────────────
def gerar_pdf_diagnostico(dados):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Diagnóstico Personalizado - Luis Kummer")

    # garante IMC calculado
    if not dados.get("imc"):
        dados["imc"] = calc_imc(dados.get("peso"), dados.get("altura"))

    pag_capa(c, dados)
    pag_bio(c, dados)
    pag_meta(c, dados)
    pag_perfil(c, dados)
    pag_oferta(c, dados)
    pag_depoimentos(c, dados)

    c.save()
    buf.seek(0)
    return buf.read()
