# The CRE Grind

A weekly two-host podcast on commercial real estate: one topic per episode, 30–50 minutes. Site: https://podcast.houzrealestate.com/ · Feed: `/feed.xml`

## How the repo is organized

```
episodes.json                 ← single source of truth: site info, market ticker, upcoming topics, every episode
episodes/eNN-<slug>/
    notes.md                  ← show notes (takeaways, worked example, sources), rendered on the episode page
    script.txt                ← the two-host script the audio was rendered from
tools/
    build.py                  ← generates docs/ from the above (pip install markdown pillow)
    render.py                 ← script → MP3 with Kokoro TTS
    style.css, player.js      ← site look and player behavior
docs/                         ← GENERATED website served by GitHub Pages (never edit by hand)
ROADMAP.md                    ← season plan and topic queue
```

**Audio** lives in `docs/audio/cre-grind-eNN.mp3`, served by GitHub Pages, at 64 kbps mono (about 17 MB per 35 minutes). GitHub Pages sites cap at about 1 GB, which is roughly 55 episodes. When `docs/` approaches about 900 MB, move older seasons' MP3s to a new repo (e.g. `cre-grind-audio-s1`) with Pages on, and point those episodes' URLs there. Check the size with `du -sh docs`.

## Publishing a new episode

1. Render the MP3 with `tools/render.py`, then re-encode for the web:
   `ffmpeg -i in.mp3 -ac 1 -ar 24000 -b:a 64k cre-grind-eNN.mp3`
2. Copy it to `docs/audio/cre-grind-eNN.mp3`.
3. Add `episodes/eNN-<slug>/notes.md` and `script.txt`.
4. Add the episode to `episodes.json` (number, slug, title, headline, summary, type, date, audio_file, duration_sec from ffprobe, size_bytes, interview_line, panel, stats). Refresh `ticker` with this week's figures and remove it from `upcoming`, adding the next topics.
5. `python3 tools/build.py`, then commit and push. GitHub Pages redeploys automatically.
