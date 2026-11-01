#!/usr/bin/env python3
"""For each primer page, find the column width that lets it fill the 16:9 video frame at the largest size, measured
once the page is fully built, and write it into site/index.html as /*VFIT*/{id: [width, scale]}/*END*/.
Serve site/ on :8767 first.  Usage: fit.py FONTCSS"""
import asyncio, json, pathlib, re, sys
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]; PAGE = ROOT / 'site/index.html'
FONTCSS = pathlib.Path(sys.argv[1]).read_text()
html = PAGE.read_text(); ready = json.loads(re.search(r'/\*VO-TV\*/(.*?)/\*END\*/', html, re.S).group(1))
HASH = {'ch0': 'ch0', 'ch1': 'ch1', 'ch2': 'ch2', 'ch6': 'ch6', 'ch7': 'ch7'}
for c, n in ((3, 5), (4, 2), (5, 5)):
    for i in range(n): HASH[f'ch{c}-{i+1}'] = f'ch{c}-{i}'
FW, FH, MAXS = 1260, 712, 1.6
WIDTHS = [1240, 1160, 1080, 1000, 940, 880, 820, 760, 700]

async def measure(ctx, pid):
    pg = await ctx.new_page()
    await pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    await pg.route('**/geezer-geek-pilot-control-panel.netlify.app/**', lambda r: r.abort())   # the map's frame has a fixed height
    await pg.goto(f'http://localhost:8767/?video=1#{HASH[pid]}'); await pg.add_style_tag(content=FONTCSS)
    await pg.evaluate("document.getElementById('startQuiet').click()")
    await pg.wait_for_timeout(int((ready.get(pid, 15) + 3) * 1000))
    best = None
    for w in WIDTHS:
        h = await pg.evaluate(f"(()=>{{const r=document.querySelector('.rig');r.style.transform='none';r.style.maxWidth='{w}px';return r.scrollHeight}})()")
        s = min(MAXS, FW / w, (FH - 8) / (h + 8))
        if best is None or s > best[1] + 0.01: best = (w, round(s, 3), h)
    await pg.close()
    return pid, best

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 720})
        res = await asyncio.gather(*[measure(ctx, pid) for pid in HASH])
        await b.close()
    # too tall for one frame at a readable size: show it at full size and pan down it during the narration
    fit = {pid: ([w, s] if s >= 0.8 else [1000, 1.0, 'pan']) for pid, (w, s, h) in sorted(res)}
    for pid, (w, s, h) in sorted(res): print(f'{pid:6s} width {w:5d}  scale {s:.2f}  (height {h})')
    t = PAGE.read_text()
    PAGE.write_text(re.sub(r'/\*VFIT\*/.*?/\*END\*/', lambda _: '/*VFIT*/' + json.dumps(fit) + '/*END*/', t, flags=re.S))
asyncio.run(main())
