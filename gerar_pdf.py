import io, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOJI_DIR = os.path.join(BASE_DIR, "emojis")
TOTAL_PAGES = 9

def _reg():
    b = BASE_DIR
    try:
        pdfmetrics.registerFont(TTFont("DV",  os.path.join(b,"DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DVB", os.path.join(b,"DejaVuSans-Bold.ttf")))
        return "DV","DVB"
    except:
        return "Helvetica","Helvetica-Bold"
FN, FB = _reg()

# ── PALETA ───────────────────────────────────────────────────────────────────
PF=colors.HexColor("#0D120D"); PC=colors.HexColor("#1A231A"); PB=colors.HexColor("#2A382A")
VD=colors.HexColor("#1F3D1A"); VN=colors.HexColor("#39FF14"); VN2=colors.HexColor("#2ECC11")
CT=colors.HexColor("#A8C4A8"); CS=colors.HexColor("#5A7A5A")
LF=colors.HexColor("#F4FAF4"); LC=colors.white; LCG=colors.HexColor("#EBF5EB")
LB=colors.HexColor("#C8E6C9"); VM=colors.HexColor("#2E7D32"); VCL=colors.HexColor("#4CAF50")
VT=colors.HexColor("#E8F5E9"); TD=colors.HexColor("#1A2E1A"); TM=colors.HexColor("#4A6A4A")
TS=colors.HexColor("#7A9A7A"); BR=colors.white
LA=colors.HexColor("#E65100"); VE=colors.HexColor("#E53935")
AZ=colors.HexColor("#1565C0"); AM=colors.HexColor("#F9A825")
AZUL_CARD=colors.HexColor("#E3F2FD"); AZUL_B=colors.HexColor("#1976D2")

# ── EMOJI ─────────────────────────────────────────────────────────────────────
_ecache={}
def draw_em(c, nome, x, y, size=5):
    if nome not in _ecache:
        p=os.path.join(EMOJI_DIR,f"{nome}.png")
        _ecache[nome]=p if os.path.exists(p) else None
    if _ecache[nome]:
        s=size*mm
        # Centraliza verticalmente: desce 15% para alinhar com texto
        c.drawImage(_ecache[nome],x,y-s*0.85,width=s,height=s,
                    preserveAspectRatio=True,mask='auto')

# ── TEXTO ─────────────────────────────────────────────────────────────────────
def wrap(c,txt,x,y,larg,size=10,cor=TD,leading=14,align=TA_LEFT):
    st=ParagraphStyle("s",fontName=FN,fontSize=size,textColor=cor,leading=leading,alignment=align)
    p=Paragraph(str(txt),st); p.wrapOn(c,larg,999); p.drawOn(c,x,y-p.height)
    return y-p.height

def safe(v):
    if v is None or str(v).strip() in ["","None"]: return "–"
    return str(v)

def f2(v):
    try: return float(str(v).replace(",","."))
    except: return None

def calc_imc(peso,alt):
    p=f2(peso);a=f2(alt)
    if not p or not a: return None
    if a>3: a/=100
    return round(p/(a*a),1) if a else None

def class_imc(v):
    v=f2(v)
    if v is None: return "Não calculado"
    if v<18.5: return "Abaixo do peso"
    if v<25:   return "Peso normal"
    if v<30:   return "Sobrepeso"
    if v<35:   return "Obesidade I"
    return "Obesidade II/III"

def cor_imc(v):
    v=f2(v)
    if v is None: return TS
    if v<18.5: return AZ
    if v<25:   return VM
    if v<30:   return AM
    if v<35:   return LA
    return VE

def data_hoje():
    meses=["janeiro","fevereiro","março","abril","maio","junho",
           "julho","agosto","setembro","outubro","novembro","dezembro"]
    d=datetime.now(); return f"{d.day} de {meses[d.month-1]} de {d.year}"

# ── MAPEAMENTOS ───────────────────────────────────────────────────────────────
def obj_txt(o):
    m={"emagrecer":"Emagrecer e perder gordura","definir":"Definir e tonificar",
       "ganhar_massa":"Ganhar massa e força","saude":"Saúde e disposição",
       "pos_parto":"Recuperação pós-parto","perder_peso":"Perda de peso"}
    return m.get(str(o or "").lower().strip(),str(o) if o else "Não informado")

def ex_txt(e):
    m={"nao":"Não pratico musculação","1x":"1-2x por semana","3x":"3-4x por semana","5x":"5x ou mais/sem"}
    return m.get(str(e or "").lower().strip(),str(e) if e else "–")

def fc_txt(f):
    m={"nao":"Não faz cardio","1x":"1-2x por semana","3x":"3-4x por semana","5x":"5x ou mais/sem"}
    return m.get(str(f or "").lower().strip(),str(f) if f else "–")

def tt_txt(t):
    m={"nao_treino":"–","menos30":"< 30 min","30a45":"30–45 min","45a60":"45–60 min","mais60":"> 60 min"}
    return m.get(str(t or "").lower().strip(),str(t) if t else "–")

def tc_txt(t):
    m={"nao_faco":"–","menos20":"< 20 min","20a30":"20–30 min","30a45":"30–45 min","mais45":"> 45 min"}
    return m.get(str(t or "").lower().strip(),str(t) if t else "–")

def al_txt(a):
    m={"muito_ruim":"Muito irregular","ruim":"Precisa melhorar","media":"Razoável","boa":"Boa rotina"}
    return m.get(str(a or "").lower().strip(),str(a) if a else "–")

def cardio_txt(cv):
    m={"nao":"–","caminhada":"Caminhada","corrida":"Corrida","bike":"Bike/ciclismo",
       "natacao":"Natação","hiit":"HIIT/funcional","danca":"Dança/zumba","outro":"Outro"}
    if not cv or str(cv).strip() in ["","None"]: return "–"
    return ", ".join(m.get(p.strip(),p.strip()) for p in str(cv).split(",") if p.strip())

def ob_txt(o):
    m={"tempo":"Falta de tempo","motivacao":"Falta de motivação",
       "orientacao":"Não sabe por onde começar","alimentacao":"Dificuldade alimentar",
       "dinheiro":"Custo/investimento","saude":"Questões de saúde","nada":"Nada me atrapalha"}
    if not o or str(o).strip() in ["","None"]: return "–"
    return ", ".join(m.get(p.strip(),p.strip()) for p in str(o).split(",") if p.strip())

def cardio_intensidade(cv):
    """Classifica intensidade do cardio para fins OMS"""
    if not cv: return "moderada"
    cv=str(cv).lower()
    if any(x in cv for x in ["hiit","corrida"]): return "vigorosa"
    return "moderada"

# ── META ──────────────────────────────────────────────────────────────────────
def meta(d):
    obj=str(d.get("objetivo") or "").lower()
    peso=f2(d.get("peso")); pobj=f2(d.get("peso_obj"))
    imc=f2(d.get("imc")) or calc_imc(d.get("peso"),d.get("altura"))
    ex=str(d.get("exercicio") or "").lower(); sx=str(d.get("sexo") or "").lower()
    emag=obj in ["emagrecer","perder_peso"] or "perder" in obj or (peso and pobj and peso-pobj>2)
    massa=obj in ["ganhar_massa"] or "massa" in obj
    parto=obj in ["pos_parto"]; defin=obj in ["definir"] or "defin" in obj
    if emag and peso and pobj:
        diff=peso-pobj
        if diff<=0: return {"tipo":"ok"}
        iv=f2(imc) or 25
        taxa=0.3 if iv<25 else (0.5 if iv<30 else (0.75 if iv<35 else 1.0))
        meses=max(1,round((diff/taxa)/4.3))
        return {"tipo":"emagrec","diff":round(diff,1),"taxa":taxa,"meses":meses,"pa":peso,"po":pobj}
    elif massa:
        gn=0.15 if ex=="5x" else (0.3 if ex=="3x" else 0.5)
        gx=0.45 if ex=="5x" else (0.6 if ex=="3x" else 0.8)
        if "m" in sx[:2]: gn=round(gn*1.5,1);gx=round(gx*1.5,1)
        return {"tipo":"massa","g3n":round(gn*3,1),"g3x":round(gx*3,1),"g6n":round(gn*6,1),"g6x":round(gx*6,1)}
    elif parto: return {"tipo":"parto"}
    elif defin: return {"tipo":"defin"}
    return {"tipo":"saude"}

def oms_detalhado(d):
    """Retorna breakdown detalhado: musculação + cardio separados"""
    es=str(d.get("exercicio") or "").lower(); ts=str(d.get("tempo_treino") or "").lower()
    cs=str(d.get("cardio") or "").lower();   ct=str(d.get("tempo_cardio") or "").lower()
    fc=str(d.get("freq_cardio") or "").lower()

    freq_musc={"1x":1,"3x":3,"5x":5}.get(es,0)
    mt_musc={"menos30":20,"30a45":37,"45a60":52,"mais60":75}.get(ts,0)
    min_musc=freq_musc*mt_musc

    freq_card={"1x":1,"3x":3,"5x":5}.get(fc,0)
    mt_card={"menos20":15,"20a30":25,"30a45":37,"mais45":52}.get(ct,0)
    min_card=freq_card*mt_card if cs not in ["nao","","none"] else 0

    # Cardio vigoroso vale 2x na OMS
    intens=cardio_intensidade(cs)
    min_card_equiv=min_card*2 if intens=="vigorosa" else min_card

    total=min_musc+min_card_equiv
    st="insuf" if total<75 else ("parcial" if total<150 else ("ok" if total<=300 else "exce"))

    return {
        "min_musc":min_musc,"freq_musc":freq_musc,
        "min_card":min_card,"freq_card":freq_card,
        "min_card_equiv":min_card_equiv,"intens":intens,
        "total":total,"status":st,
        "tipo_cardio":cardio_txt(cs),"tempo_cardio":tc_txt(ct)
    }

def dicas(d):
    out=[]
    obj=str(d.get("objetivo") or "").lower(); ex=str(d.get("exercicio") or "").lower()
    al=str(d.get("alimentacao") or "").lower(); es=f2(d.get("estresse")) or 0
    co=f2(d.get("compro")) or 0; ob=str(d.get("obstaculo") or "").lower()
    li=str(d.get("limitacao") or "").lower(); me=str(d.get("medicamento") or d.get("medicamentos") or "").lower()
    oms=oms_detalhado(d)

    if co>=8:
        out.append(("trofeu",AM,"Comprometimento excepcional!",
            f"Você declarou {int(co)}/10 — esse é o ingrediente mais raro na transformação. A maioria desiste por falta de comprometimento. Você já passou dessa etapa."))
    elif co>=6:
        out.append(("musculo",VM,"Bom comprometimento!",
            f"Nível {int(co)}/10 — você está no caminho certo. Com o protocolo adequado os resultados aparecem em 4 a 6 semanas."))

    if es>=7:
        out.append(("raiva",VE,"Estresse alto interfere nos resultados",
            "Cortisol elevado dificulta a perda de gordura e prejudica a recuperação muscular. Seu protocolo vai considerar isso. Dica imediata: 7–8h de sono e 10 min de caminhada ao ar livre já fazem diferença."))
    elif es>=5:
        out.append(("aviso",LA,"Estresse moderado — fique de olho",
            f"Nível {int(es)}/10. Estresse crônico sabota resultados mesmo com treino correto. Priorize sono de qualidade e momentos de descanso ativo ao longo da semana."))

    if al in ["muito_ruim","ruim"]:
        out.append(("salada",VCL,"Comece pela proteína em cada refeição",
            "Não precisa contar calorias agora. Montar o prato com proteína primeiro (frango, ovo, peixe) reduz naturalmente o excesso calórico e protege a massa muscular durante o emagrecimento."))
    elif al=="media":
        out.append(("salada",VM,"Alimentação razoável — um ajuste resolve",
            "Foque em aumentar proteína e reduzir açúcar líquido (refrigerante, suco industrializado). Essas duas mudanças aceleram os resultados sem virar a rotina de cabeça pra baixo."))

    if ex=="nao":
        out.append(("correr",AZ,"Comece com 10 minutos — sério",
            "10 minutos de caminhada após o almoço já reduz glicemia, melhora disposição e cria o hábito. Seu protocolo vai progredir gradualmente, sem sobrecarga."))
    elif ex=="1x":
        out.append(("correr",VM,"1–2x/semana é um ótimo ponto de partida",
            "Seu protocolo vai evoluir para 3x com treinos de 30–40 min. Essa progressão dobra seus resultados sem aumentar muito o tempo dedicado."))

    if oms["min_card"]==0 and oms["status"] in ["insuf","parcial"]:
        out.append(("bike",VCL,"Adicione cardio 2x por semana",
            f"Você está com {oms['total']} min/semana. Duas sessões de 30 min de caminhada rápida ou bike já chegam perto da meta OMS de 150 min. Pequeno ajuste, grande resultado."))
    elif oms["min_card"]>0 and oms["intens"]=="moderada":
        out.append(("bike",VM,f"Cardio: {oms['tipo_cardio']} — ótima escolha",
            f"Você faz {oms['freq_card']}x por semana com sessões de {oms['tempo_cardio']}. Isso representa {oms['min_card']} min/semana. Manter essa consistência é fundamental para os resultados."))

    if "tempo" in ob:
        out.append(("relogio",colors.HexColor("#7B1FA2"),"Falta de tempo — tem solução",
            "Treinos de 30 min 3x/semana superam qualquer treino de 1h esporádico. Seu protocolo foi desenhado para caber na vida real, não na vida ideal. Consistência supera duração."))

    if obj=="pos_parto" or "parto" in obj:
        out.append(("coracao",colors.HexColor("#E91E63"),"Seu corpo merece atenção especial",
            "O abdômen pós-parto passa por mudanças reais (diástase). Exercícios genéricos podem piorar a condição. Seu protocolo vai incluir exercícios específicos e seguros para essa fase."))

    if li and li not in ["nao","nenhuma","","–","nao informado"]:
        out.append(("aviso",LA,"Limitação física — protocolo adaptado",
            "Sua limitação foi registrada e será considerada. Treinar com compensação postural aumenta risco de lesão. Seu protocolo vai respeitar esses limites."))

    if me and me not in ["nao","nenhum","","–","nao informado"]:
        out.append(("remedio",AZ,"Medicamentos considerados no protocolo",
            "Alguns medicamentos afetam metabolismo e recuperação. Seu protocolo será montado levando isso em conta para garantir progressão segura e eficiente."))

    return out[:6]

# ── PRIMITIVAS ────────────────────────────────────────────────────────────────
def bg_dark(c): c.setFillColor(PF); c.rect(0,0,W,H,fill=1,stroke=0)
def bg_light(c): c.setFillColor(LF); c.rect(0,0,W,H,fill=1,stroke=0)

def card_d(c,x,y,w,h,fill=PC,r=3,borda=PB):
    c.setFillColor(fill); c.roundRect(x,y,w,h,r*mm,fill=1,stroke=0)
    if borda: c.setStrokeColor(borda); c.setLineWidth(0.7); c.roundRect(x,y,w,h,r*mm,fill=0,stroke=1)

def card_l(c,x,y,w,h,fill=LC,r=3,borda=LB):
    c.setFillColor(fill); c.roundRect(x,y,w,h,r*mm,fill=1,stroke=0)
    if borda: c.setStrokeColor(borda); c.setLineWidth(0.6); c.roundRect(x,y,w,h,r*mm,fill=0,stroke=1)

def nline(c,x,y,w,h=1.5):
    c.setStrokeColor(VN); c.setLineWidth(h); c.line(x,y,x+w,y)

def vline(c,x,y,w,h=1.0):
    c.setStrokeColor(VM); c.setLineWidth(h); c.line(x,y,x+w,y)

def barra(c,x,y,w,hmm,pct,cor=VM,bg=LCG):
    hh=hmm*mm; c.setFillColor(bg); c.roundRect(x,y,w,hh,2*mm,fill=1,stroke=0)
    if pct>0: c.setFillColor(cor); c.roundRect(x,y,w*min(pct,1.0),hh,2*mm,fill=1,stroke=0)

def rodape_d(c,n):
    c.setFillColor(colors.HexColor("#0A0F0A")); c.rect(0,0,W,10*mm,fill=1,stroke=0)
    nline(c,0,10*mm,W,0.5)
    c.setFillColor(CT); c.setFont(FN,7.5)
    c.drawString(18*mm,3.5*mm,"Luis Kummer Personal Trainer  .  Diagnóstico Exclusivo")
    c.setFillColor(VN); c.setFont(FB,8.5); c.drawRightString(W-18*mm,3.5*mm,f"{n} / {TOTAL_PAGES}")

def rodape_l(c,n):
    c.setFillColor(VM); c.rect(0,0,W,10*mm,fill=1,stroke=0)
    c.setFillColor(BR); c.setFont(FN,7.5)
    c.drawString(18*mm,3.5*mm,"Luis Kummer Personal Trainer  .  Diagnóstico Exclusivo")
    c.setFillColor(BR); c.setFont(FB,8.5); c.drawRightString(W-18*mm,3.5*mm,f"{n} / {TOTAL_PAGES}")

def header_l(c,sec,titulo,subtit):
    c.setFillColor(LF); c.rect(0,H-32*mm,W,32*mm,fill=1,stroke=0)
    vline(c,0,H-32*mm,W,2)
    c.setFillColor(VT); c.roundRect(18*mm,H-12*mm,18*mm,9*mm,3*mm,fill=1,stroke=0)
    c.setFillColor(VM); c.setFont(FB,7.5); c.drawCentredString(27*mm,H-8.2*mm,f"SEÇÃO {sec}")
    c.setFillColor(TD); c.setFont(FB,22); c.drawString(18*mm,H-24*mm,titulo)
    c.setFillColor(TM); c.setFont(FN,10); c.drawString(18*mm,H-30*mm,subtit)

def btn_desbloquear(c,y):
    # Garante que o botão não sobreponha o rodapé (10mm) + margem (5mm)
    y_min=18*mm
    if y-15*mm < y_min: y=y_min+15*mm
    bw=W-36*mm; bh=15*mm
    c.setFillColor(VM); c.roundRect(18*mm,y-bh,bw,bh,4*mm,fill=1,stroke=0)
    c.setStrokeColor(VN2); c.setLineWidth(1.5); c.roundRect(18*mm,y-bh,bw,bh,4*mm,fill=0,stroke=1)
    draw_em(c,"cadeado",22*mm,y-1.5*mm,size=5)
    c.setFillColor(BR); c.setFont(FB,12)
    c.drawCentredString(W/2+3*mm,y-bh/2-12*0.35,"Desbloquear minha consultoria")
    c.linkAbsolute("",  "oferta", (18*mm, y-bh, 18*mm+bw, y))

# ── PÁG 1: CAPA (DARK) ────────────────────────────────────────────────────────
def pag_capa(c,d):
    bg_dark(c)
    nome=d.get("nome") or "Aluno"; mt=meta(d)
    c.setFillColor(VN); c.rect(0,H-3*mm,W,3*mm,fill=1,stroke=0)
    logo=os.path.join(BASE_DIR,"logo_sem_fundo.png")
    if os.path.exists(logo):
        c.drawImage(logo,18*mm,H-26*mm,width=20*mm,height=20*mm,preserveAspectRatio=True,mask='auto')
    c.setFillColor(BR); c.setFont(FB,12); c.drawString(42*mm,H-14*mm,"LUIS KUMMER")
    c.setFillColor(VN); c.setFont(FB,8.5); c.drawString(42*mm,H-22*mm,"PERSONAL TRAINER")
    c.setFillColor(CS); c.setFont(FN,8); c.drawRightString(W-18*mm,H-17*mm,data_hoje())
    # tag — dentro do box
    tw=84*mm; th=10*mm; tx=W/2-tw/2; ty=H-37*mm
    card_d(c,tx,ty-th,tw,th,fill=VD,r=4,borda=VN)
    draw_em(c,"alvo",tx+4*mm,ty-1*mm,size=5)
    c.setFillColor(VN); c.setFont(FB,8.5)
    c.drawString(tx+13*mm,ty-th/2-8.5*0.35,"Diagnóstico Inicial Personalizado")
    # nome
    c.setFillColor(CS); c.setFont(FB,10); c.drawCentredString(W/2,H-54*mm,"CRIADO EXCLUSIVAMENTE PARA")
    # Fonte adaptativa: reduz conforme o comprimento do nome
    nome_max_w = W - 36*mm
    nome_size = 60
    for sz in [60, 50, 42, 34, 26]:
        c.setFont(FB, sz)
        if c.stringWidth(nome, FB, sz) <= nome_max_w:
            nome_size = sz
            break
    c.setFillColor(BR); c.setFont(FB, nome_size); c.drawCentredString(W/2, H-78*mm, nome)
    nline(c,W/2-35*mm,H-82*mm,70*mm,2.5)
    if mt.get("tipo")=="emagrec": mtxt=f"Meta: Perder {mt['diff']} kg"
    elif mt.get("tipo")=="massa": mtxt="Meta: Ganhar massa muscular"
    elif mt.get("tipo")=="parto": mtxt="Meta: Recuperação pós-parto"
    else: mtxt=f"Meta: {obj_txt(d.get('objetivo',''))}"
    c.setFillColor(VN); c.setFont(FB,15); c.drawCentredString(W/2,H-90*mm,mtxt)
    c.setFillColor(CT); c.setFont(FN,9.5)
    c.drawCentredString(W/2,H-97*mm,f"Baseado nas suas respostas . {data_hoje()}")
    # card 3 números
    cy=H-107*mm; ch=50*mm
    card_d(c,18*mm,cy-ch,W-36*mm,ch,fill=PC,r=4,borda=PB)
    nline(c,18*mm,cy,W-36*mm,2.5)
    if mt.get("tipo")=="emagrec":
        cols=[(str(int(mt["pa"])),"kg","HOJE"),(str(int(mt["po"])),"kg","META"),(f"{mt['meses']}","meses","ESTIMATIVA")]
    elif mt.get("tipo")=="massa":
        cols=[(f"+{mt['g3n']}-{mt['g3x']}","kg","3 MESES"),(f"+{mt['g6n']}-{mt['g6x']}","kg","6 MESES"),(safe(d.get("compro")),"/10","COMPRO.")]
    else:
        iv=d.get("imc") or calc_imc(d.get("peso"),d.get("altura"))
        cols=[(str(iv or "–"),"","IMC"),(safe(d.get("peso")),"kg","PESO"),(safe(d.get("compro")),"/10","COMPRO.")]
    cw3=(W-36*mm)/3
    for i,(num,unid,lbl) in enumerate(cols):
        cx3=18*mm+i*cw3+cw3/2
        if i>0:
            c.setStrokeColor(PB); c.setLineWidth(0.5)
            c.line(18*mm+i*cw3,cy-10*mm,18*mm+i*cw3,cy-ch+10*mm)
        c.setFillColor(VN); c.setFont(FB,44); c.drawCentredString(cx3,cy-26*mm,str(num))
        c.setFillColor(CT); c.setFont(FN,9); c.drawCentredString(cx3,cy-34*mm,unid)
        c.setFillColor(CS); c.setFont(FB,7.5); c.drawCentredString(cx3,cy-42*mm,lbl)
    # seções
    y_s=cy-ch-8*mm
    c.setFillColor(CS); c.setFont(FB,8); c.drawString(18*mm,y_s,"ESTE DOCUMENTO CONTÉM:")
    items=[("alvo","Análise biométrica completa — IMC e composição corporal"),
           ("bike","Análise detalhada de cardio vs. recomendações da OMS"),
           ("brilho","Dicas práticas personalizadas para a sua rotina"),
           ("cadeado","Planos com preços e link direto de acesso")]
    for i,(em,txt) in enumerate(items):
        ys=y_s-9*mm-i*9*mm
        draw_em(c,em,18*mm,ys+1*mm,size=4.5)
        c.setFillColor(BR); c.setFont(FN,9.5); c.drawString(28*mm,ys-1*mm,txt)

    # prova social — preenche espaço vazio
    y_ps=y_s-9*mm-4*9*mm-10*mm
    # linha divisória
    c.setStrokeColor(CS); c.setLineWidth(0.4)
    c.line(18*mm,y_ps,W-18*mm,y_ps)
    y_ps-=8*mm
    # números de impacto — 3 colunas
    cw_ps=(W-36*mm)/3
    stats=[("1000+","alunas\ntransformadas"),("20+","países\natendidos"),("4.9","avaliação\nmedia")]
    for i,(num,lbl) in enumerate(stats):
        cx_ps=18*mm+i*cw_ps+cw_ps/2
        if i>0:
            c.setStrokeColor(CS); c.setLineWidth(0.3)
            c.line(18*mm+i*cw_ps,y_ps+2*mm,18*mm+i*cw_ps,y_ps-16*mm)
        c.setFillColor(VN); c.setFont(FB,22); c.drawCentredString(cx_ps,y_ps-6*mm,num)
        c.setFillColor(CT); c.setFont(FN,8)
        for j,linha in enumerate(lbl.split('\n')):
            c.drawCentredString(cx_ps,y_ps-13*mm-j*8,linha)
    y_ps-=26*mm

    # frase de impacto final
    card_d(c,18*mm,y_ps-22*mm,W-36*mm,23*mm,fill=VD,r=4,borda=VN)
    draw_em(c,"trofeu",24*mm,y_ps-4*mm,size=5.5)
    c.setFillColor(BR); c.setFont(FB,11)
    c.drawString(34*mm,y_ps-9*mm,"Seu protocolo personalizado começa com este diagnóstico.")
    c.setFillColor(CT); c.setFont(FN,9)
    c.drawString(34*mm,y_ps-16*mm,"Cada resposta foi usada para montar a análise das próximas páginas.")

    c.setFillColor(CS); c.setFont(FN,7.5)
    c.drawCentredString(W/2,18*mm,"Documento confidencial . Luis Kummer Personal Trainer")
    rodape_d(c,1); c.showPage()

# ── PÁG 2: BIOMÉTRICO (LIGHT) ─────────────────────────────────────────────────
def pag_bio(c,d):
    bg_light(c)
    header_l(c,"1","Seu Diagnóstico","Análise completa dos seus dados biométricos")
    iv=d.get("imc") or calc_imc(d.get("peso"),d.get("altura"))
    ivf=f2(iv); CIMC=cor_imc(ivf); mt=meta(d); y=H-38*mm
    # 4 cards
    campos=[("balanca",safe(d.get("peso")),"kg","PESO ATUAL"),
            ("regua",safe(d.get("altura")),"cm","ALTURA"),
            ("bolo",safe(d.get("idade")),"anos","IDADE"),
            ("alvo",safe(d.get("peso_obj")),"kg","OBJ. PESO")]
    cw=(W-40*mm)/4
    for i,(em,val,unid,lbl) in enumerate(campos):
        cx=18*mm+i*(cw+1.3*mm); ch=30*mm
        card_l(c,cx,y-ch,cw,ch,fill=LC,r=3)
        c.setFillColor(VM); c.rect(cx,y-3.5*mm,cw,3.5*mm,fill=1,stroke=0)
        draw_em(c,em,cx+cw/2-3.5*mm,y-5*mm,size=5.5)
        c.setFillColor(TD); c.setFont(FB,17); c.drawCentredString(cx+cw/2,y-18*mm,val)
        c.setFillColor(TM); c.setFont(FN,8); c.drawCentredString(cx+cw/2,y-23*mm,unid)
        c.setFillColor(TS); c.setFont(FB,7); c.drawCentredString(cx+cw/2,y-28*mm,lbl)
    # IMC card
    y_imc=y-36*mm
    card_l(c,18*mm,y_imc-57*mm,W-36*mm,58*mm,fill=LC,r=4)
    c.setFillColor(TD); c.setFont(FB,12)
    c.drawString(24*mm,y_imc-8*mm,"ÍNDICE DE MASSA CORPORAL (IMC)")
    segs=[(4.5,AZ,"BAIXO"),(6.5,VCL,"NORMAL"),(5.0,AM,"SOBREPESO"),(5.0,LA,"OBESO I"),(4.0,VE,"OB.II")]
    tots=sum(s[0] for s in segs)
    bw=W-52*mm; bh=9*mm; yb=y_imc-20*mm; xp=24*mm
    for vs,cs2,ls in segs:
        sw=bw*vs/tots
        c.setFillColor(cs2); c.rect(xp,yb,sw,bh,fill=1,stroke=0)
        if sw>11*mm:
            c.setFillColor(BR); c.setFont(FB,6.5); c.drawCentredString(xp+sw/2,yb+2.5*mm,ls)
        xp+=sw
    c.setStrokeColor(LB); c.setLineWidth(0.5); c.roundRect(24*mm,yb,bw,bh,2*mm,fill=0,stroke=1)
    # marcador ABAIXO da barra
    if ivf:
        ratio=(min(max(ivf,15.0),42.0)-15.0)/27.0
        mx=24*mm+bw*ratio
        path=c.beginPath()
        path.moveTo(mx,yb-1*mm); path.lineTo(mx-3*mm,yb-6*mm); path.lineTo(mx+3*mm,yb-6*mm); path.close()
        c.setFillColor(CIMC); c.drawPath(path,fill=1,stroke=0)
        c.setFillColor(CIMC); c.setFont(FB,8.5); c.drawCentredString(mx,yb-10*mm,f"Você: {ivf}")
    c.setFillColor(CIMC); c.setFont(FB,14); c.drawString(24*mm,y_imc-38*mm,class_imc(iv))
    c.setFillColor(TM); c.setFont(FN,9)
    imc_str=str(ivf) if ivf else "N/A"
    c.drawString(86*mm,y_imc-38*mm,f"Ideal: 18,5-24,9  .  Seu IMC: {imc_str}")
    # faixas referência — dentro do card, fonte reduzida
    refs=[(AZ,"< 18,5","Baixo"),(VCL,"18,5-24,9","Normal"),(AM,"25-29,9","Sobr."),(LA,">= 30","Obeso")]
    rw=(W-40*mm)/4; yr=y_imc-46*mm
    for i,(cr,fx,lb) in enumerate(refs):
        rx=18*mm+i*(rw+1.5*mm)
        c.setFillColor(cr); c.roundRect(rx,yr-7*mm,rw,8*mm,2*mm,fill=1,stroke=0)
        c.setFillColor(BR); c.setFont(FB,6.5)
        c.drawCentredString(rx+rw/2,yr-3.5*mm,f"{lb}: {fx}")
    # card meta
    ym=y_imc-63*mm; mh=48*mm
    c.setFillColor(VT); c.roundRect(18*mm,ym-mh,W-36*mm,mh,4*mm,fill=1,stroke=0)
    c.setStrokeColor(VM); c.setLineWidth(1.2); c.roundRect(18*mm,ym-mh,W-36*mm,mh,4*mm,fill=0,stroke=1)
    vline(c,18*mm,ym,W-36*mm,2.5)
    tp=mt.get("tipo","")
    c.setFillColor(TD); c.setFont(FB,11)
    if tp=="emagrec":
        c.drawCentredString(W/2,ym-10*mm,"SUA META DE EMAGRECIMENTO")
        c2=[(str(int(mt["pa"])),"kg","HOJE"),(str(int(mt["po"])),"kg","META"),(f"{mt['meses']}","meses","ESTIMATIVA")]
    elif tp=="massa":
        c.drawCentredString(W/2,ym-10*mm,"SUA META DE GANHO MUSCULAR")
        c2=[(f"+{mt['g3n']}-{mt['g3x']}","kg","3 MESES"),(f"+{mt['g6n']}-{mt['g6x']}","kg","6 MESES"),(safe(d.get("compro")),"/10","COMPRO.")]
    else:
        c.drawCentredString(W/2,ym-10*mm,"SUAS METAS EM 60 DIAS")
        c2=[(safe(d.get("peso")),"kg","PESO"),(safe(d.get("compro")),"/10","COMPRO."),(safe(d.get("estresse")),"/10","ESTRESSE")]
    cw3=(W-36*mm)/3
    for i,(num,unid,lbl) in enumerate(c2):
        cx3=18*mm+i*cw3+cw3/2
        if i>0:
            c.setStrokeColor(LB); c.setLineWidth(0.5)
            c.line(18*mm+i*cw3,ym-14*mm,18*mm+i*cw3,ym-mh+8*mm)
        # número grande
        c.setFillColor(VM); c.setFont(FB,32); c.drawCentredString(cx3,ym-32*mm,str(num))
        # unidade
        c.setFillColor(TM); c.setFont(FN,9); c.drawCentredString(cx3,ym-39*mm,unid)
        # label
        c.setFillColor(TS); c.setFont(FB,7.5); c.drawCentredString(cx3,ym-mh+6*mm,lbl)

    # card gordura corporal estimada — preenche espaço
    yg=ym-mh-6*mm
    # estimar gordura corporal via fórmula Deurenberg (simplificada)
    ivf2=f2(iv); idade2=f2(d.get("idade")); sexo2=str(d.get("sexo") or "").lower()
    gord_est=None
    if ivf2 and idade2:
        # Homem: (1.20 * IMC) + (0.23 * idade) - 16.2
        # Mulher: (1.20 * IMC) + (0.23 * idade) - 5.4
        k = 5.4 if "f" in sexo2[:2] else 16.2
        gord_est = round((1.20*ivf2)+(0.23*idade2)-k, 1)
        gord_est = max(5.0, min(gord_est, 60.0))  # limitar entre 5 e 60
    if gord_est:
        # classificação
        if "f" in sexo2[:2]:
            if gord_est<21: gc="Atlética"; gcc=VM
            elif gord_est<33: gc="Saudável"; gcc=VM
            elif gord_est<39: gc="Excesso"; gcc=AM
            else: gc="Obesidade"; gcc=LA
        else:
            if gord_est<14: gc="Atlético"; gcc=VM
            elif gord_est<25: gc="Saudável"; gcc=VM
            elif gord_est<31: gc="Excesso"; gcc=AM
            else: gc="Obesidade"; gcc=LA
        card_l(c,18*mm,yg-20*mm,W-36*mm,21*mm,fill=LC,r=3)
        c.setFillColor(VM); c.rect(18*mm,yg-20*mm,4*mm,21*mm,fill=1,stroke=0)
        draw_em(c,"barras",25*mm,yg-3*mm,size=5.5)
        c.setFillColor(TD); c.setFont(FB,10); c.drawString(34*mm,yg-7*mm,"GORDURA CORPORAL ESTIMADA:")
        c.setFillColor(gcc); c.setFont(FB,16); c.drawString(34*mm,yg-16*mm,f"{gord_est}%")
        c.setFillColor(gcc); c.setFont(FB,10); c.drawString(70*mm,yg-16*mm,f"  {gc}")
        c.setFillColor(TS); c.setFont(FN,7.5); c.drawRightString(W-22*mm,yg-16*mm,"Estimativa via formula Deurenberg")

    rodape_l(c,2); c.showPage()

# ── PÁG 3: HÁBITOS (LIGHT) — SEM cards estresse/compro ───────────────────────
def pag_hab(c,d):
    bg_light(c)
    header_l(c,"2","Hábitos e Rotina","Sua rotina atual de exercícios, alimentação e estilo de vida")
    itens=[
        ("alvo","Objetivo",obj_txt(d.get("objetivo",""))),
        ("halteres","Musculação",ex_txt(d.get("exercicio",""))),
        ("relogio","Duração do treino",tt_txt(d.get("tempo_treino",""))),
        ("bike","Cardio — frequência",fc_txt(d.get("freq_cardio",""))),
        ("bike","Cardio — tipo e duração",f"{cardio_txt(d.get('cardio',''))}  ·  {tc_txt(d.get('tempo_cardio',''))}"),
        ("salada","Alimentação",al_txt(d.get("alimentacao",""))),
        ("aviso","Principais obstáculos",ob_txt(d.get("obstaculo",""))),
        ("aviso","Limitações físicas",safe(d.get("limitacao"))),
        ("remedio","Medicamentos",safe(d.get("medicamento") or d.get("medicamentos"))),
    ]
    itens=[(e,l,v) for e,l,v in itens if v and v not in ["–","Não informado"]]
    y=H-38*mm
    for em,lbl,val in itens:
        n=max(1,len(str(val))//55+1); hh=(12+n*5)*mm
        card_l(c,18*mm,y-hh,W-36*mm,hh,fill=LC,r=3)
        c.setFillColor(VM); c.rect(18*mm,y-hh,4*mm,hh,fill=1,stroke=0)
        draw_em(c,em,25*mm,y-2.5*mm,size=5.5)
        c.setFillColor(VM); c.setFont(FB,9); c.drawString(34*mm,y-7*mm,lbl.upper())
        wrap(c,str(val),34*mm,y-11.5*mm,W-56*mm,size=10,cor=TD,leading=13)
        y-=hh+3*mm
    rodape_l(c,3); c.showPage()

# ── PÁG 4: PERFIL (LIGHT) ─────────────────────────────────────────────────────
def pag_perfil(c,d):
    bg_light(c)
    header_l(c,"3","Leitura do Perfil","Como este diagnóstico interpreta suas respostas")
    co=f2(d.get("compro")) or 0; es=f2(d.get("estresse")) or 5
    iv=d.get("imc") or calc_imc(d.get("peso"),d.get("altura")); CIMC=cor_imc(f2(iv))
    y=H-38*mm; cw2=(W-40*mm)/2; ch_c=40*mm
    # cards 2x2 com faixa de 8mm
    dados=[
        ("alvo","OBJETIVO",obj_txt(d.get("objetivo","")),f"Comprometimento: {int(co)}/10",VM),
        ("barras","PERFIL FÍSICO",class_imc(iv),f"IMC: {iv or '–'}",CIMC),
        ("halteres","ATIVIDADE FÍSICA",f"Musculação: {ex_txt(d.get('exercicio',''))}",f"Cardio: {fc_txt(d.get('freq_cardio',''))}",VM),
        ("salada","ALIMENTAÇÃO",al_txt(d.get("alimentacao","")),f"Estresse: {int(es)}/10",LA),
    ]
    for i,(em,tit,val,det,cor) in enumerate(dados):
        col=i%2; row=i//2
        cx=18*mm+col*(cw2+4*mm); cy=y-row*(ch_c+4*mm)
        card_l(c,cx,cy-ch_c,cw2,ch_c,fill=LC,r=3)
        # faixa de 8mm
        c.setFillColor(cor); c.roundRect(cx,cy-8*mm,cw2,8*mm,2*mm,fill=1,stroke=0)
        draw_em(c,em,cx+3*mm,cy-1.5*mm,size=5.5)
        c.setFillColor(BR); c.setFont(FB,9); c.drawString(cx+13*mm,cy-6*mm,tit)
        wrap(c,str(val)[:40],cx+4*mm,cy-16*mm,cw2-8*mm,size=11,cor=TD,leading=14)
        c.setFillColor(TM); c.setFont(FN,9); c.drawString(cx+4*mm,cy-31*mm,str(det))
    # barra comprometimento — texto ABAIXO da barra
    yc=y-2*(ch_c+4*mm)-6*mm
    card_l(c,18*mm,yc-24*mm,W-36*mm,25*mm,fill=LC,r=3)
    draw_em(c,"musculo",22*mm,yc-2.5*mm,size=5.5)
    c.setFillColor(TD); c.setFont(FB,11); c.drawString(31*mm,yc-8*mm,"Nível de comprometimento declarado:")
    # barra primeiro
    barra(c,31*mm,yc-16*mm,W-65*mm,5,co/10,VM if co>=7 else AM)
    # texto abaixo da barra
    lbl_c="Excepcional!" if co>=8 else ("Ótimo!" if co>=6 else "Vamos juntos!")
    c.setFillColor(VM if co>=6 else AM); c.setFont(FB,10)
    c.drawRightString(W-22*mm,yc-22*mm,f"{int(co)}/10  .  {lbl_c}")
    # alertas
    yo=yc-30*mm
    li=str(d.get("limitacao") or ""); me=str(d.get("medicamento") or d.get("medicamentos") or "")
    for lbl_o,vo,co2 in [
        ("Limitação física registrada",li,LA) if li and li.lower() not in ["nao","nenhuma","","–"] else (None,None,None),
        ("Medicamento em uso",me,AZ) if me and me.lower() not in ["nao","nenhum","","–"] else (None,None,None),
    ]:
        if not lbl_o: continue
        hh=16*mm; card_l(c,18*mm,yo-hh,W-36*mm,hh,fill=LC,r=3)
        c.setFillColor(co2); c.setFont(FB,9); c.drawString(24*mm,yo-7*mm,lbl_o+":")
        wrap(c,str(vo),24*mm,yo-11*mm,W-52*mm,size=9.5,cor=TD,leading=12); yo-=hh+3*mm
    yn=yo-4*mm
    card_l(c,18*mm,yn-13*mm,W-36*mm,14*mm,fill=VT,r=3,borda=LB)
    draw_em(c,"medico",22*mm,yn-2.5*mm,size=5)
    wrap(c,"Este diagnóstico não substitui consulta médica. Ele organiza os sinais do seu perfil para você entender por onde começar.",
         31*mm,yn-3*mm,W-52*mm,size=9,cor=TM,leading=11)
    btn_desbloquear(c,yn-20*mm)
    rodape_l(c,4); c.showPage()

# ── PÁG 5: DICAS (LIGHT) ──────────────────────────────────────────────────────
def pag_dicas(c,d):
    bg_light(c)
    header_l(c,"4","Suas Recomendações","Dicas práticas baseadas exatamente nas suas respostas")
    nome=d.get("nome") or "você"; dc=dicas(d); y=H-38*mm
    card_l(c,18*mm,y-20*mm,W-36*mm,21*mm,fill=VT,r=3,borda=LB)
    c.setFillColor(VM); c.rect(18*mm,y-20*mm,4*mm,21*mm,fill=1,stroke=0)
    draw_em(c,"brilho",26*mm,y-3*mm,size=5.5)
    wrap(c,f"{nome}, estas recomendações foram geradas com base nas suas respostas. Não são genéricas - falam diretamente sobre a sua situação.",
         35*mm,y-5*mm,W-58*mm,size=10.5,cor=VM,leading=13)
    y-=25*mm
    if not dc:
        card_l(c,18*mm,y-22*mm,W-36*mm,23*mm,fill=LC,r=3)
        draw_em(c,"ok",24*mm,y-3*mm,size=6)
        c.setFillColor(TD); c.setFont(FB,12); c.drawString(34*mm,y-10*mm,"Seu perfil está bem equilibrado!")
        y-=28*mm
    else:
        for em,cor,titulo,desc in dc:
            n=max(2,len(desc)//58+1); hh=(15+n*5)*mm
            card_l(c,18*mm,y-hh,W-36*mm,hh,fill=LC,r=3,borda=LB)
            c.setFillColor(cor); c.roundRect(18*mm,y-hh,4*mm,hh,1.5*mm,fill=1,stroke=0)
            draw_em(c,em,26*mm,y-3*mm,size=5.5)
            c.setFillColor(cor); c.setFont(FB,10.5); c.drawString(35*mm,y-8*mm,titulo)
            wrap(c,desc,35*mm,y-13*mm,W-58*mm,size=9.5,cor=TD,leading=12); y-=hh+3.5*mm
    btn_desbloquear(c,y-5*mm)
    rodape_l(c,5); c.showPage()

# ── PÁG 6: LAUDO CARDIO + OMS (LIGHT) ────────────────────────────────────────
def pag_oms(c,d):
    bg_light(c)
    header_l(c,"5","Laudo de Atividade Física","Análise detalhada do seu cardio vs. recomendações da OMS")
    oms=oms_detalhado(d); tot=oms["total"]; st=oms["status"]
    cst={"insuf":VE,"parcial":LA,"ok":VM,"exce":VM}.get(st,VM)
    lbl_st={"insuf":"Nível Insuficiente","parcial":"Quase lá!","ok":"Dentro da Meta OMS","exce":"Acima da Meta OMS"}.get(st,"")
    em_st={"insuf":"aviso","parcial":"fogo","ok":"ok","exce":"trofeu"}.get(st,"ok")
    bgst={"insuf":colors.HexColor("#FFF3F3"),"parcial":colors.HexColor("#FFF8E1"),"ok":VT,"exce":VT}.get(st,VT)
    y=H-38*mm

    # ── BREAKDOWN CARDIO + MUSCULAÇÃO ─────────────────────────────────────────
    # Título da seção de breakdown
    c.setFillColor(TD); c.setFont(FB,11); c.drawString(18*mm,y,"DETALHAMENTO DA SUA ATIVIDADE:")
    y-=7*mm

    # 3 cards breakdown lado a lado
    bw3=(W-42*mm)/3; bh3=32*mm
    breakdown=[
        ("halteres","MUSCULAÇÃO",f"{oms['min_musc']} min/sem",
         f"{oms['freq_musc']}x/sem · {tt_txt(d.get('tempo_treino',''))}",VM),
        ("bike","CARDIO",f"{oms['min_card']} min/sem",
         f"{oms['freq_card']}x/sem · {oms['tempo_cardio']}",AZUL_B),
        ("trofeu","TOTAL EQUIVALENTE",f"{oms['total']} min/sem",
         f"{'Intensidade vigorosa (2x)' if oms['intens']=='vigorosa' else 'Intensidade moderada'}",cst),
    ]
    for i,(em,tit,val,det,cor) in enumerate(breakdown):
        bx=18*mm+i*(bw3+3*mm)
        card_l(c,bx,y-bh3,bw3,bh3,fill=LC if i<2 else colors.HexColor("#F9FBE7") if st in ["ok","exce"] else colors.HexColor("#FFF3F3"),r=3,borda=cor)
        c.setFillColor(cor); c.roundRect(bx,y-8*mm,bw3,8*mm,2*mm,fill=1,stroke=0)
        draw_em(c,em,bx+3*mm,y-1*mm,size=5.5)
        c.setFillColor(BR); c.setFont(FB,8); c.drawString(bx+12*mm,y-6*mm,tit)
        c.setFillColor(cor); c.setFont(FB,18); c.drawCentredString(bx+bw3/2,y-20*mm,val)
        wrap(c,det,bx+4*mm,y-23*mm,bw3-8*mm,size=7.5,cor=TM,leading=10)
    y-=bh3+6*mm

    # card tipo de cardio
    if oms["min_card"]>0:
        card_l(c,18*mm,y-19*mm,W-36*mm,20*mm,fill=AZUL_CARD,r=3,borda=AZUL_B)
        c.setFillColor(AZUL_B); c.rect(18*mm,y-19*mm,4*mm,20*mm,fill=1,stroke=0)
        draw_em(c,"bike",26*mm,y-2*mm,size=5)
        c.setFillColor(AZUL_B); c.setFont(FB,9); c.drawString(34*mm,y-8*mm,"TIPO DE CARDIO PRATICADO:")
        c.setFillColor(TD); c.setFont(FN,9.5); c.drawString(34*mm,y-15*mm,f"{oms['tipo_cardio']}")
        y-=23*mm
    else:
        card_l(c,18*mm,y-19*mm,W-36*mm,20*mm,fill=colors.HexColor("#FFF3F3"),r=3,borda=VE)
        c.setFillColor(VE); c.rect(18*mm,y-19*mm,4*mm,20*mm,fill=1,stroke=0)
        draw_em(c,"aviso",26*mm,y-2*mm,size=5)
        c.setFillColor(VE); c.setFont(FB,9); c.drawString(34*mm,y-8*mm,"CARDIO NÃO INFORMADO")
        c.setFillColor(TD); c.setFont(FN,9.5); c.drawString(34*mm,y-15*mm,"Nenhuma atividade cardiovascular registrada.")
        y-=23*mm

    # ── STATUS GERAL OMS ──────────────────────────────────────────────────────
    y-=4*mm
    ch_st=46*mm
    card_l(c,18*mm,y-ch_st,W-36*mm,ch_st,fill=bgst,r=4,borda=cst)
    c.setStrokeColor(cst); c.setLineWidth(2.5); c.line(18*mm,y,18*mm+W-36*mm,y)
    # emoji + label no topo
    draw_em(c,em_st,22*mm,y-3*mm,size=6)
    c.setFillColor(cst); c.setFont(FB,13); c.drawString(32*mm,y-9*mm,lbl_st)
    # número grande centralizado
    c.setFillColor(cst); c.setFont(FB,44); c.drawCentredString(W/2,y-30*mm,str(tot))
    # texto abaixo do número — dentro do card
    c.setFillColor(TM); c.setFont(FN,10); c.drawCentredString(W/2,y-38*mm,"min/semana de atividade")
    c.setFillColor(TS); c.setFont(FN,8); c.drawCentredString(W/2,y-ch_st+5*mm,"OMS recomenda mínimo 150 min/semana")
    y-=ch_st+6*mm

    # barras comparativas — texto dentro do card
    card_l(c,18*mm,y-38*mm,W-36*mm,40*mm,fill=LC,r=3)
    c.setFillColor(TM); c.setFont(FN,9.5); c.drawString(24*mm,y-8*mm,"Você")
    barra(c,50*mm,y-14*mm,W-90*mm,5,min(tot/300.0,1.0),cst,LCG)
    c.setFillColor(TD); c.setFont(FB,9); c.drawString(W-34*mm,y-11.5*mm,f"{tot} min")
    c.setFillColor(TM); c.setFont(FN,9.5); c.drawString(24*mm,y-25*mm,"Meta OMS")
    barra(c,50*mm,y-31*mm,W-90*mm,5,150/300.0,VM,LCG)
    c.setFillColor(TD); c.setFont(FB,9); c.drawString(W-40*mm,y-28.5*mm,"150 min")
    y-=44*mm

    # mensagem personalizada
    msgs={"insuf":"Você está abaixo das recomendações. Seu protocolo vai aumentar gradualmente o volume de treino e incluir orientações de cardio de forma segura.",
          "parcial":"Você está quase lá! Com pequenos ajustes no cardio você chega facilmente aos 150 min/semana com o protocolo certo.",
          "ok":"Parabéns! Você já está dentro da meta OMS. Seu protocolo vai potencializar ainda mais seus resultados.",
          "exce":"Excelente! Você supera as recomendações. Seu protocolo vai garantir recuperação adequada e maximizar resultados."}
    card_l(c,18*mm,y-20*mm,W-36*mm,22*mm,fill=VT,r=3,borda=LB)
    c.setFillColor(VM); c.rect(18*mm,y-20*mm,4*mm,22*mm,fill=1,stroke=0)
    draw_em(c,"brilho",26*mm,y-3.5*mm,size=5.5)
    wrap(c,msgs.get(st,""),35*mm,y-5*mm,W-58*mm,size=10,cor=TD,leading=13)
    y-=26*mm

    # cards estresse e comprometimento — com faixa 8mm
    es=f2(d.get("estresse")) or 0; co=f2(d.get("compro")) or 0
    cw2=(W-40*mm)/2
    me2={(1,3):("Estresse Baixo","Favorece recuperação e consistência nos treinos."),
         (4,6):("Estresse Moderado","Atenção. Seu protocolo vai incluir orientações de recuperação."),
         (7,8):("Estresse Elevado","Impacta resultados. Progressão adaptada para esse cenário."),
         (9,10):("Estresse Crítico","Protocolo mais gradual para não sobrecarregar.")}
    mc2={(1,4):("Comprometimento Inicial","Seu protocolo vai te ajudar a criar consistência."),
         (5,7):("Bom Comprometimento","No caminho certo! Os resultados vão aparecer."),
         (8,10):("Alto Comprometimento","Excepcional! Você tem tudo para transformar seu corpo.")}
    def gm(v,mp):
        for (l,h),(t,ds) in mp.items():
            if l<=int(v)<=h: return t,ds
        return "–","–"
    te,de=gm(es,me2); tc,dc2=gm(co,mc2)
    for i,(val,tit,desc,corb) in enumerate([(es,te,de,LA),(co,tc,dc2,VM)]):
        cx=18*mm+i*(cw2+4*mm); ch2=44*mm
        card_l(c,cx,y-ch2,cw2,ch2,fill=LC,r=3,borda=LB)
        # faixa 8mm
        c.setFillColor(corb); c.roundRect(cx,y-8*mm,cw2,8*mm,2*mm,fill=1,stroke=0)
        c.setFillColor(BR); c.setFont(FB,9.5); c.drawCentredString(cx+cw2/2,y-5.5*mm,tit)
        c.setFillColor(corb); c.setFont(FB,26); c.drawString(cx+4*mm,y-24*mm,f"{int(val)}/10")
        barra(c,cx+4*mm,y-31*mm,cw2-8*mm,4,val/10,corb)
        wrap(c,desc,cx+4*mm,y-37*mm,cw2-8*mm,size=8.5,cor=TM,leading=11)

    rodape_l(c,6); c.showPage()

# ── PÁG 7: APP (LIGHT) ────────────────────────────────────────────────────────
def pag_app(c,d):
    bg_light(c)
    header_l(c,"6","Seu App de Treinos","Tudo que você vai ter acesso no protocolo personalizado")
    nome=d.get("nome") or "você"; y=H-38*mm
    c.setFillColor(TD); c.setFont(FB,14); c.drawCentredString(W/2,y,f"{nome}, tudo na palma da mão:")
    y-=9*mm
    app1=os.path.join(BASE_DIR,"app_print1.png"); app2=os.path.join(BASE_DIR,"app_print2.png")
    if os.path.exists(app1) or os.path.exists(app2):
        aw=38*mm; ah=65*mm; gap=6*mm
        ax1=W/2-(aw*2+gap)/2; ax2=ax1+aw+gap; ay=y
        if os.path.exists(app1): c.drawImage(app1,ax1,ay-ah,width=aw,height=ah,preserveAspectRatio=True,mask="auto")
        if os.path.exists(app2): c.drawImage(app2,ax2,ay-ah,width=aw,height=ah,preserveAspectRatio=True,mask="auto")
        c.setFillColor(TS); c.setFont(FN,8); c.drawCentredString(W/2,ay-ah-4*mm,"Interface real do app MFIT Personal")
        y=ay-ah-9*mm
    else: y-=4*mm
    difs=[("halteres","Protocolo personalizado","Treinos montados do zero pelo Luis, exclusivamente para o seu perfil e objetivo."),
          ("camera","Vídeos de todos os exercícios","Cada exercício com vídeo demonstrativo do próprio Luis para garantir execução correta."),
          ("chat","Suporte direto com o Luis","Atendimento personalizado via app e WhatsApp durante todo o protocolo."),
          ("meditacao","Mobilidade e alongamento","Protocolos complementares inclusos para melhorar recuperação e flexibilidade."),
          ("bike","Orientações de cardio","Guia personalizado baseado no seu objetivo, limitações e tempo disponível."),
          ("grafico","Acompanhamento de evolução","Registre cargas e acompanhe seu progresso semana a semana pelo app."),]
    dw=(W-40*mm)/2; dh=24*mm
    for i,(em,tit,desc) in enumerate(difs):
        col=i%2; row=i//2
        dx=18*mm+col*(dw+4*mm); dy=y-row*(dh+3*mm)
        card_l(c,dx,dy-dh,dw,dh,fill=LC,r=3,borda=LB)
        c.setFillColor(VM); c.rect(dx,dy-dh,4*mm,dh,fill=1,stroke=0)
        draw_em(c,em,dx+8*mm,dy-4*mm,size=5.5)
        c.setFillColor(VM); c.setFont(FB,10); c.drawString(dx+17*mm,dy-9*mm,tit)
        wrap(c,desc,dx+8*mm,dy-14*mm,dw-12*mm,size=8.5,cor=TM,leading=10)

    # prints do app no final
    y_app=y-3*(dh+3*mm)-6*mm
    app1=os.path.join(BASE_DIR,"app_print1.png"); app2=os.path.join(BASE_DIR,"app_print2.png")
    if os.path.exists(app1) or os.path.exists(app2):
        aw=42*mm; ah=70*mm; gap=8*mm
        tot_w=aw*2+gap; ax1=W/2-tot_w/2; ax2=ax1+aw+gap
        if os.path.exists(app1):
            c.drawImage(app1,ax1,y_app-ah,width=aw,height=ah,preserveAspectRatio=True,mask="auto")
        if os.path.exists(app2):
            c.drawImage(app2,ax2,y_app-ah,width=aw,height=ah,preserveAspectRatio=True,mask="auto")
        c.setFillColor(TS); c.setFont(FN,8)
        c.drawCentredString(W/2,y_app-ah-4*mm,"Interface real do app MFIT Personal")
    else:
        # fallback: card CTA se não tiver prints
        card_l(c,18*mm,y_app-22*mm,W-36*mm,23*mm,fill=VT,r=4,borda=LB)
        c.setStrokeColor(VM); c.setLineWidth(1.5); c.roundRect(18*mm,y_app-22*mm,W-36*mm,23*mm,4*mm,fill=0,stroke=1)
        draw_em(c,"foguete",22*mm,y_app-3*mm,size=5.5)
        c.setFillColor(VM); c.setFont(FB,11)
        c.drawString(32*mm,y_app-9*mm,"Pronto para começar sua transformação?")
        c.setFillColor(TM); c.setFont(FN,9.5)
        c.drawString(32*mm,y_app-16*mm,"Veja os planos disponíveis na próxima página.")

    rodape_l(c,7); c.showPage()

# ── PÁG 8: OFERTA (DARK) ──────────────────────────────────────────────────────
def pag_oferta(c,d):
    bg_dark(c)
    # bookmark para links internos funcionarem
    c.bookmarkPage("oferta")
    nome=d.get("nome") or "você"; mt=meta(d)
    c.setFillColor(VN); c.rect(0,H-3*mm,W,3*mm,fill=1,stroke=0)
    c.setFillColor(CS); c.setFont(FB,8.5); c.drawString(18*mm,H-14*mm,"+ PRÓXIMO PASSO")
    if mt.get("tipo")=="emagrec": l2=f"chegar aos {int(mt['po'])} kg."
    elif mt.get("tipo")=="parto": l2="cuidado especial."
    else: l2="transformar seu corpo."
    c.setFillColor(BR); c.setFont(FB,28); c.drawString(18*mm,H-30*mm,f"{nome}, você tem tudo para")
    c.setFillColor(VN); c.setFont(FB,28); c.drawString(18*mm,H-44*mm,l2)
    c.setFillColor(CT); c.setFont(FN,10.5); c.drawString(18*mm,H-53*mm,"Escolha seu acesso e comece hoje mesmo.")
    y=H-59*mm
    difs=[("calendario","Protocolo montado do zero pelo Luis"),
          ("camera","Vídeos de todos os exercícios"),
          ("chat","Suporte via app e WhatsApp"),
          ("casa","Treinos para academia e casa")]
    for em,txt in difs:
        c.setStrokeColor(PB); c.setLineWidth(0.4); c.line(18*mm,y-1*mm,W-18*mm,y-1*mm)
        draw_em(c,em,18*mm,y-0.5*mm,size=5)
        c.setFillColor(BR); c.setFont(FN,10.5); c.drawString(30*mm,y-8.5*mm,txt)
        y-=13*mm
    c.setStrokeColor(PB); c.setLineWidth(0.4); c.line(18*mm,y,W-18*mm,y); y-=7*mm
    planos=[
        ("INDIVIDUAL","1 Protocolo · 60 dias","R$ 119",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636",False),
        ("DUPLA","1 Protocolo · 60 dias","R$ 207",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112637&page=112636",False),
        ("INDIVIDUAL","3 Protocolos · 180 dias","R$ 297",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112638&page=112636",True),
        ("DUPLA","3 Protocolos · 180 dias","R$ 479",
         "https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112639&page=112636",False),
    ]
    pw=(W-40*mm)/2; ph=50*mm; gap=4*mm
    for i,(tit,desc,preco,url,pop) in enumerate(planos):
        col=i%2; row=i//2; px=18*mm+col*(pw+gap); py=y-row*(ph+gap)
        fc2=VD if pop else PC; bc=VN if pop else PB
        card_d(c,px,py-ph,pw,ph,fill=fc2,r=4,borda=bc)
        if pop:
            # badge no topo do card — bem dentro
            badge_w=34*mm; badge_y=py-6*mm
            c.setFillColor(VN); c.roundRect(px+pw/2-badge_w/2,badge_y-6*mm,badge_w,7*mm,3*mm,fill=1,stroke=0)
            draw_em(c,"estrela",px+pw/2-badge_w/2+2*mm,badge_y-0.5*mm,size=3.5)
            c.setFillColor(PF); c.setFont(FB,7.5)
            c.drawString(px+pw/2-badge_w/2+9*mm,badge_y-4.5*mm,"Mais popular")
            # título
            c.setFillColor(CT); c.setFont(FB,8.5); c.drawCentredString(px+pw/2,py-16*mm,tit)
            # preço
            c.setFillColor(BR); c.setFont(FB,26); c.drawCentredString(px+pw/2,py-30*mm,preco)
            # descrição
            c.setFillColor(CT); c.setFont(FN,9); c.drawCentredString(px+pw/2,py-37*mm,desc)
        else:
            # título
            c.setFillColor(CT); c.setFont(FB,8.5); c.drawCentredString(px+pw/2,py-10*mm,tit)
            # preço
            c.setFillColor(BR); c.setFont(FB,26); c.drawCentredString(px+pw/2,py-26*mm,preco)
            # descrição
            c.setFillColor(CT); c.setFont(FN,9); c.drawCentredString(px+pw/2,py-33*mm,desc)
        # botão
        bx=px+4*mm; bw2=pw-8*mm; bh=10*mm; by=py-ph+6*mm
        c.setFillColor(VN2); c.roundRect(bx,by,bw2,bh,3*mm,fill=1,stroke=0)
        c.setFillColor(PF); c.setFont(FB,9.5); c.drawCentredString(bx+bw2/2,by+3.5*mm,"Escolher")
        c.linkURL(url,(bx,by,bx+bw2,by+bh),relative=0)
    y_cta=y-2*(ph+gap)-7*mm; bwc=W-36*mm
    c.setFillColor(VN2); c.roundRect(18*mm,y_cta-15*mm,bwc,16*mm,4*mm,fill=1,stroke=0)
    draw_em(c,"foguete",22*mm,y_cta-1.5*mm,size=5.5)
    c.setFillColor(PF); c.setFont(FB,12.5); c.drawCentredString(W/2+3*mm,y_cta-9*mm,"Começar meu protocolo agora")
    c.linkURL("https://pages.mfitpersonal.com.br/index?acao=page&tipo=2&buyPage=112636&page=112636",
              (18*mm,y_cta-15*mm,18*mm+bwc,y_cta),relative=0)
    y_selos=y_cta-22*mm
    c.setFillColor(CS); c.setFont(FN,8)
    c.drawCentredString(W/2,y_selos,"Pagamento 100% seguro . Suporte via WhatsApp")
    # selos de garantia
    y_selos-=8*mm
    selos=[("cadeado","Pagamento\nseguro"),("chat","Suporte\nWhatsApp"),("ok","Satisfação\ngarantida"),("estrela","4.9/5\navaliacoes")]
    sw2=(W-36*mm)/4
    for i,(em,lbl) in enumerate(selos):
        sx=18*mm+i*sw2+sw2/2
        draw_em(c,em,sx-3*mm,y_selos,size=4.5)
        c.setFillColor(CS); c.setFont(FN,7)
        for j,ln in enumerate(lbl.split('\n')):
            c.drawCentredString(sx,y_selos-9*mm-j*7,ln)
    rodape_d(c,8); c.showPage()

# ── PÁG 9: DEPOIMENTOS (DARK) ─────────────────────────────────────────────────
def pag_dep(c,d):
    bg_dark(c); nome=d.get("nome") or "você"
    c.setFillColor(VN); c.rect(0,H-3*mm,W,3*mm,fill=1,stroke=0)
    c.setFillColor(AM); c.setFont(FB,20); c.drawCentredString(W/2,H-15*mm,"* * * * *")
    c.setFillColor(VN); c.setFont(FB,46); c.drawCentredString(W/2,H-34*mm,"+1000")
    c.setFillColor(CT); c.setFont(FN,10.5)
    c.drawCentredString(W/2,H-42*mm,"alunos transformados em mais de 20 países")
    y=H-50*mm

    # depoimento destaque — maior
    card_d(c,18*mm,y-38*mm,W-36*mm,39*mm,fill=PC,r=4,borda=PB)
    nline(c,18*mm,y,W-36*mm,2.5)
    c.setFillColor(VN); c.setFont(FB,30); c.drawString(22*mm,y-10*mm,'"')
    c.setFillColor(AM); c.setFont(FB,9); c.drawRightString(W-22*mm,y-6*mm,"* * * * *")
    wrap(c,"Perdi 8kg em 60 dias seguindo o protocolo. O acompanhamento pelo app fez toda a diferença! Nunca imaginei conseguir me comprometer tanto com a minha saúde. Recomendo para todas as minhas amigas.",
         28*mm,y-8*mm,W-52*mm,size=10,cor=BR,leading=13)
    c.setFillColor(VN); c.setFont(FB,10); c.drawString(28*mm,y-34*mm,"Ana Paula, 34 anos  .  Curitiba  .  Objetivo: emagrecer")
    y-=42*mm

    dw2=(W-40*mm)/2
    dep2=[("Marcos e Juliana","Fizemos o plano dupla e nos motivamos juntos. Em 3 meses transformamos completamente nossa rotina de vida!"),
          ("Cristiane, 41 anos","Com duas filhas e trabalho não sobrava tempo. O protocolo foi perfeito para a minha realidade e o resultado veio rápido.")]
    for i,(nm,txt) in enumerate(dep2):
        dx=18*mm+i*(dw2+4*mm); dh2=36*mm
        card_d(c,dx,y-dh2,dw2,dh2,fill=PC,r=3,borda=PB)
        c.setFillColor(AM); c.setFont(FN,10); c.drawString(dx+4*mm,y-7*mm,"* * * * *")
        wrap(c,f'"{txt}"',dx+4*mm,y-13*mm,dw2-8*mm,size=9,cor=BR,leading=12)
        c.setFillColor(VN); c.setFont(FB,9); c.drawString(dx+4*mm,y-32*mm,nm)
    y-=40*mm

    dep3=[("Fernanda, 28 anos","Cabe perfeitamente na rotina corrida. Em 60 dias já vi resultados reais e minha energia melhorou muito!"),
          ("Roberto, 52 anos","Protocolo totalmente adaptado para a minha hérnia. Hoje me sinto 10 anos mais jovem e sem dores!")]
    for i,(nm,txt) in enumerate(dep3):
        dx=18*mm+i*(dw2+4*mm); dh3=34*mm
        card_d(c,dx,y-dh3,dw2,dh3,fill=PC,r=3,borda=PB)
        c.setFillColor(AM); c.setFont(FN,10); c.drawString(dx+4*mm,y-7*mm,"* * * * *")
        wrap(c,f'"{txt}"',dx+4*mm,y-13*mm,dw2-8*mm,size=9,cor=BR,leading=12)
        c.setFillColor(VN); c.setFont(FB,9); c.drawString(dx+4*mm,y-30*mm,nm)
    y-=38*mm

    # CTA final — duas linhas separadas
    ycc=y-5*mm; chc=28*mm
    card_d(c,18*mm,ycc-chc,W-36*mm,chc,fill=VD,r=4,borda=VN)
    nline(c,18*mm,ycc,W-36*mm,2.5)
    c.setFillColor(BR); c.setFont(FB,20); c.drawCentredString(W/2,ycc-12*mm,f"{nome},")
    c.setFillColor(VN); c.setFont(FB,20); c.drawCentredString(W/2,ycc-24*mm,"agora é a sua vez.")
    rodape_d(c,9); c.showPage()

# ── PRINCIPAL ──────────────────────────────────────────────────────────────────
def gerar_pdf_diagnostico(dados):
    buf=io.BytesIO(); cv=canvas.Canvas(buf,pagesize=A4)
    cv.setTitle("Diagnóstico Personalizado - Luis Kummer")
    if not dados.get("imc"):
        iv=calc_imc(dados.get("peso"),dados.get("altura"))
        if iv: dados["imc"]=iv
    pag_capa(cv,dados); pag_bio(cv,dados); pag_hab(cv,dados); pag_perfil(cv,dados)
    pag_dicas(cv,dados); pag_oms(cv,dados); pag_app(cv,dados); pag_oferta(cv,dados); pag_dep(cv,dados)
    cv.save(); buf.seek(0); return buf.read()

if __name__=="__main__":
    dados={"nome":"Camila","objetivo":"emagrecer","sexo":"F",
           "peso":"72","altura":"162","idade":"34","peso_obj":"62","imc":None,
           "limitacao":"joelho","medicamento":"tireoide","exercicio":"1x","tempo_treino":"30a45",
           "freq_cardio":"3x","cardio":"caminhada,danca","tempo_cardio":"20a30",
           "alimentacao":"media","obstaculo":"tempo,motivacao","estresse":"7",
           "compro":"8","origem":"luana"}
    pdf=gerar_pdf_diagnostico(dados)
    with open("/mnt/user-data/outputs/diagnostico_v9.pdf","wb") as f: f.write(pdf)
    print("OK — 9 páginas")
