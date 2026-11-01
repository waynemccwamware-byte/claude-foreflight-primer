#!/usr/bin/env python3
"""Captions (.srt) and YouTube description with chapters for the video, from the same timing the video uses.
Usage: captions.py OUTDIR   (reads tools/video/scenes.txt, site/index.html, tools/vo-script.md, site/media/vo/)"""
import json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = pathlib.Path(sys.argv[1])
html = (ROOT / 'site/index.html').read_text(); md = (ROOT / 'tools/vo-script.md').read_text()
VO = ROOT / 'site/media/vo'; GAP, PAD = 0.15, 0.4
MUSIC_PRE = {'ch0': 3.0, 'ch1': 0.8, 'ch7': 5.2}
voice_end = json.loads(re.search(r'/\*VO-VOICE-END\*/(.*?)/\*END\*/', html, re.S).group(1))
SEQ = {k: re.findall(r"'([^']+)'", v) for k, v in re.findall(r"'([\w-]+)':\s*\[([^\]]*)\]", re.search(r'const SEQ = \{(.*?)\n  \};', html, re.S).group(1))}
TEXT = {m.group(1).rsplit('.', 1)[0]: ' '.join(m.group(2).split()) for m in re.finditer(r'^### `([^`]+)` — .+?\n\n(.+?)(?=\n\n(?:###|---|##)|\Z)', md, re.S | re.M)}
for k, v in re.findall(r"^- `(claude-[\w-]+)` — (.+)$", md, re.M): TEXT[k] = v.strip()
def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)
def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{s:06.3f}'.replace('.', ',')
def chunks(text, n=84):
    out, cur = [], ''
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > n: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    return out + ([cur] if cur else [])
def lines2(c):   # break a chunk into two balanced lines
    if len(c) <= 42: return c
    mid = len(c) // 2; i = c.rfind(' ', 0, mid + 8); i = i if i > 0 else mid
    return c[:i] + '\n' + c[i + 1:]

scenes = [l.strip() for l in (ROOT / 'tools/video/scenes.txt').read_text().splitlines() if l.strip() and not l.startswith('#')]
CHAP = {'ch0': 'Start', 'ch1': 'Why connect', 'ch2': 'Before you start', 'ch3-1': 'Connect, in five steps', 'ch4-1': 'Your logbook, in a question',
        'ch5-1': 'One trip, start to finish', 'ch6': 'Good habits', 'ch7': 'Wrap-up'}
subs, chapters, t0 = [], [], 0.0
for sc in scenes:
    name, secs = sc.rsplit(':', 1); secs = float(secs); pid = name.split('+')[-1]
    if pid in CHAP: chapters.append((t0, CHAP[pid]))
    if not name.startswith('card-'):
        t = t0
        for step in SEQ.get(pid, ['narr']):
            clip = pid if step == 'narr' else step
            d = dur(VO / f'{clip}.m4a')
            if step == 'narr':
                a = t + MUSIC_PRE.get(pid, PAD); z = t + voice_end.get(pid, d - PAD); text = TEXT.get(pid, '')
            else:
                a, z = t + 0.6, t + d - 0.45
                text = ('Claude: ' if clip.startswith('claude') else 'To Claude: ') + TEXT.get(clip, '')
            cs = chunks(text); total = sum(len(c) for c in cs) or 1; u = a
            for c in cs:
                v = u + (z - a) * len(c) / total
                subs.append((u, min(v, t0 + secs), lines2(c))); u = v
            t += d + GAP
    t0 += secs
srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n' for i, (a, b, c) in enumerate(subs, 1))
(OUT / 'claude-foreflight-primer.en.srt').write_text(srt)
mmss = lambda t: f'{int(t // 60)}:{int(t % 60):02d}'
desc = f"""How to connect Claude to your ForeFlight account, and what that pairing can do: summarize your logbook, map everywhere you've flown, and research, plan and build a real trip (Santa Barbara to the Oregon coast) in a single Claude chat.

▶ Try the interactive primer (go at your own pace, replay each chat, copy the prompts into Claude):
https://geezer-geek-pilot-control-panel.netlify.app/
It's the first card on GeezerGeek Pilot Apps. Direct link: https://claude-foreflight-primer.netlify.app/

Chapters
{chr(10).join(f'{mmss(t)} {n}' for t, n in chapters)}
{mmss(t0 - 9)} Try it yourself

Music: "Acoustic Guitar 1" by Audionautix is licensed under a Creative Commons Attribution 4.0 license. https://creativecommons.org/licenses/by/4.0/

Examples use my own ForeFlight data (logbook totals lightly fictionalized) and a real Claude chat from 13-Oct-2026, trimmed. Not affiliated with ForeFlight or Anthropic. Not for flight; verify everything with official sources.
"""
(OUT / 'youtube-description.txt').write_text(desc)
print(f'{len(subs)} captions, {len(chapters)} chapters, {mmss(t0)} total'); print(desc)
