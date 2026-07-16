# Setup

Everything except the Tauri desktop build works with just Python and Node. The desktop *window*
additionally needs Rust + C++ build tools. Set up in this order and you can stop wherever you like.

## 0. Prerequisites

| Tool | Needed for | Install |
| --- | --- | --- |
| Python 3.11 | the API | Already present; invoke with the `py` launcher on Windows. |
| Node 20+ | shared package, both apps | Already present (`node --version`). |
| Rust (stable) | Tauri desktop build only | `winget install Rustlang.Rustup` then `rustup default stable` |
| MSVC C++ Build Tools | Tauri desktop build only | `winget install Microsoft.VisualStudio.2022.BuildTools`, then select "Desktop development with C++" |

> On Windows, bash's bare `python` opens the Microsoft Store. Use `py` (the launcher) for the API.

## 1. Backend (API)

```bash
cd api
py -m venv .venv
.venv/Scripts/activate            # PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env              # defaults are fine for console mode
py -m app.seed                    # optional: demo boards/tasks
uvicorn app.main:app --reload     # http://127.0.0.1:8000  (docs at /docs)
```

Run the tests any time with `pytest -q`.

To print for real instead of to the log, follow
[printer integration, turning on real printing](03-printer-integration.md#turning-on-real-printing).

## 2. Shared package + clients

From the repo root (npm workspaces):

```bash
npm install
npm run build:shared
```

### Desktop (browser dev, no Rust needed)

```bash
npm run dev --workspace desktop   # http://localhost:1420 in your browser
```

This is the fastest way to work on the UI. It talks to the API at `http://127.0.0.1:8000` (change it
in the sidebar's "API URL" field).

### Desktop (native window, needs Rust + C++ build tools)

```bash
cd desktop
npm run tauri icon path/to/logo.png   # one-time: generate app icons (JS only, no Rust)
npm run tauri:dev                     # builds the Rust shell and opens the window
```

### Mobile (Expo)

```bash
npm run dev:mobile                # or: npm run start --workspace mobile
```

Open the project in **Expo Go** on your phone (same Wi-Fi as the PC). On the first screen, set the
**API URL** to the PC's LAN address, e.g. `http://192.168.1.20:8000` (a phone can't reach
`localhost`). Find the PC's IP with `ipconfig`. The URL is saved on the device (AsyncStorage), so you
only enter it once; for remote use, point it at the PC's Tailscale IP instead (see section 3).

> Expo Go only. This edition runs the mobile app through the Expo Go client; there is no standalone
> Android/iOS build here.

## 3. Use it from a browser, and away from home (Tailscale)

The API can serve the board itself, so any browser (phone or laptop) can use TaskBoard with no dev
server and no Expo. Build the web bundle once, then start the API:

```bash
npm run build --workspace desktop     # emits desktop/dist
uvicorn app.main:app --reload         # from api/, as above
```

On startup the API mounts `desktop/dist` at `/` (see [`api/app/main.py`](../api/app/main.py)); if the
build isn't present it stays API-only and logs that. Open the API's address in a browser and you get
the full, responsive UI, which auto-connects to that same origin:

```
http://<api-host>:8000
```

On a narrow screen the sidebar collapses into a drawer, so the same build works on a phone.

**Reaching it from outside your network (Tailscale).** Rather than opening a port, put both machines
on a private mesh:

1. Install [Tailscale](https://tailscale.com/) on the PC and on your phone; sign both into the same
   tailnet.
2. Find the PC's mesh IP (a `100.x.y.z` address) with `tailscale ip -4` (or in the Tailscale app).
3. Make sure the API is bound to all interfaces, not just loopback: run it with
   `uvicorn app.main:app --host 0.0.0.0` (the auto-start launcher below already does this).
4. From the phone, use `http://100.x.y.z:8000`, in a browser or as the mobile app's API URL.

No ports are opened to the public internet and the printer stays home; only devices on your tailnet
can reach the API.

## Ports at a glance

| Service | URL |
| --- | --- |
| API | `http://127.0.0.1:8000` (`/docs` for Swagger) |
| Board in a browser | `http://<api-host>:8000` (served by the API once `desktop/dist` is built) |
| Desktop dev server | `http://localhost:1420` |
| Mobile | Expo Go, pointed at the PC's `http://<lan-ip>:8000` (or `http://100.x.y.z:8000` over Tailscale) |

## Auto-start the API on Windows (optional)

To keep the API running so it's always available (e.g. over a Tailscale mesh from your phone),
[`api/serve-hidden.vbs`](../api/serve-hidden.vbs) launches uvicorn **windowless**, bound to
`0.0.0.0`, logging to `api/api.log`. Point a shortcut at it from your Startup folder so it runs at
logon (no admin needed):

```powershell
$vbs   = (Resolve-Path .\api\serve-hidden.vbs).Path
$lnk   = Join-Path ([Environment]::GetFolderPath('Startup')) 'TaskBoard API.lnk'
$ws    = New-Object -ComObject WScript.Shell
$sc    = $ws.CreateShortcut($lnk)
$sc.TargetPath = "$env:SystemRoot\System32\wscript.exe"
$sc.Arguments  = "`"$vbs`""
$sc.Save()
```

Notes:
- The PC must be **awake** and Tailscale running for remote access; a sleeping PC is unreachable.
- `pythonw` needs its output redirected (the `.vbs` sends it to `api.log`); without a valid
  stdout/stderr, uvicorn's logging kills the process.
- For restart-on-crash / start-before-logon, register a Scheduled Task instead (needs admin).
