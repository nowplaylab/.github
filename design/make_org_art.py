"""Картинки для страницы организации nowplaylab: баннер в стиле ТВ-баннера NowPlaying
(строки, горит одна) и карточка проекта. Рисуется в 2x для чёткости, PNG с прозрачными углами."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
NP = r'C:\Users\try\Desktop\tab 3 прошив\nowplaying'
FONTS = os.path.join(NP, 'android', 'assets', 'fonts')
BOLD = os.path.join(FONTS, 'Inter-DisplayBold.ttf')
SEMI = os.path.join(FONTS, 'Inter-DisplaySemiBold.ttf')
MED = os.path.join(FONTS, 'Inter-Medium.ttf')
OUT = os.path.join(HERE, 'profile')


def lav_gradient(w, h):
    """Лавандовый фон, как у баннера: светлее слева сверху, глубже слева снизу, ровный справа."""
    tl, bl, rt = (0x7a, 0x68, 0x9b), (0x34, 0x37, 0x59), (0x55, 0x50, 0x7f)
    small = Image.new('RGB', (64, 32))
    px = small.load()
    for y in range(32):
        for x in range(64):
            fy, fx = y / 31, x / 63
            left = tuple(tl[i] + (bl[i] - tl[i]) * fy for i in range(3))
            k = min(1, fx * 1.4)
            px[x, y] = tuple(int(left[i] + (rt[i] - left[i]) * k) for i in range(3))
    return small.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(w / 80))


def rounded(img, r):
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    out = img.convert('RGBA')
    out.putalpha(mask)
    return out


def center_text(d, cx, y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def banner():
    W, H = 2560, 760
    img = lav_gradient(W, H).convert('RGBA')
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rows = [('Old phones', 104, 0.29), ('Old tablets', 104, 0.49), ('nowplaylab', 150, 1.0),
            ('Old TVs', 104, 0.49), ('From the drawer', 104, 0.29)]
    gap = 26
    heights = []
    for text, size, _ in rows:
        f = ImageFont.truetype(BOLD, size)
        a, b = f.getbbox('Hg')[1], f.getbbox('Hg')[3]
        heights.append(b - a)
    total = sum(heights) + gap * (len(rows) - 1)
    y = (H - total) / 2
    for (text, size, alpha), hh in zip(rows, heights):
        f = ImageFont.truetype(BOLD, size)
        top = f.getbbox('Hg')[1]
        center_text(d, W / 2, y - top, text, f, (255, 255, 255, int(255 * alpha)))
        y += hh + gap
    img = Image.alpha_composite(img, layer)
    rounded(img.convert('RGB'), 44).save(os.path.join(OUT, 'banner.png'), optimize=True)


def card():
    W, H = 2560, 980
    bg = Image.new('RGB', (W, H), (0x1d, 0x1c, 0x30))
    # мягкое лавандовое пятно справа, как свечение за обложкой в приложении
    glow = Image.new('RGB', (W, H), (0x1d, 0x1c, 0x30))
    ImageDraw.Draw(glow).ellipse((W * 0.55, -H * 0.3, W * 1.25, H * 1.2), fill=(0x4a, 0x40, 0x72))
    bg = Image.blend(bg, glow.filter(ImageFilter.GaussianBlur(220)), 1.0)
    img = bg.convert('RGBA')
    # скрин с планшета (свой тестовый трек), в тонкой рамке планшета
    shot = Image.open(os.path.join(NP, 'design', 'themes-now', 'classic.png')).convert('RGB')
    sw = 1360
    sh = round(shot.height * sw / shot.width)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    pad = 34
    x0, y0 = 110, (H - sh - 2 * pad) // 2
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0, y0 + 40, x0 + sw + 2 * pad, y0 + sh + 2 * pad + 40), 60, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x0 + sw + 2 * pad, y0 + sh + 2 * pad), 56, fill=(0x16, 0x16, 0x18))
    d.rounded_rectangle((x0, y0, x0 + sw + 2 * pad, y0 + sh + 2 * pad), 56, outline=(0x33, 0x33, 0x38), width=3)
    img.paste(shot, (x0 + pad, y0 + pad))
    # текст справа
    tx = x0 + sw + 2 * pad + 120
    f_title = ImageFont.truetype(BOLD, 128)
    f_sub = ImageFont.truetype(SEMI, 56)
    f_small = ImageFont.truetype(MED, 46)
    d.text((tx, 300), 'NowPlaying', font=f_title, fill=(255, 255, 255))
    d.text((tx, 470), 'Windows', font=f_sub, fill=(232, 230, 242))
    d.text((tx, 545), 'Android 4.1+', font=f_sub, fill=(232, 230, 242))
    d.text((tx, 620), 'Android TV', font=f_sub, fill=(232, 230, 242))
    d.text((tx, 730), 'Open source, MIT', font=f_small, fill=(150, 146, 176))
    rounded(img.convert('RGB'), 44).save(os.path.join(OUT, 'nowplaying.png'), optimize=True)


os.makedirs(OUT, exist_ok=True)
banner()
card()
print('ok')
