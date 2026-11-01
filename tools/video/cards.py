#!/usr/bin/env python3
"""Title, primer-link and end cards for the YouTube video, as 1920x1080 JPEGs (rendered from HTML with Playwright)."""
import asyncio, base64, io, sys, pathlib
import qrcode
from playwright.async_api import async_playwright
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5   # 1.5 = 1080p, 3 = 4K
OUT = pathlib.Path(sys.argv[1]); FONTCSS = pathlib.Path(sys.argv[2]).read_text() if len(sys.argv) > 2 else ''
URL = 'geezer-geek-pilot-control-panel.netlify.app'   # the Control Panel; the primer is its top card

def qr_svg():
    q = qrcode.QRCode(border=0, box_size=10); q.add_data('https://' + URL + '/'); q.make(fit=True)
    m = q.get_matrix(); n = len(m)
    cells = ''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="-2 -2 {n+4} {n+4}" shape-rendering="crispEdges"><rect x="-2" y="-2" width="{n+4}" height="{n+4}" fill="#e7e4dc"/><g fill="#10141a">{cells}</g></svg>'

BASE = """<!doctype html><meta charset="utf-8"><style>%s
:root{--bg:#10141a;--panel:#1b222c;--bezel:#2a323f;--amber:#f5a623;--text:#e7e4dc;--muted:#8b93a1;--teal:#3fa7a0}
*{box-sizing:border-box} html,body{margin:0;width:1280px;height:720px;background:var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif;overflow:hidden}
body{background:radial-gradient(1200px 600px at 50%% 40%%,#18202a,#10141a)}
body::after{content:"";position:absolute;inset:0;opacity:.06;pointer-events:none;   /* fine grain: no banding in the glow */
  background-image:url("data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%%3E%%3Cfilter id='n'%%3E%%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%%3E%%3C/filter%%3E%%3Crect width='160' height='160' filter='url(%%23n)'/%%3E%%3C/svg%%3E")}
.wrap{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 110px}
.k{font:500 15px 'IBM Plex Mono',monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--amber);margin-bottom:18px}
h1{font-size:64px;font-weight:600;margin:0 0 18px;letter-spacing:.005em}
p{font-size:26px;line-height:1.45;color:var(--muted);margin:0;max-width:900px}
.by{position:absolute;left:110px;bottom:56px;font:500 16px 'IBM Plex Mono',monospace;color:var(--muted);letter-spacing:.06em}
.row{display:flex;align-items:center;gap:64px}
.url{font:600 27px 'IBM Plex Mono',monospace;white-space:nowrap;color:var(--amber);margin:22px 0 22px;letter-spacing:.01em}
.qr{width:250px;height:250px;flex:0 0 250px;padding:0;border-radius:14px;overflow:hidden;box-shadow:0 0 0 2px var(--bezel)}
.qr svg{display:block;width:100%%;height:100%%}
.qrl{font:500 14px 'IBM Plex Mono',monospace;color:var(--muted);text-align:center;margin-top:12px;letter-spacing:.08em}
.small{font-size:16px;color:var(--muted);position:absolute;left:110px;right:110px;bottom:44px}
.line{width:120px;height:4px;background:var(--amber);border-radius:2px;margin:6px 0 26px}
</style>""" % FONTCSS

CARDS = {
 'title': """<div class="wrap"><div class="k">GeezerGeek Pilot</div><h1>Claude + ForeFlight Primer</h1><div class="line"></div>
  <p>Why and how to connect Claude to your ForeFlight account, and one real trip planned in a single chat.</p></div>
  <div class="by">Narrated by Wayne McClelland</div>""",
 'link': """<div class="wrap"><div class="row"><div style="flex:1"><div class="k">Try it yourself</div><h1 style="font-size:54px">The interactive primer</h1>
  <p style="color:var(--text)">On GeezerGeek Pilot Apps, the first card:</p><div class="url">%s</div><p>Go at your own pace, replay each chat, and copy the prompts straight into Claude.</p></div>
  <div><div class="qr">%s</div><div class="qrl">SCAN TO OPEN</div></div></div></div>""",
 'end': """<div class="wrap"><div class="row"><div style="flex:1"><div class="k">Your turn</div><h1 style="font-size:54px">Open the primer, then connect ForeFlight</h1>
  <p style="color:var(--text)">The primer and more pilot tools, on GeezerGeek Pilot Apps:</p><div class="url">%s</div><p>Then ask Claude about your own logbook, or your next trip.</p></div>
  <div><div class="qr">%s</div><div class="qrl">SCAN TO OPEN</div></div></div></div>
  <div class="small">Music: "Acoustic Guitar 1" by Audionautix, licensed CC BY 4.0. Not affiliated with ForeFlight or Anthropic. Not for flight; verify everything with official sources.</div>""",
}

async def main():
    q = qr_svg()
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=SCALE)
        for name, body in CARDS.items():
            html = BASE + (body % (URL, q) if '%s' in body else body)
            await pg.set_content(html); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(OUT / f'card-{name}.jpg'), type='jpeg', quality=92)
        await b.close()
asyncio.run(main())
