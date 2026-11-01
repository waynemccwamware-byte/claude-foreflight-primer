#!/usr/bin/env python3
"""Join cards and filmed pages into the video, with the soundtrack from site/media/vo-tv/panel-*.m4a.
Usage: assemble.py WORKDIR OUT.mp4 scene ...   scene = title+chN:secs | chN:secs | card-NAME:secs"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
W = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); SCENES = sys.argv[3:]
VOTV, MUSIC = ROOT / 'site/media/vo-tv', ROOT / 'tools/music/audionautix-acoustic-guitar-1.mp3'
X264 = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30']
def ff(*a): subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', *a], check=True)
def lufs(f):
    e = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(f), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l.split()[1] for l in e.splitlines() if l.strip().startswith('I:')][-1])
MUS_GAIN = -31 - lufs(MUSIC)     # guitar alone under the cards, about -31 LUFS
music_at = [45.0]                # each card takes a fresh stretch of the guitar track

vids, auds = [], []
for i, sc in enumerate(SCENES):
    name, secs = sc.rsplit(':', 1); secs = float(secs)
    v, a = W / f'scene{i:02d}.tmp.mp4', W / f'scene{i:02d}.wav'
    fin = 0.6 if i == 0 else 0.35
    if name.startswith('card-'):
        ff('-framerate', '30', '-i', str(W / f'{name}.jpg'), '-vf',
           f'format=yuv420p,loop=-1:1,trim=duration={secs},fade=t=in:st=0:d={fin},fade=t=out:st={secs-0.45}:d=0.45', *X264, str(v))
        off = music_at[0]; music_at[0] += secs + 20
        ff('-ss', f'{off}', '-t', f'{secs}', '-i', str(MUSIC), '-af',
           f'volume={MUS_GAIN:.1f}dB,afade=t=in:d=1.0,afade=t=out:st={secs-1.6}:d=1.6,aresample=48000', '-ac', '2', str(a))
    else:
        title = name.startswith('title+'); pid = name.split('+')[-1]
        page = W / f'{pid}.mp4'
        if title:   # title card over the music lead-in, then crossfade into the page
            T = 3.0
            ff('-framerate', '30', '-i', str(W / 'card-title.jpg'), '-ss', f'{T}', '-i', str(page), '-filter_complex',
               f'[0:v]format=yuv420p,loop=-1:1,trim=duration={T+0.8},setpts=PTS-STARTPTS,fps=30[t];[1:v]setpts=PTS-STARTPTS,fps=30[p];'
               f'[t][p]xfade=transition=fade:duration=0.8:offset={T},trim=duration={secs},fade=t=in:st=0:d={fin},fade=t=out:st={secs-0.45}:d=0.45[o]',
               '-map', '[o]', *X264, str(v))
        else:
            ff('-i', str(page), '-vf', f'trim=duration={secs},fade=t=in:st=0:d={fin},fade=t=out:st={secs-0.45}:d=0.45', *X264, str(v))
        ff('-i', str(VOTV / f'panel-{pid}.m4a'), '-af',
           f'aresample=48000,apad,atrim=0:{secs},afade=t=out:st={secs-2.5}:d=2.5', '-ac', '2', str(a))
    v.rename(W / f'scene{i:02d}.mp4'); vids.append(W / f'scene{i:02d}.mp4'); auds.append(a)
    print('scene', i, name, secs)

(W / 'v.txt').write_text(''.join(f"file '{p}'\n" for p in vids))
ff('-f', 'concat', '-safe', '0', '-i', str(W / 'v.txt'), '-c', 'copy', str(W / 'video.tmp.mp4'))
ins = sum([['-i', str(a)] for a in auds], [])
ff(*ins, '-filter_complex', ''.join(f'[{i}:a]' for i in range(len(auds))) + f'concat=n={len(auds)}:v=0:a=1[o]', '-map', '[o]', str(W / 'audio.wav'))
tmp = OUT.with_suffix('.tmp.mp4')
ff('-i', str(W / 'video.tmp.mp4'), '-i', str(W / 'audio.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
   '-movflags', '+faststart', '-shortest', str(tmp))
tmp.rename(OUT); print('->', OUT)
