#!/usr/bin/env python3
"""Build the primer's voice-over files from the raw recordings (needs ffmpeg and numpy; run in a Claude session).

tools/vo-raw/  raw recordings, not published:
  ch*.m4a|mp3|webm Wayne narrating -> head/tail silence trimmed to 0.4 s, leveled to -21 LUFS, AAC      -> copied as is (clean, full volume)
  claude-*.m4a     Claude (Reed) bubble -> ding + bubble voice + send
  wayne-*.m4a|mp3  Wayne's typed prompt -> ding + bubble voice + send
Bubble voice: 80% of the clean level, 300-3400 Hz band, light compression, faint pink-noise bed (approved 31-Oct-2026).
Ding: the ATC Chair-Fly Trainer's two notes (880 Hz, then 1318.5 Hz, sine). Send: a Return-key click (down + up), half volume.
Writes site/media/vo/<name>.m4a, then refreshes the VO_FILES list in site/index.html.
"""
import os, subprocess, sys, tempfile, wave, pathlib
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / 'tools/vo-raw', pathlib.Path(os.environ.get('VO_OUT', ROOT / 'site/media/vo'))   # VO_OUT: preview elsewhere
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
    # Send: a Return-key press -- key-down click, softer key-up click 85 ms later (approved 31-Oct-2026, half volume)
    rng = np.random.default_rng(3)
    lp = lambda x, k: np.convolve(x, np.ones(k) / k, mode='same')
    def click(peak, thump, thump_amp, dur=0.035):
        n = int(SR * dur); t = np.arange(n) / SR
        noise = rng.standard_normal(n)
        bp = lp(noise, int(SR / 6000)) - lp(noise, int(SR / 1500))
        x = bp * np.exp(-t / 0.006)
        return x / np.abs(x).max() * peak + np.sin(2 * np.pi * thump * t) * np.exp(-t / 0.012) * thump_amp
    send = np.zeros(int(SR * 0.3))
    send = place(send, click(0.5, 180, 0.35), 0.10)
    send = place(send, click(0.28, 240, 0.15), 0.185)
    send *= 0.35
    save(tmp / 'send.wav', send)

def ff(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args], check=True)

def codec(src):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', str(src)], capture_output=True, text=True)
    return r.stdout.strip()

RNN = ROOT / 'tools/models/std.rnnn'   # RNNoise model (github.com/richardpl/arnndn-models); 'sh' ate speech on quiet takes

def gaps_db(src):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', str(src), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); n = 800
    fr = x[:len(x) // n * n].reshape(-1, n)
    return float(np.percentile(20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9), 10))

def denoise(src, tmp):
    """Wayne's takes: RNNoise after raising the take to -20 LUFS (RNNoise misreads quiet input).
    Skipped when the pauses are already clean (it clipped word ends on short, clean takes)."""
    g = -20 - lufs(src)
    if gaps_db(src) + g < -66: return src
    out = tmp / (src.stem + '-dn.wav')
    ff('-i', str(src), '-af', f'aresample=48000,volume={g:.2f}dB,highpass=f=70,arnndn=m={RNN}', str(out))
    return out

NARR_LUFS, PAD = -21.0, 0.4   # narration sits ~2 dB above the bubble clips; keep 0.4 s of quiet at each end

