# Claude + ForeFlight Primer

GeezerGeek Pilot app: why and how to connect Claude to a ForeFlight account, with a real trip and logbook as examples.

- Live: https://claude-foreflight-primer.netlify.app/ (after the Netlify site is created)
- `site/index.html` — the whole page (CSS/JS inline). Footer blocks are written by the master in the
  Control Panel repo (`tools/ggp-footer`); never edit them here.
- `tools/facts.json` — snapshot the monthly update task compares against (not published).
- Script & storyboard: Claude Doc "Claude + ForeFlight Primer — Script & Storyboard".

## YouTube video (tools/video/)

`?video=1` is a recording-only layout (16:9, no buttons, captions or footer; pages scale to fit; the map is cued from the clock).
1. `python3 tools/video/cards.py WORK FONTCSS`: title, primer-link and end cards.
2. `python3 tools/video/capture.py WORK FONTCSS ch0:27 ch1:19 …`: films each page (serve `site/` on :8767 first).
3. `python3 tools/video/assemble.py WORK out.mp4 "title+ch0:27" "ch1:19" "card-link:7" …`: joins scenes; sound from `site/media/vo-tv/`.
