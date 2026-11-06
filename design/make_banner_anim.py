"""Анимированный баннер nowplaylab: фон из записи Figma (кольцо ~16.9 c),
поверх строки едут как текст песни: вниз по одной, потом обратно до NowPlay Lab."""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
NP = r'C:\Users\try\Desktop\tab 3 прошив\nowplaying'
FF = os.path.join(NP, r'pc\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
BOLD = os.path.join(NP, r'android\assets\fonts\Inter-DisplayBold.ttf')

OW = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
FPS = int(sys.argv[2]) if len(sys.argv) > 2 else 20
OH = round(OW * 968 / 3264)
DW, DH = 2560, round(2560 * 968 / 3264)      # координаты макета (как у слоя с текстом)
SS = 2 * OW / DW                              # текст рисуем в 2x от выхода

P = 507 / 30          # период фона
A = 1.6               # с какого места записи начинаем кольцо
X = 0.8               # плавная склейка в конце
N = round(P * FPS)

LINES = ['Old Tablets', 'Old TVs', 'NowPlay Lab', 'Old Phones', 'From the drawer']
SMALL, BIG = 91, 109.5
PITCH = 141
ALPHA = [255, 125, 74, 34, 0]

# ---------- фон: кадры из записи ----------
raw = os.path.join(HERE, f'bg_{OW}_{FPS}.rgb')
if not os.path.exists(raw):
    subprocess.run([FF, '-v', 'error', '-y', '-ss', '0', '-i', os.path.join(HERE, 'in.mov'),
                    '-vf', f'crop=3264:968:72:664,fps={FPS},scale={OW}:{OH}:flags=lanczos',
                    '-t', '19', '-f', 'rawvideo', '-pix_fmt', 'rgb24', raw], check=True)
blob = open(raw, 'rb').read()
fsz = OW * OH * 3
def src(t):
    i = min(round(t * FPS), len(blob) // fsz - 1)
    return Image.frombytes('RGB', (OW, OH), blob[i * fsz:(i + 1) * fsz])

def bg(t):
    a = src(A + t)
    if t > P - X:
        w = (t - (P - X)) / X
        w = w * w * (3 - 2 * w)
        a = Image.blend(a, src(A + t - P), w)
    return a

# ---------- текст: где сейчас «центр» списка ----------
def ease(x):            # плавно разгон-торможение
    return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, x)))

T = P / 2               # цикл текста, два на кольцо фона
HOLD0, STEP, REST, BACK = 1.5, 0.55, 0.45, 1.5
def scroll(t):
    t %= T
    s = 2.0
    if t < HOLD0:
        return s
    t -= HOLD0
    for k in range(4):              # вниз: строки едут вниз, загорается верхняя
        if t < STEP:
            return s - ease(t / STEP)
        t -= STEP
        s -= 1
        if t < REST:
            return s
        t -= REST
    if t < BACK:                    # обратно до NowPlay Lab
        x = t / BACK
        e = x * x * x * (x * (6 * x - 15) + 10)
        return s + 4 * e
    return 2.0

fonts = {}
def font(sz):
    k = round(sz * SS * 4) / 4
    if k not in fonts:
        fonts[k] = ImageFont.truetype(BOLD, k)
    return fonts[k]

def alpha(o):
    o = min(abs(o), 4)
    i = int(o)
    if i >= 4:
        return 0
    return ALPHA[i] + (ALPHA[i + 1] - ALPHA[i]) * (o - i)

def text_layer(s):
    W, H = round(DW * SS), round(DH * SS)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(math.floor(s) - 4, math.floor(s) + 6):
        o = k - s
        a = alpha(o)
        if a <= 0:
            continue
        sz = SMALL + (BIG - SMALL) * max(0, 1 - abs(o))
        f = font(sz)
        txt = LINES[k % len(LINES)]
        cy = (DH / 2 + o * PITCH) * SS
        x0, y0, x1, y1 = f.getbbox('Old Hg' if txt != 'NowPlay Lab' else 'NowPlay Lab')
        cap = f.getbbox('H')
        w = d.textlength(txt, font=f)
        # центр по высоте заглавных букв
        y = cy - (cap[1] + cap[3]) / 2
        d.text((W / 2 - w / 2, y), txt, font=f, fill=(255, 255, 255, round(a)))
    return layer.resize((OW, OH), Image.LANCZOS)

# ---------- скругление ----------
R = round(44 * OW / 2560)
mask = Image.new('L', (OW * 4, OH * 4), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, OW * 4 - 1, OH * 4 - 1), R * 4, fill=255)
mask = mask.resize((OW, OH), Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)

out = os.path.join(HERE, f'frames_{OW}_{FPS}')
os.makedirs(out, exist_ok=True)
for n in range(N):
    t = n / FPS
    im = bg(t).convert('RGBA')
    im.alpha_composite(text_layer(scroll(t)))
    im.putalpha(mask)
    im.save(os.path.join(out, f'{n:04d}.png'))
print('frames', N, OW, OH)

gif = os.path.join(HERE, f'banner_{OW}_{FPS}.gif')
pal = os.path.join(HERE, 'pal.png')
subprocess.run([FF, '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(out, '%04d.png'),
                '-vf', 'palettegen=max_colors=256:stats_mode=full:reserve_transparent=1', pal], check=True)
subprocess.run([FF, '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(out, '%04d.png'), '-i', pal,
                '-lavfi', 'paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle:alpha_threshold=128',
                '-loop', '0', gif], check=True)
print(gif, os.path.getsize(gif) / 1e6, 'MB')
