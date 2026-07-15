# NetWatch

Windows desktop tool for monitoring network ports and processes — find what’s listening on a port and terminate sessions.

![NetWatch](assets/logo_header.png)

## Features

- Scan connections by port (like `netstat`)
- Quick port presets
- Sortable connection table
- Kill selected process / terminate all on a port
- Live auto-refresh
- RU / EU language switch
- Dark cyberpunk UI

## Run from source

```bat
run.bat
```

or:

```bat
python -m pip install -r requirements.txt
python main.py
```

## Build EXE

```bat
build.bat
```

Output: `dist\NetWatch.exe`

## Requirements

- Windows 10/11
- Python 3.10+ (for source / build)
- Admin rights recommended for full process access

## Download / SmartScreen

Browsers and Windows may show **"rarely downloaded"** / SmartScreen warnings for `NetWatch.exe`.
This is normal for a small open-source app without a paid code-signing certificate.

- Prefer downloading from the official GitHub Releases page only
- If Windows blocks: **More info → Run anyway**
- Or run from source: `python main.py`

## License

MIT
