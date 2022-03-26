import os
from PIL import Image, ImageDraw

gpoint = {
    '0': (512, 70),
    '1': (880, 290),
    '2': (880, 734),
    '3': (512, 954),
    '4': (144, 734),
    '5': (144, 290),
    '6': (696, 400),
    '7': (696, 624),
    '8': (328, 624),
    '9': (328, 400),
    'a': (512, 512)
}


def draw_bg(im, xy):
    bg = Image.open(os.path.join(os.path.dirname(__file__),
                                 'defaultbg.png')).convert('RGBA')
    im.paste(bg, xy, bg)


def draw_glyph(im, xy, color, points):
    draw = ImageDraw.Draw(im, 'RGBA')
    for i in range(0, len(points), 2):
        p1 = gpoint[points[i]]
        p2 = gpoint[points[i+1]]
        draw.line(
            (int(p1[0] / 4), int(p1[1] / 4), int(p2[0] / 4), int(p2[1] / 4)),
            fill=color,
            width=7, joint="curve")
