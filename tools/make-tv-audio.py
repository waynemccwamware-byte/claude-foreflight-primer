#!/usr/bin/env python3
"""Make the Apple TV audio: one continuous file per page, site/media/vo-tv/panel-<id>.m4a, stereo 48 kHz AAC.

The primer uses these only when opened with ?tv=1 (opt-in, 01-Nov-2026). Screen mirroring to an Apple TV popped and
rattled between clips, so on the TV link each page plays a single file: its clips in the page's play order (SEQ in
site/index.html), joined with a short gap like the normal chain's. Built from the published clips in site/media/vo/,
which it never changes, so the normal link plays exactly what was approved.
Also writes /*VO-TV*/{id: seconds}/*END*/ into the page: when the page's last voice ends inside its file (the music
pages run on past it), which is when Next turns amber.
Run after tools/build_vo.py (which calls it)."""
import json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE, SRC, OUT = ROOT / 'site/index.html', ROOT / 'site/media/vo', ROOT / 'site/media/vo-tv'
GAP = 0.15   # seconds between clips, about what the normal chain's hand-off takes

def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                capture_output=True, text=True).stdout)

html = PAGE.read_text()
seq_src = re.search(r'const SEQ = \{(.*?)\n  \};', html, re.S).group(1)
SEQ = {k: re.findall(r"'([^']+)'", v) for k, v in re.findall(r"'([\w-]+)':\s*\[([^\]]*)\]", seq_src)}
voice_end = json.loads(re.search(r'/\*VO-VOICE-END\*/(.*?)/\*END\*/', html, re.S).group(1))

OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('*.m4a'): old.unlink()          # earlier per-clip copies are no longer used
ready = {}
for narr in sorted(p.stem for p in SRC.glob('ch*.m4a')):
    steps = SEQ.get(narr, ['narr'])
    files = [SRC / ((narr if s == 'narr' else s) + '.m4a') for s in steps if not s.startswith('wait:')]
    if not all(f.exists() for f in files): print('skip', narr, '(a clip is missing)'); continue
    ins, chain, t, last_voice = [], [], 0.0, 0.0
    for i, f in enumerate(files):
        ins += ['-i', str(f)]
        pad = GAP if i < len(files) - 1 else 0
        chain.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,apad=pad_dur={pad}[a{i}]')
        d = dur(f)
        last_voice = t + voice_end.get(f.stem, d)    # music pages: the voice ends before the file does
        t += d + pad
    fc = ';'.join(chain) + ';' + ''.join(f'[a{i}]' for i in range(len(files))) + f'concat=n={len(files)}:v=0:a=1[o]'
    out = OUT / f'panel-{narr}.m4a'
    subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', *ins, '-filter_complex', fc,
                    '-map', '[o]', '-ar', '48000', '-ac', '2', '-c:a', 'aac', '-b:a', '160k', str(out)], check=True)
    ready[narr] = round(last_voice, 2)
html = re.sub(r'/\*VO-TV\*/.*?/\*END\*/', lambda _: '/*VO-TV*/' + json.dumps(ready) + '/*END*/', html, flags=re.S)
PAGE.write_text(html)
print(f'{len(ready)} page files -> site/media/vo-tv/ (stereo, 48 kHz)')
