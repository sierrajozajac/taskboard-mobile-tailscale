# App icons

Tauri needs generated icons (`32x32.png`, `128x128.png`, `icon.ico`, `icon.icns`) here
before `tauri dev` / `tauri build`.

Generate them from a single square source PNG (≥ 512×512) — this uses the **JS** Tauri
CLI and does **not** require Rust:

```bash
cd desktop
npm install
npm run tauri icon path/to/logo.png   # writes all sizes into src-tauri/icons/
```

The generated icon files are git-ignored binaries; regenerate them after cloning.
