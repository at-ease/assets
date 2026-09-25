"""生成体重同步的 iOS 图标：和 NodePulse 同一套深色底，线条换成体重走势。"""
import math
from PIL import Image, ImageDraw

S = 4                      # 超采样倍数，最后缩回 1024 做抗锯齿
N = 1024 * S
TOP, BOTTOM = (53, 53, 60), (19, 19, 23)   # 与 NodePulse 背景一致
W = 40                     # 线宽，同 NodePulse
R = 46                     # 终点圆点半径
GAP = 18                   # 圆点与线头之间的空隙

# 走势折线：起伏着往下走，最后一个点是"这次称重"
KNOTS = [(282, 385), (435, 590), (589, 455), (742, 640)]


def bg_color(y):
    t = y / 1023
    return tuple(round(a + (b - a) * t) for a, b in zip(TOP, BOTTOM))


def bg():
    im = Image.new("RGB", (N, N))
    d = ImageDraw.Draw(im)
    for y in range(N):
        d.line([(0, y), (N, y)], fill=bg_color(y / S))
    return im


def dot(d, c, r, color):
    x, y = c[0] * S, c[1] * S
    r *= S
    d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def make(color, warn=False):
    im = bg()
    d = ImageDraw.Draw(im)
    # 最后一段缩短，让线头停在圆点外 GAP 处
    (ax, ay), (bx, by) = KNOTS[-2], KNOTS[-1]
    k = (R + GAP + W / 2) / math.hypot(bx - ax, by - ay)
    pts = KNOTS[:-1] + [(bx - (bx - ax) * k, by - (by - ay) * k)]
    d.line([(x * S, y * S) for x, y in pts], fill=color, width=W * S)
    for p in pts:                      # 圆头、圆角
        dot(d, p, W / 2, color)
    dot(d, KNOTS[-1], R, color)
    if warn:                           # 圆点里挖一个感叹号
        x, y = KNOTS[-1]
        dark = bg_color(y)
        d.rounded_rectangle([((x - 8) * S, (y - 30) * S), ((x + 8) * S, (y + 8) * S)],
                            radius=8 * S, fill=dark)
        dot(d, (x, y + 24), 8.5, dark)
    return im.resize((1024, 1024), Image.LANCZOS)


if __name__ == "__main__":
    make((64, 200, 255)).save("icon-ios.png")
    make((255, 159, 10), warn=True).save("icon-ios-warn.png")
