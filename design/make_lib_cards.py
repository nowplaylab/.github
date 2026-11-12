"""Карточки библиотек для страницы организации nowplaylab.
Тот же лавандовый фон, что у баннера, сверху простой значок, снизу название и подпись.
Квадрат 1000x1000, на странице стоят по три в ряд."""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'profile')
# Шрифт Inter: путь можно передать первым аргументом
FONT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'Inter.ttf')

W = H = 1000
SIDE = 70  # прозрачное поле слева и справа
WHITE = (255, 255, 255)
SOFT = (232, 230, 242)
MUTED = (160, 155, 190)


def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([min(32, max(14, size // 3)), weight])
    except Exception:
        pass
    return f


def lav_gradient(w, h):
    """Как у баннера: светлее слева сверху, глубже слева снизу, ровный справа."""
    tl, bl, rt = (0x7a, 0x68, 0x9b), (0x34, 0x37, 0x59), (0x55, 0x50, 0x7f)
    small = Image.new('RGB', (32, 32))
    px = small.load()
    for y in range(32):
        for x in range(32):
            fy, fx = y / 31, x / 31
            left = tuple(tl[i] + (bl[i] - tl[i]) * fy for i in range(3))
            k = min(1, fx * 1.4)
            px[x, y] = tuple(int(left[i] + (rt[i] - left[i]) * k) for i in range(3))
    return small.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(w / 60))


def rounded(img, r):
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    out = img.convert('RGBA')
    out.putalpha(mask)
    return out


def glow(img, draw_fn, blur, strength=1.0):
    """Мягкое свечение под значком."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    if strength != 1.0:
        a = layer.getchannel('A').point(lambda v: int(v * strength))
        layer.putalpha(a)
    return Image.alpha_composite(img, layer)


X0 = 90  # левый отступ


def over(img, fn):
    """Рисует на прозрачном слое и накладывает, чтобы полупрозрачность работала."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    return Image.alpha_composite(img, layer)


def icon_lyrics(img):
    """Строки текста песни, горит одна, как на баннере."""
    rows = [(430, 0.22), (560, 0.4), (500, 1.0), (380, 0.4), (470, 0.22)]
    for i, (w, a) in enumerate(rows):
        y = 110 + i * 76
        box = (X0, y, X0 + w, y + 46)
        if a == 1.0:
            img = glow(img, lambda d, box=box: d.rounded_rectangle(box, 23, fill=(255, 255, 255, 110)), 28)
        img = over(img, lambda d, box=box, a=a: d.rounded_rectangle(box, 23, fill=(255, 255, 255, int(255 * a))))
    return img


def icon_lamp(img):
    """Лампочка со свечением и волны сигнала справа."""
    cx, cy, r = X0 + 130, 260, 115
    img = glow(img, lambda d: d.ellipse((cx - r - 70, cy - r - 70, cx + r + 70, cy + r + 70), fill=(255, 236, 200, 150)), 60)

    def draw(d):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE)
        d.rounded_rectangle((cx - 56, cy + r - 4, cx + 56, cy + r + 46), 14, fill=(255, 255, 255, 170))
        d.rounded_rectangle((cx - 38, cy + r + 56, cx + 38, cy + r + 84), 12, fill=(255, 255, 255, 110))
        ox = cx + r + 40
        for i, a in enumerate((230, 150, 80)):
            rr = 70 + i * 75
            d.arc((ox - rr, cy - rr, ox + rr, cy + rr), -45, 45, fill=(255, 255, 255, a), width=26)
    return over(img, draw)


def icon_house(img):
    """Домик с горящим окном и выключатель."""
    x, y, w, h = X0 + 20, 250, 300, 220
    wx, wy = x + w / 2, y + h / 2
    img = glow(img, lambda d: d.ellipse((wx - 115, wy - 115, wx + 115, wy + 115), fill=(255, 236, 200, 170)), 45)

    def draw(d):
        roof = [(x - 30, y + 10), (x + w / 2, y - 130), (x + w + 30, y + 10)]
        d.line(roof, fill=WHITE, width=32, joint='curve')
        for p in (roof[0], roof[2]):
            d.ellipse((p[0] - 16, p[1] - 16, p[0] + 16, p[1] + 16), fill=WHITE)
        d.rounded_rectangle((x + 10, y, x + w - 10, y + h), 28, outline=WHITE, width=28)
        d.rounded_rectangle((wx - 46, wy - 46, wx + 46, wy + 46), 14, fill=WHITE)
        sx, sy = x + w + 130, y + 40
        d.rounded_rectangle((sx, sy, sx + 190, sy + 100), 50, fill=(255, 255, 255, 230))
        d.ellipse((sx + 100, sy + 10, sx + 180, sy + 90), fill=(0x55, 0x50, 0x7f, 255))
    return over(img, draw)


def fit(text, size, weight, maxw):
    """Уменьшает шрифт, пока строка не влезет."""
    while size > 40:
        f = font(size, weight)
        if f.getlength(text) <= maxw:
            return f
        size -= 2
    return font(size, weight)


def card(name, en, ru, icon, fn):
    img = lav_gradient(W, H).convert('RGBA')
    img = icon(img)
    d = ImageDraw.Draw(img)
    d.text((X0, 600), name, font=fit(name, 92, 700, W - 2 * X0), fill=WHITE)
    d.text((X0, 730), en, font=font(50, 600), fill=SOFT)
    d.text((X0, 800), ru, font=font(42, 500), fill=MUTED)
    d.text((X0, 890), 'Python · MIT', font=font(38, 500), fill=MUTED)
    card_img = rounded(img.convert('RGB'), 56)
    # прозрачные поля по бокам: так между карточками на странице есть промежуток
    out = Image.new('RGBA', (W + 2 * SIDE, H), (0, 0, 0, 0))
    out.paste(card_img, (SIDE, 0))
    out.save(os.path.join(OUT, fn), optimize=True)


os.makedirs(OUT, exist_ok=True)
card('synced-lyrics', 'Synced song lyrics', 'Текст песни по времени', icon_lyrics, 'lib-synced-lyrics.png')
card('yeelight-lan', 'Yeelight over LAN', 'Лампы Yeelight по сети', icon_lamp, 'lib-yeelight-lan.png')
card('yandex-smarthome', 'Alice smart home', 'Умный дом Яндекса', icon_house, 'lib-yandex-smarthome.png')
print('ok')
