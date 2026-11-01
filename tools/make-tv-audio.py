#!/usr/bin/env python3
"""Make the Apple TV copy of the voice-over: site/media/vo-tv/, every clip as stereo 48 kHz AAC.

The primer uses it only when opened with ?tv=1 (opt-in, 01-Nov-2026). Screen mirroring to an Apple TV popped and
rattled, likely when the stream switched between the clips' mixed formats (mono/stereo, 44.1/48 kHz). Converts from
the published files in site/media/vo/ and never touches them, so the normal link plays exactly what was approved.
Run after tools/build_vo.py (which calls it)."""
import pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / 'site/media/vo', ROOT / 'site/media/vo-tv'
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('*.m4a'):
    if not (SRC / old.name).exists(): old.unlink()
n = 0
for f in sorted(SRC.glob('*.m4a')):
    subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(f),
                    '-ac', '2', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', str(OUT / f.name)], check=True)
    n += 1
print(f'{n} clips -> site/media/vo-tv/ (stereo, 48 kHz)')
