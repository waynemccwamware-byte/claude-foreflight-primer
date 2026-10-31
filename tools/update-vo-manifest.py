#!/usr/bin/env python3
"""Rewrite the VO_FILES list in site/index.html from the files in site/media/vo/. Run after adding recordings."""
import os, re, json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
files = sorted(f for f in os.listdir(root/'site/media/vo') if f.endswith(('.mp3', '.m4a')))
p = root/'site/index.html'; s = p.read_text()
s, n = re.subn(r'/\*VO-MANIFEST\*/.*?/\*END\*/', '/*VO-MANIFEST*/' + json.dumps(files) + '/*END*/', s, flags=re.S)
assert n == 1; p.write_text(s); print(len(files), 'voice files listed')