def trim_filter(src, pad):
    """atrim filter keeping `pad` s of quiet around the speech. Speech = a run of >= 250 ms above (loud - 32 dB),
    so a knock or click before the first word or after the last one is cut off."""
    raw = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', str(src), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); hop = 800; dur = len(x) / 16000
    r = 20 * np.log10(np.sqrt((x[:len(x) // hop * hop].reshape(-1, hop) ** 2).mean(1)) + 1e-9)
    act = r > np.percentile(r, 95) - 32
    runs, k = [], 0
    while k < len(act):
        if act[k]:
            j = k
            while j < len(act) and act[j]: j += 1
            runs.append((k, j)); k = j
        else: k += 1
    long = [(a, z) for a, z in runs if z - a >= 5] or runs or [(0, len(act))]
    a = long[0][0] * hop / 16000
    z = long[-1][1] * hop / 16000
    s0, s1 = a, z
    a, z = max(0.0, a - pad), min(dur, z + pad)
    # the pads are true silence: fade in over the last 80 ms before the first word, out over 200 ms after the last
    fi = max(0.0, s0 - a - 0.08); fo = min(z - a, s1 - a + 0.05)
    return (f'atrim={a:.3f}:{z:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=mono,'
            f'afade=t=in:st={fi:.3f}:d=0.08,afade=t=out:st={fo:.3f}:d=0.2')

# Gentle gate for narration pauses (applied at -20 LUFS): leftover bumps under -38 dBFS are pulled down up to 15 dB.
GATE = 'agate=threshold=0.0126:ratio=3:range=0.178:attack=5:release=250:knee=2'

def narration(src, dst):
    """Trim long head/tail silence to PAD, then level to NARR_LUFS (two-pass loudnorm), AAC .m4a."""
    import json
    trim = f'{trim_filter(src, PAD)},volume={-20 - lufs(src):.2f}dB,{GATE}'
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
       f'[0:a]{trim_filter(src, 0.15)},aresample=44100,volume={gain:.2f}dB,highpass=f=300,lowpass=f=3400,'
       'acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=5.9dB,volume=0.8[v];'
       '[1:a]highpass=f=200,lowpass=f=5000[n];[v][n]amix=inputs=2:duration=first:normalize=0[o]', '-map', '[o]', str(v))
    ff('-i', str(tmp / 'ding.wav'), '-i', str(v), '-i', str(tmp / 'send.wav'), '-filter_complex',
       '[0:a][1:a][2:a]concat=n=3:v=0:a=1[o]', '-map', '[o]', '-c:a', 'aac', '-b:a', '96k', str(dst))

# Music bed under the Start and Wrap-up narration (approved 31-Oct-2026).
# "Acoustic Guitar 1" by Audionautix, CC BY 4.0 -- the credit must stay on the page (Wrap-up + fine print).
MUSIC = ROOT / 'tools/music/audionautix-acoustic-guitar-1.mp3'
MUSIC_ON = ('ch0', 'ch7')
MUSIC_PRE, MUSIC_TAIL = 3.0, 5.0     # music starts 3 s before the first word; runs 5 s past the narration, fading to silence
MUSIC_OPEN, MUSIC_DUCK = -37.0, -45.0  # LUFS of the music alone: in pauses / under the voice ("low")

def pcm(src, ch):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', str(src), '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()

def add_music(voice_m4a, tmp):
    v = pcm(voice_m4a, 1)[:, 0]
    pre = MUSIC_PRE - PAD                       # the narration file already starts with PAD of quiet
    i0 = int(SR * pre); n = i0 + len(v) + int(SR * MUSIC_TAIL)
    m = pcm(MUSIC, 2)[:n]
    if len(m) < n: m = np.concatenate([m, np.zeros((n - len(m), 2))])
    vv = np.zeros(n); vv[i0:i0 + len(v)] = v
    hop = int(SR * 0.02); fr = np.pad(vv, (0, (-n) % hop)).reshape(-1, hop)
    act = (20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9) > -45).astype(float)
    sm = np.zeros_like(act); s = 0.0
    for k, a in enumerate(act):                 # duck: 80 ms down, 700 ms back up
        s += (a - s) * min(1, 0.02 / (0.08 if a > s else 0.7)); sm[k] = s
    env = np.repeat(sm, hop)[:n]
    ml = lufs(MUSIC)
    g = 10 ** ((MUSIC_OPEN - ml) / 20) + (10 ** ((MUSIC_DUCK - ml) / 20) - 10 ** ((MUSIC_OPEN - ml) / 20)) * env
    t = np.arange(n) / SR
    fin = np.clip(t / 0.8, 0, 1)
    f0 = (i0 + len(v)) / SR - PAD               # last word
    fout = np.cos(np.clip((t - f0) / (t[-1] - f0), 0, 1) * np.pi / 2) ** 2
    out = m * (g * fin * fout)[:, None] + vv[:, None]
    out *= min(1.0, 0.89 / np.abs(out).max())
    w = tmp / 'music-mix.wav'
    with wave.open(str(w), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((out * 32767).astype('<i2').tobytes())
    ff('-i', str(w), '-c:a', 'aac', '-b:a', '160k', str(voice_m4a))

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
                bubble(denoise(src, tmp) if name.startswith('wayne-') else src, OUT / (name + '.m4a'), tmp); print('bubble ', name)
            else:
                narration(denoise(src, tmp), OUT / (name + '.m4a'))
                if name in MUSIC_ON: add_music(OUT / (name + '.m4a'), tmp)
                print('narration', name)
    if 'VO_OUT' not in os.environ:
        subprocess.run([sys.executable, str(ROOT / 'tools/update-vo-manifest.py')], check=True)

if __name__ == '__main__':
    main()
