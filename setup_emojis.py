"""
setup_emojis.py
---------------
Gera a pasta 'emojis/' com os PNGs necessários para o gerar_pdf.py.
Execute uma vez no servidor antes de rodar a API:

    python setup_emojis.py

Funciona em Ubuntu/Debian (instala NotoColorEmoji se necessário).
"""

import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOJI_DIR = os.path.join(BASE_DIR, "emojis")
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

EMOJIS = {
    'balanca':   '⚖️',
    'regua':     '📏',
    'bolo':      '🎂',
    'alvo':      '🎯',
    'barras':    '📊',
    'musculo':   '💪',
    'correr':    '🏃',
    'salada':    '🥗',
    'relogio':   '⏱️',
    'bike':      '🚴',
    'alarme':    '⏰',
    'raiva':     '😤',
    'aviso':     '⚠️',
    'remedio':   '💊',
    'celular':   '📱',
    'estrela':   '⭐',
    'lupa':      '🔍',
    'lista':     '📋',
    'pino':      '📌',
    'halteres':  '🏋️',
    'grafico':   '📈',
    'camera':    '🎬',
    'chat':      '💬',
    'meditacao': '🧘',
    'foguete':   '🚀',
    'ok':        '✅',
    'trofeu':    '🏆',
    'fogo':      '🔥',
    'sorriso':   '😊',
    'brilho':    '🌟',
    'cadeado':   '🔓',
    'medico':    '⚕️',
}

def instalar_fonte():
    if os.path.exists(FONT_PATH):
        print(f"✅ Fonte encontrada: {FONT_PATH}")
        return True
    print("⚙️  Instalando fonte NotoColorEmoji...")
    try:
        subprocess.run(
            ["apt-get", "install", "-y", "fonts-noto-color-emoji"],
            check=True, capture_output=True
        )
        if os.path.exists(FONT_PATH):
            print("✅ Fonte instalada com sucesso.")
            return True
    except Exception as e:
        print(f"❌ Falha ao instalar via apt: {e}")

    # Tenta caminhos alternativos
    alternativas = [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/noto/NotoColorEmoji.ttf",
        "/usr/local/share/fonts/NotoColorEmoji.ttf",
    ]
    for p in alternativas:
        if os.path.exists(p):
            print(f"✅ Fonte encontrada em: {p}")
            return p
    print("❌ Fonte NotoColorEmoji não encontrada. Instale com:")
    print("   sudo apt-get install fonts-noto-color-emoji")
    return False

def gerar_emojis(font_path=None):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚙️  Instalando Pillow...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow",
                        "--break-system-packages", "-q"], check=True)
        from PIL import Image, ImageDraw, ImageFont

    fp = font_path if font_path and isinstance(font_path, str) else FONT_PATH
    if not os.path.exists(fp):
        print(f"❌ Fonte não encontrada em: {fp}")
        return False

    font = ImageFont.truetype(fp, 109)
    os.makedirs(EMOJI_DIR, exist_ok=True)

    ok = 0
    erros = []
    for nome, emoji in EMOJIS.items():
        try:
            img = Image.new('RGBA', (130, 130), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.text((5, 5), emoji, font=font, embedded_color=True)
            img.save(os.path.join(EMOJI_DIR, f"{nome}.png"))
            ok += 1
        except Exception as e:
            erros.append(f"{nome}: {e}")

    print(f"✅ Emojis gerados: {ok}/{len(EMOJIS)}")
    if erros:
        print("⚠️  Erros:")
        for e in erros:
            print(f"   {e}")
    return ok > 0

def verificar():
    faltando = [n for n in EMOJIS if not os.path.exists(os.path.join(EMOJI_DIR, f"{n}.png"))]
    if faltando:
        print(f"⚠️  Faltando {len(faltando)} emojis: {faltando}")
        return False
    print(f"✅ Todos os {len(EMOJIS)} emojis estão presentes em '{EMOJI_DIR}'")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  Setup de Emojis — Luis Kummer PDF")
    print("=" * 50)

    if verificar():
        print("Nada a fazer.")
        sys.exit(0)

    resultado = instalar_fonte()
    font_path = resultado if isinstance(resultado, str) else None

    if resultado:
        sucesso = gerar_emojis(font_path)
        if sucesso:
            verificar()
            print("\n✅ Setup concluído! Pode rodar o gerar_pdf.py normalmente.")
        else:
            print("\n❌ Falha ao gerar emojis.")
            sys.exit(1)
    else:
        sys.exit(1)
