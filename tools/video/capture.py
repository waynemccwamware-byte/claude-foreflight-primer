#!/usr/bin/env python3
"""Film primer pages for the YouTube video: each page in ?video=1 mode, muted, 1920x1080, via Chromium's screencast.
Writes <out>/<id>.mp4 (30 fps) holding each page for <seconds>.  Usage: capture.py OUT FONTCSS id:seconds ..."""
import asyncio, base64, sys, pathlib, subprocess, time
from playwright.async_api import async_playwright
OUT = pathlib.Path(sys.argv[1]); FONTCSS = pathlib.Path(sys.argv[2]).read_text()
import os
SCALE = float(os.environ.get('VSCALE', '1.5'))          # 1.5 = 1920x1080, 3 = 3840x2160 (4K)
W, H = int(1280 * SCALE), int(720 * SCALE)
JOBS = [(a.split(':')[0], float(a.split(':')[1])) for a in sys.argv[3:]]
BASE = 'http://localhost:8767/?video=1'
# primer hash for each page id (chapter index, 0-based step)
HASH = {'ch0': 'ch0', 'ch1': 'ch1', 'ch2': 'ch2', 'ch6': 'ch6', 'ch7': 'ch7'}
for c, n in ((3, 5), (4, 2), (5, 5)):
    for i in range(n): HASH[f'ch{c}-{i+1}'] = f'ch{c}-{i}'

async def film(ctx, pid, secs):
    pg = await ctx.new_page()
    await pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    await pg.goto(f'{BASE}#{HASH[pid]}'); await pg.add_style_tag(content=FONTCSS); await pg.wait_for_timeout(600)
    cdp = await ctx.new_cdp_session(pg); frames = []
    def on_frame(ev):
        frames.append((ev['metadata']['timestamp'], ev['data']))
        asyncio.ensure_future(cdp.send('Page.screencastFrameAck', {'sessionId': ev['sessionId']}))
    cdp.on('Page.screencastFrame', on_frame)
    await cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 92, 'maxWidth': W, 'maxHeight': H, 'everyNthFrame': 1})
    await pg.wait_for_timeout(300)
    t0 = time.time()
    await pg.evaluate("document.getElementById('startQuiet').click()")   # starts the page's animations
    await pg.wait_for_timeout(int(secs * 1000) + 300)
    await cdp.send('Page.stopScreencast'); await pg.close()
    # frames -> image sequence with durations -> constant 30 fps
    d = OUT / f'frames-{pid}'; d.mkdir(exist_ok=True)
    for f in d.glob('*'): f.unlink()
    kept = [(t, b) for t, b in frames if t >= t0 - 0.05]
    before = [(t, b) for t, b in frames if t < t0 - 0.05]
    if before: kept = [(t0, before[-1][1])] + kept     # what was on screen at the click
    lst = []
    for i, (t, b) in enumerate(kept):
        p = d / f'{i:05d}.jpg'; p.write_bytes(base64.b64decode(b))
        nxt = kept[i + 1][0] if i + 1 < len(kept) else t0 + secs
        lst.append(f"file '{p}'\nduration {max(0.001, min(nxt, t0 + secs) - max(t, t0)):.4f}")
    lst.append(f"file '{d / f'{len(kept)-1:05d}.jpg'}'")
    (d / 'list.txt').write_text('\n'.join(lst) + '\n')
    tmp = OUT / f'{pid}.tmp.mp4'
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(d / 'list.txt'),
                    '-vf', f'scale={W}:{H}:flags=lanczos,fps=30,format=yuv420p', '-t', f'{secs:.3f}',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-r', '30', str(tmp)], check=True)
    tmp.rename(OUT / f'{pid}.mp4')
    print(pid, f'{secs:.1f}s', len(kept), 'frames captured', f'({len(kept)/secs:.1f}/s)')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=SCALE)
        cp = pathlib.Path(sys.argv[0]).resolve().parents[3] / 'geezer-geek-pilot-control-panel/site'
        if cp.exists():   # serve the Airports Visited map from a local Control Panel clone (same code as the live site)
            async def serve(route):
                path = route.request.url.split('netlify.app/')[1].split('?')[0]
                f = cp / (path + 'index.html' if path.endswith('/') or path == '' else path)
                await (route.fulfill(path=str(f)) if f.exists() else route.continue_())
            await ctx.route('https://geezer-geek-pilot-control-panel.netlify.app/**', serve)
        if any(pid == 'ch4-2' for pid, _ in JOBS):   # warm the cache so the live map loads quickly
            w = await ctx.new_page(); await w.goto('https://geezer-geek-pilot-control-panel.netlify.app/airports/?embed=1')
            await w.wait_for_timeout(15000); await w.close()
        for pid, secs in JOBS: await film(ctx, pid, secs)
        await b.close()
asyncio.run(main())
