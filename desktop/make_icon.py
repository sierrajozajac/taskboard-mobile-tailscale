"""Generate app-icon.png — a 1024px source image for `tauri icon`.

A dark rounded square with a white thermal-receipt glyph: an accent header bar,
text lines, and a torn zigzag bottom edge. Run once; the PNG is the input to
`npm run tauri icon`.
"""

from PIL import Image, ImageDraw

SIZE = 1024
BG = (23, 27, 33)         # panel dark
ACCENT = (79, 156, 249)   # blue
PAPER = (240, 242, 245)
INK = (150, 160, 172)

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Rounded-square background.
d.rounded_rectangle([0, 0, SIZE, SIZE], radius=220, fill=BG)

# Receipt body.
rx0, ry0, rx1 = 330, 210, 694
top = ry0
bottom = 760
d.rectangle([rx0, top, rx1, bottom], fill=PAPER)

# Torn zigzag bottom edge.
teeth = 8
tooth_w = (rx1 - rx0) / teeth
pts = [(rx0, bottom)]
for i in range(teeth):
    x_mid = rx0 + tooth_w * (i + 0.5)
    x_end = rx0 + tooth_w * (i + 1)
    pts.append((x_mid, bottom + 46))
    pts.append((x_end, bottom))
pts.append((rx1, bottom))
d.polygon(pts, fill=PAPER)

# Accent header bar.
d.rounded_rectangle([rx0 + 40, top + 44, rx1 - 40, top + 104], radius=18, fill=ACCENT)

# Text lines.
y = top + 168
for w in (0.85, 0.65, 0.78, 0.5):
    line_w = (rx1 - rx0 - 80) * w
    d.rounded_rectangle([rx0 + 40, y, rx0 + 40 + line_w, y + 34], radius=17, fill=INK)
    y += 84

img.save("app-icon.png")
print("wrote app-icon.png", img.size)
