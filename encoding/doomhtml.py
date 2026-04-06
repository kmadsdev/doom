import base64, pathlib

wasm_bytes = pathlib.Path("doom.wasm").read_bytes()
wad_bytes  = pathlib.Path("linuxdoom-1.10/doom1.wad").read_bytes()
main_js    = pathlib.Path("main.js").read_text()

wasm_b64 = base64.b64encode(wasm_bytes).decode()
wad_b64  = base64.b64encode(wad_bytes).decode()

# Patch main.js: replace fetch() calls with inline buffer reads
patched_js = main_js \
  .replace(
    "fetch('doom.wasm')",
    "Promise.resolve({ arrayBuffer: () => Promise.resolve(window._DOOM_WASM) })"
  ).replace(
    "fetch('doom1.wad')",
    "Promise.resolve({ arrayBuffer: () => Promise.resolve(window._DOOM_WAD) })"
  )

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DOOM (1993) — Single File</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      background: #000;
      width: 100%; height: 100vh;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      font-family: monospace;
      color: #c00;
    }}
    h1 {{ font-size: 2rem; letter-spacing: .2em; margin-bottom: .5rem; color: #f00; text-shadow: 0 0 20px #f00; }}
    p  {{ font-size: .75rem; color: #666; margin-bottom: 1rem; }}
    canvas {{
      display: block;
      width: 640px; height: 400px;
      image-rendering: pixelated;
      border: 2px solid #400;
    }}
    #controls {{ margin-top: .75rem; font-size: .7rem; color: #555; }}
    #controls span {{ color: #900; }}
  </style>
</head>
<body>
  <h1>DOOM</h1>
  <p>Episode 1: Knee-Deep in the Dead &nbsp;|&nbsp; id Software 1993 (Shareware)</p>
  <canvas id="screen" width="640" height="400" tabindex="0"></canvas>
  <div id="controls">
    <span>↑↓←→</span> move &nbsp;
    <span>CTRL</span> shoot &nbsp;
    <span>SPACE</span> open &nbsp;
    <span>ALT+←→</span> strafe &nbsp;
    <span>ENTER</span> confirm
  </div>
  <script>
  (function() {{
    function b64ToBuffer(b64) {{
      const bin = atob(b64);
      const buf = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      return buf.buffer;
    }}
    window._DOOM_WASM = b64ToBuffer("{wasm_b64}");
    window._DOOM_WAD  = b64ToBuffer("{wad_b64}");
  }})();
  </script>
  <script>
{patched_js}
  </script>
</body>
</html>"""

out = pathlib.Path("doom_single.html")
out.write_text(html)
mb = out.stat().st_size / 1024 / 1024
print(f"✅  doom_single.html  —  {mb:.1f} MB")
