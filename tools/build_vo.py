#!/usr/bin/env python3
"""Build the primer's voice-over files from the raw recordings (needs ffmpeg and numpy; run in a Claude session).

tools/vo-raw/  raw recordings, not published:
  ch*.m4a|mp3|webm Wayne narrating -> head/tail silence trimmed to 0.4 s, leveled to -21 LUFS, AAC      -> copied as is (clean, full volume)
  claude-*.m4a     Claude (Reed) bubble -> ding + bubble voice + send
  wayne-*.m4a|mp3  Wayne's typed prompt -> ding + bubble voice + send
Bubble voice: 80% of the clean level, 300-3400 Hz band, light compression, faint pink-noise bed (approved 31-Oct-2026).
Ding: the ATC Chair-Fly Trainer's two notes (880 Hz, then 1318.5 Hz, sine). Send: a short rising swoosh + blip.
Writes site/media/vo/<name>.m4a, then refreshes the VO_FILES list in site/index.html.
"""
import os, subprocess, sys, tempfile, wave, pathlib
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / 'tools/vo-raw', ROOT / 'site/media/vo'
SR = 44100

def tone(f0, f1, dur, kind, peak):
    t = np.arange(int(SR * (dur + 0.02))) / SR
    f = f0 * (f1 / f0) ** np.clip(t / dur, 0, 1) if f1 != f0 else np.full_like(t, f0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(ph) if kind == 'sine' else (2 / np.pi) * np.arcsin(np.sin(ph))
    env = np.where(t < 0.02, 1e-4 * (peak / 1e-4) ** (t / 0.02), peak * (1e-4 / peak) ** np.clip((t - 0.02) / (dur - 0.02), 0, 1))
    env[t > dur] = 0
    return w * env

def place(buf, sig, at):
    i = int(at * SR)
    if len(buf) < i + len(sig): buf = np.concatenate([buf, np.zeros(i + len(sig) - len(buf))])
    buf[i:i + len(sig)] += sig
    return buf

def save(path, x):
    d = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())

def make_fx(tmp):
    ding = place(place(np.zeros(0), tone(880, 880, 0.12, 'sine', 0.3), 0), tone(1318.5, 1318.5, 0.18, 'sine', 0.3), 0.09)
    save(tmp / 'ding.wav', np.concatenate([ding, np.zeros(int(SR * 0.25))]))
    n = int(SR * 0.32); t = np.arange(n) / SR
    noise = np.random.default_rng(7).standard_normal(n)
    lp = lambda x, k: np.convolve(x, np.ones(k) / k, mode='same')
    sw = (lp(noise, 18) - lp(noise, 60)) * np.sin(np.pi * np.clip(t / 0.32, 0, 1)) ** 2 * 0.28
    send = place(place(np.zeros(int(SR * 0.15)), sw, 0.15), tone(1100, 1760, 0.12, 'sine', 0.18), 0.30)
    save(tmp / 'send.wav', send)

def ff(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args], check=True)

def codec(src):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', str(src)], capture_output=True, text=True)
    return r.stdout.strip()

NARR_LUFS, PAD = -21.0, 0.4   # narration sits ~2 dB above the bubble clips; keep 0.4 s of quiet at each end

def narration(src, dst):
    """Trim long head/tail silence to PAD, then level to NARR_LUFS (two-pass loudnorm), AAC .m4a."""
    import json, re
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-af', 'silencedetect=n=-45dB:d=0.25', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    dur = float(re.search(r'Duration: (\d+):(\d+):([\d.]+)', log).groups()[2]) + 60 * int(re.search(r'Duration: (\d+):(\d+)', log).group(2))
    starts = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    a = ends[0] if starts and starts[0] <= 0.01 and ends else 0.0
    z = starts[-1] if starts and (len(starts) > len(ends) or ends[-1] >= dur - 0.05) else dur
    a, z = max(0.0, a - PAD), min(dur, z + PAD)
    trim = f'atrim={a:.3f}:{z:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=mono'
    ln = f'loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11'
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-af', f'{trim},{ln}:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    ff('-i', str(src), '-af', f"{trim},{ln}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
       f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000",
       '-c:a', 'aac', '-b:a', '128k', str(dst))

BUBBLE_IN_LUFS = -21.8   # the Reed recordings' level, which the bubble chain below was tuned on

def lufs(src):
    import re
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1])

def bubble(src, dst, tmp):
    v = tmp / 'v.wav'
    gain = BUBBLE_IN_LUFS - lufs(src)   # bring every raw take (Wayne or Reed) to the same input level first
    ff('-i', str(src), '-f', 'lavfi', '-i', 'anoisesrc=color=pink:amplitude=0.012:sample_rate=44100', '-filter_complex',
       f'[0:a]aresample=44100,aformat=channel_layouts=mono,volume={gain:.2f}dB,highpass=f=300,lowpass=f=3400,'
       'acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=5.9dB,volume=0.8[v];'
       '[1:a]highpass=f=200,lowpass=f=5000[n];[v][n]amix=inputs=2:duration=first:normalize=0[o]', '-map', '[o]', str(v))
    ff('-i', str(tmp / 'ding.wav'), '-i', str(v), '-i', str(tmp / 'send.wav'), '-filter_complex',
       '[0:a][1:a][2:a]concat=n=3:v=0:a=1[o]', '-map', '[o]', '-c:a', 'aac', '-b:a', '96k', str(dst))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td); make_fx(tmp)
        for fx in ('ding', 'send'):   # also published on their own, for bubbles read by the browser voice
            ff('-i', str(tmp / (fx + '.wav')), '-c:a', 'aac', '-b:a', '96k', str(OUT / (fx + '.m4a')))
        for src in sorted(RAW.iterdir()):
            if src.suffix.lower() not in ('.m4a', '.mp3', '.wav', '.aiff', '.webm', '.ogg'): continue
            name = src.stem
            if name.startswith(('claude-', 'wayne-')):
                bubble(src, OUT / (name + '.m4a'), tmp); print('bubble ', name)
            else:
                narration(src, OUT / (name + '.m4a'))
                print('narration', name)
    subprocess.run([sys.executable, str(ROOT / 'tools/update-vo-manifest.py')], check=True)

if __name__ == '__main__':
    main()
