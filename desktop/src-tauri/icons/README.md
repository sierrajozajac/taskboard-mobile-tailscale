# App icons

Tauri needs generated icons (`32x32.png`, `128x128.png`, `icon.ico`, `icon.icns`) here
before `tauri dev` / `tauri build`. They are git-ignored binaries — regenerate after cloning.

The source image lives at [`desktop/app-icon.png`](../../app-icon.png), produced by
[`desktop/make_icon.py`](../../make_icon.py). To (re)generate everything:

```bash
cd desktop
python make_icon.py                 # writes app-icon.png (needs Pillow)
npm install
npm run tauri icon app-icon.png     # JS CLI — no Rust required
```

To use your own logo instead, point the last command at any square PNG (≥ 512×512).
