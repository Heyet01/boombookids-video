"""BoomBoo Kids original characters and props (all drawn in code, owned by the channel)."""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 3  # supersampling
INK = (45, 22, 85)

CHARS = {
    "boo":  dict(body=(140, 82, 255), belly=(200, 175, 255), top="horns"),
    "pip":  dict(body=(255, 196, 40), belly=(255, 236, 160), top="ears"),
    "momo": dict(body=(70, 205, 120), belly=(185, 245, 200), top="antenna"),
}


def char_sprite(name, size, blink=0.0, mouth=0.4, wave=0.0):
    c = CHARS[name]
    body, belly = c["body"], c["belly"]
    dark = tuple(int(v * 0.72) for v in body)
    W = size * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(2, int(W * 0.014))
    cx, cy, r = W / 2, W * 0.56, W * 0.34
    # top decoration
    if c["top"] == "horns":
        for s in (-1, 1):
            hx = cx + s * r * 0.55
            d.polygon([(hx - r * .17, cy - r * .7), (hx + r * .17, cy - r * .7), (hx + s * r * .12, cy - r * 1.2)],
                      fill=(255, 190, 60), outline=INK, width=lw)
    elif c["top"] == "ears":
        for s in (-1, 1):
            ex = cx + s * r * 0.62
            d.ellipse((ex - r * .3, cy - r * 1.05, ex + r * .3, cy - r * .45), fill=body, outline=INK, width=lw)
            d.ellipse((ex - r * .16, cy - r * .92, ex + r * .16, cy - r * .6), fill=(255, 150, 170))
    else:
        d.line((cx, cy - r * .85, cx + r * .1, cy - r * 1.3), fill=INK, width=lw * 2)
        d.ellipse((cx + r * .1 - r * .14, cy - r * 1.44, cx + r * .1 + r * .14, cy - r * 1.16), fill=(255, 90, 140), outline=INK, width=lw)
    # feet
    for s in (-1, 1):
        d.ellipse((cx + s * r * .45 - r * .28, cy + r * .78, cx + s * r * .45 + r * .28, cy + r * 1.02), fill=dark, outline=INK, width=lw)
    # arms (right arm can wave up)
    for s in (-1, 1):
        lift = wave if s == 1 else 0
        ay = cy + r * .25 - lift * r * .75
        ax = cx + s * (r * .98 + lift * r * .1)
        d.ellipse((ax - r * .18, ay - r * .2, ax + r * .18, ay + r * .2), fill=body, outline=INK, width=lw)
    # body
    d.ellipse((cx - r, cy - r * .9, cx + r, cy + r * .95), fill=body, outline=INK, width=int(lw * 1.3))
    d.ellipse((cx - r * .55, cy + r * .05, cx + r * .55, cy + r * .85), fill=belly)
    # eyes
    for s in (-1, 1):
        ex, ey, er = cx + s * r * .36, cy - r * .3, r * .27
        h = max(er * (1 - blink), er * 0.08)
        d.ellipse((ex - er, ey - h, ex + er, ey + h), fill="white", outline=INK, width=lw)
        if blink < 0.7:
            pr = er * .55
            ph = pr * (1 - blink)
            d.ellipse((ex - pr + r * .03, ey - ph, ex + pr + r * .03, ey + ph), fill=(30, 20, 60))
            d.ellipse((ex - pr * .1, ey - pr * .7, ex + pr * .35, ey - pr * .25), fill="white")
    for s in (-1, 1):
        d.ellipse((cx + s * r * .68 - r * .13, cy - r * .02, cx + s * r * .68 + r * .13, cy + r * .14), fill=(255, 130, 180))
    # mouth
    mw, mh = r * .38, r * (.06 + .32 * mouth)
    if mouth < 0.08:
        d.arc((cx - mw * .7, cy - r * .1, cx + mw * .7, cy + r * .18), 20, 160, fill=INK, width=lw)
    else:
        d.chord((cx - mw, cy - mh * .3 + r * .02, cx + mw, cy + mh + r * .02), 0, 180, fill=(120, 20, 60), outline=INK, width=lw)
        d.ellipse((cx - mw * .45, cy + mh * .5, cx + mw * .45, cy + mh + r * .02), fill=(255, 110, 140))
    return im.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ props
COLORS = {
    "red": (238, 50, 60), "orange": (255, 140, 30), "yellow": (255, 215, 40), "green": (60, 190, 80),
    "blue": (40, 120, 240), "purple": (150, 80, 230), "pink": (255, 120, 180), "brown": (150, 95, 50),
    "black": (40, 40, 50), "white": (250, 250, 250), "gray": (150, 150, 160),
}


def col(name, default="red"):
    return COLORS.get(str(name).lower().strip(), COLORS.get(default))


