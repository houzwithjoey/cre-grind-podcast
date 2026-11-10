# The CRE Grind

A weekly two-host podcast on commercial real estate: one topic per episode, 30–50 minutes. Site: https://houzwithjoey.github.io/cre-grind-podcast/ · Feed: `/feed.xml`

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

**Audio never goes in the repo.** Each MP3 is attached to a GitHub Release tagged `eNN` (e.g. `e01`), so the repo stays small no matter how many episodes there are. Audio URL pattern:
`https://github.com/houzwithjoey/cre-grind-podcast/releases/download/eNN/cre-grind-eNN.mp3`

## Publishing a new episode

1. Render the MP3 with `tools/render.py`, then re-encode for the web:
   `ffmpeg -i in.mp3 -ac 1 -ar 24000 -b:a 64k cre-grind-eNN.mp3`
2. Create the release and upload the audio:
   `gh release create eNN cre-grind-eNN.mp3 --title "ENN: <title>" --notes "<summary>"`
3. Add `episodes/eNN-<slug>/notes.md` and `script.txt`.
4. Add the episode to `episodes.json` (number, slug, title, headline, summary, type, date, audio_file, duration_sec from ffprobe, size_bytes, interview_line, panel, stats). Refresh `ticker` with this week's figures and remove it from `upcoming`, adding the next topics.
5. `python3 tools/build.py`, then commit and push. GitHub Pages redeploys automatically.