def _star(cx, cy, r, n=5, inner=0.45, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = rot + i * math.pi / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def prop(kind, size, color=(238, 50, 60)):
    W = size * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(2, int(W * 0.02))
    c, r = W / 2, W * 0.42
    k = str(kind).lower()
    if k == "star":
        d.polygon(_star(c, c, r), fill=color, outline=INK, width=lw)
    elif k == "heart":
        d.ellipse((c - r, c - r * .75, c, c + r * .2), fill=color)
        d.ellipse((c, c - r * .75, c + r, c + r * .2), fill=color)
        d.polygon([(c - r * .97, c - r * .1), (c + r * .97, c - r * .1), (c, c + r)], fill=color)
    elif k == "square":
        d.rounded_rectangle((c - r * .85, c - r * .85, c + r * .85, c + r * .85), radius=r * .12, fill=color, outline=INK, width=lw)
    elif k == "triangle":
        d.polygon([(c, c - r), (c + r, c + r * .8), (c - r, c + r * .8)], fill=color, outline=INK, width=lw)
    elif k == "sun":
        for i in range(12):
            a = i * math.pi / 6
            d.line((c + r * .7 * math.cos(a), c + r * .7 * math.sin(a), c + r * math.cos(a), c + r * math.sin(a)), fill=(255, 170, 0), width=lw * 2)
        d.ellipse((c - r * .62, c - r * .62, c + r * .62, c + r * .62), fill=(255, 210, 40), outline=INK, width=lw)
    elif k == "moon":
        d.ellipse((c - r, c - r, c + r, c + r), fill=(255, 235, 140), outline=INK, width=lw)
        d.ellipse((c - r * .35, c - r * 1.1, c + r * 1.25, c + r * .7), fill=(0, 0, 0, 0))
    elif k == "cloud":
        for (x, y, rr) in ((-.45, .1, .42), (.05, -.15, .55), (.5, .1, .42)):
            d.ellipse((c + x * r - rr * r, c + y * r - rr * r, c + x * r + rr * r, c + y * r + rr * r), fill=(255, 255, 255), outline=INK, width=lw)
        d.rectangle((c - r * .8, c + r * .05, c + r * .8, c + r * .5), fill=(255, 255, 255))
    elif k == "apple":
        d.ellipse((c - r * .9, c - r * .7, c + r * .9, c + r), fill=color, outline=INK, width=lw)
        d.line((c, c - r * .7, c + r * .1, c - r * 1.05), fill=(110, 70, 30), width=lw * 2)
        d.ellipse((c + r * .1, c - r * 1.05, c + r * .55, c - r * .8), fill=(70, 180, 70), outline=INK, width=lw)
    elif k == "balloon":
        d.line((c, c + r * .7, c - r * .1, c + r * 1.1), fill=INK, width=lw)
        d.ellipse((c - r * .7, c - r, c + r * .7, c + r * .7), fill=color, outline=INK, width=lw)
        d.ellipse((c - r * .4, c - r * .75, c - r * .15, c - r * .4), fill=(255, 255, 255, 170))
    elif k == "flower":
        for i in range(6):
            a = i * math.pi / 3
            px, py = c + r * .55 * math.cos(a), c - r * .1 + r * .55 * math.sin(a)
            d.ellipse((px - r * .35, py - r * .35, px + r * .35, py + r * .35), fill=color, outline=INK, width=lw)
        d.ellipse((c - r * .28, c - r * .38, c + r * .28, c + r * .18), fill=(255, 210, 40), outline=INK, width=lw)
    elif k == "fish":
        d.polygon([(c + r * .45, c), (c + r, c - r * .45), (c + r, c + r * .45)], fill=color, outline=INK, width=lw)
        d.ellipse((c - r, c - r * .55, c + r * .6, c + r * .55), fill=color, outline=INK, width=lw)
        d.ellipse((c - r * .6, c - r * .2, c - r * .35, c + r * .05), fill="white", outline=INK, width=lw)
    elif k == "car":
        d.rounded_rectangle((c - r, c - r * .1, c + r, c + r * .5), radius=r * .15, fill=color, outline=INK, width=lw)
        d.rounded_rectangle((c - r * .55, c - r * .55, c + r * .45, c), radius=r * .15, fill=color, outline=INK, width=lw)
        for x in (-.55, .55):
            d.ellipse((c + x * r - r * .25, c + r * .3, c + x * r + r * .25, c + r * .8), fill=(40, 40, 50), outline=INK, width=lw)
    else:  # circle / ball
        d.ellipse((c - r, c - r, c + r, c + r), fill=color, outline=INK, width=lw)
        d.ellipse((c - r * .55, c - r * .6, c - r * .2, c - r * .25), fill=(255, 255, 255, 150))
    return im.resize((size, size), Image.LANCZOS)


PROPS = ["star", "heart", "square", "triangle", "circle", "sun", "moon", "cloud", "apple", "balloon", "flower", "fish", "car"]
