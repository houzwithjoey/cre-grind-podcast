"""Build the CRE Grind website into docs/ from episodes.json + episodes/<slug>/notes.md.

Usage: python3 tools/build.py
Requires: pip install markdown pillow
Outputs: docs/index.html, docs/episodes/index.html, docs/episodes/<slug>/index.html,
         docs/feed.xml, docs/assets/{style.css,player.js,cover.png}
Audio is NOT stored in the repo: each MP3 is a GitHub Release asset (tag eNN).
"""
import json, os, shutil, html, datetime
from email.utils import format_datetime
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
E = html.escape

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900'
         '&amp;family=Source+Serif+4:ital,wght@0,400;0,600;1,400&amp;family=Inter:wght@500;600'
         '&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap">')


def d(iso):
    return datetime.date.fromisoformat(iso)


def nice_date(iso, short=False):
    x = d(iso)
    return x.strftime("%b %-d") if short else x.strftime("%B %-d, %Y")


def mmss(sec):
    return f"{sec // 60}:{sec % 60:02d}"


def audio_url(site, ep):
    return f"{site['audio_base']}/e{ep['number']:02d}/{ep['audio_file']}"


def page(site, data, title, body, depth, desc=None):
    up = "../" * depth
    t = data["ticker"]
    items = "".join(
        f'<span><span class="lbl">{E(i["label"])}</span><span class="{E(i.get("tone", ""))}">{E(i["value"])}</span></span>'
        for i in t["items"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or site['description'])}">
<link rel="alternate" type="application/rss+xml" title="{E(site['title'])}" href="{up}feed.xml">
<link rel="icon" href="{up}assets/cover.png">
{FONTS}
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<div class="ticker" aria-label="Market snapshot"><div class="ticker-row">{items}<span class="asof">AS OF {E(nice_date(t['as_of'], True).upper())}</span></div></div>
<div class="wrap">
{body}
<footer><span>{E(site['title'])} · by {E(site['author'])}</span><span>AI-voiced hosts · Sources in every episode's notes · <a href="{up}feed.xml">RSS</a></span></footer>
</div>
</body>
</html>
"""


def masthead(up, small=False):
    return f"""<header class="masthead{' small' if small else ''}">
<a class="name" href="{up}index.html">The CRE Grind</a>
<nav class="nav" aria-label="Main"><a href="{up}index.html">Home</a><a href="{up}episodes/index.html">All episodes</a><a href="{up}index.html#about">About</a><a class="sub" href="{up}feed.xml">Subscribe · RSS</a></nav>
</header>"""


def panel(ep):
    p = ep.get("panel")
    if not p:
        return ""
    rows = "".join(f'<div class="prow"><span>{E(a)}</span><span>{E(b)}</span></div>' for a, b in p["rows"])
    return f'<div class="panel"><div class="ptitle">// {E(p["title"])}</div>{rows}</div>'


def stats(ep):
    s = ep.get("stats") or []
    if not s:
        return ""
    return '<div class="section-label" style="margin:0">By the numbers</div>' + "".join(
        f'<div class="stat"><div class="big">{E(a)}</div><div class="cap">{E(b)}</div></div>' for a, b in s)


def archive_table(eps, upcoming, up):
    rows = "".join(
        f'<tr><td class="num">E{e["number"]:02d}</td><td><a href="{up}episodes/{e["slug"]}/index.html">{E(e["title"])}</a></td>'
        f'<td>{E(e["type"])}</td><td>{nice_date(e["date"], True)}</td><td>{mmss(e["duration_sec"])}</td></tr>'
        for e in eps)
    rows += "".join(
        f'<tr class="soon"><td class="num">E{u["number"]:02d}</td><td>{E(u["title"])}</td><td>{E(u["type"])}</td>'
        f'<td>{nice_date(u["date"], True)}</td><td>Upcoming</td></tr>' for u in upcoming)
    return (f'<div class="table-scroll"><table class="ep-table"><thead><tr><th>NO.</th><th>TITLE</th><th>SECTION</th>'
            f'<th>DATE</th><th>LENGTH</th></tr></thead><tbody>{rows}</tbody></table></div>')


def build_home(site, data, eps):
    latest = eps[0]
    up = ""
    href = f"episodes/{latest['slug']}/index.html"
    upcoming = "".join(
        f'<div><span class="kicker">{E(d(u["date"]).strftime("%A, %b %-d"))} · {E(u["type"])}</span><h3>{E(u["title"])}</h3></div>'
        for u in data["upcoming"][:3])
    body = f"""<div class="dateline"><span>Latest episode: {nice_date(latest['date'])}</span><span>A weekly podcast · New episodes Sundays</span></div>
{masthead(up)}
<section class="lead">
<article>
<div class="kicker">Episode {latest['number']} · {E(latest['type'])}</div>
<h1 class="headline"><a href="{href}" style="text-decoration:none">{E(latest.get('headline') or latest['title'])}</a></h1>
<p class="dek">{E(latest['summary'])}</p>
<div class="listen"><a class="btn-round" href="{href}" aria-label="Listen to episode {latest['number']}">▶</a><strong>Listen · {latest['duration_sec'] // 60} min</strong><span class="meta">{E(latest['title'])}</span></div>
{panel(latest)}
</article>
<aside>{stats(latest)}</aside>
</section>
<section class="upcoming"><h2 class="section-label">Coming up</h2><div class="cols">{upcoming}</div></section>
<section class="archive"><h2 class="section-label">Every episode</h2>{archive_table(eps, data['upcoming'], up)}</section>
<section class="about" id="about">
<div><h2 class="section-label">From the latest show notes</h2><p class="quote">“{E(latest.get('interview_line', ''))}”</p></div>
<div><h2 class="section-label">About the show</h2><p>{E(site['description'])} Every episode ships with a worked example, five takeaways and sources. Subscribe in any podcast app with the <a href="feed.xml">RSS feed</a>.</p></div>
</section>"""
    return page(site, data, f"{site['title']} — {site['tagline']}", body, 0)


def build_archive(site, data, eps):
    up = "../"
    body = f"""{masthead(up, True)}
<section class="archive"><h1 class="headline" style="margin-bottom:24px">All episodes</h1>{archive_table(eps, data['upcoming'], up)}</section>"""
    return page(site, data, f"All episodes — {site['title']}", body, 1)


def build_episode(site, data, eps, i):
    ep = eps[i]
    up = "../../"
    notes_path = os.path.join(ROOT, "episodes", ep["slug"], "notes.md")
    notes_html = markdown.markdown(open(notes_path, encoding="utf-8").read()) if os.path.exists(notes_path) else ""
    newer = eps[i - 1] if i > 0 else None
    older = eps[i + 1] if i + 1 < len(eps) else None
    pager = '<nav class="pager" aria-label="Episodes">'
    pager += f'<a href="{up}episodes/{older["slug"]}/index.html">← E{older["number"]:02d} · {E(older["title"])}</a>' if older else "<span></span>"
    pager += f'<a href="{up}episodes/{newer["slug"]}/index.html">E{newer["number"]:02d} · {E(newer["title"])} →</a>' if newer else "<span></span>"
    pager += "</nav>"
    url = audio_url(site, ep)
    speeds = "".join(f'<button type="button" data-speed="{s}" aria-pressed="false">{s}×</button>' for s in ("1", "1.25", "1.5", "1.75"))
    body = f"""{masthead(up, True)}
<section class="ep-head">
<div class="kicker">Episode {ep['number']} · {E(ep['type'])} · {nice_date(ep['date'])} · {ep['duration_sec'] // 60} min</div>
<h1 class="headline">{E(ep['title'])}</h1>
<p class="dek">{E(ep['summary'])}</p>
</section>
<div class="player">
<audio controls preload="metadata" src="{E(url)}" data-slug="{E(ep['slug'])}">Your browser does not support audio. <a href="{E(url)}">Download the MP3</a>.</audio>
<div class="controls"><button type="button" data-skip="-15" aria-label="Back 15 seconds">−15s</button><button type="button" data-skip="30" aria-label="Forward 30 seconds">+30s</button>{speeds}<a class="dl" href="{E(url)}" download>Download MP3</a></div>
</div>
<div class="ep-body">
<div class="notes">{notes_html}</div>
<aside class="side">{panel(ep)}{stats(ep)}
<div><div class="section-label" style="margin-bottom:8px">Interview line</div><p class="quote" style="margin:0">“{E(ep.get('interview_line', ''))}”</p></div>
</aside>
</div>
{pager}
<script src="{up}assets/player.js"></script>"""
    return page(site, data, f"E{ep['number']:02d}: {ep['title']} — {site['title']}", body, 2, ep["summary"])


def build_feed(site, eps):
    base = site["url"].rstrip("/")
    items = []
    for ep in eps:
        link = f"{base}/episodes/{ep['slug']}/"
        pub = format_datetime(datetime.datetime.combine(d(ep["date"]), datetime.time(16, 0), datetime.timezone.utc))
        items.append(f"""<item>
<title>{E(f"E{ep['number']:02d}: {ep['title']}")}</title>
<link>{link}</link>
<guid isPermaLink="false">cre-grind-e{ep['number']:02d}</guid>
<pubDate>{pub}</pubDate>
<description>{E(ep['summary'])}</description>
<enclosure url="{E(audio_url(site, ep))}" length="{ep['size_bytes']}" type="audio/mpeg"/>
<itunes:duration>{ep['duration_sec']}</itunes:duration>
<itunes:episode>{ep['number']}</itunes:episode>
<itunes:explicit>false</itunes:explicit>
</item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>{E(site['title'])}</title>
<link>{base}/</link>
<atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>
<description>{E(site['description'])}</description>
<language>{site['language']}</language>
<itunes:author>{E(site['author'])}</itunes:author>
<itunes:image href="{base}/assets/cover.png"/>
<itunes:category text="{E(site['category'])}"/>
<itunes:explicit>false</itunes:explicit>
<itunes:type>episodic</itunes:type>
{''.join(items)}
</channel>
</rss>
"""


def make_cover(path):
    """1400x1400 podcast artwork (required by podcast apps). Built once, kept in docs/assets."""
    if os.path.exists(path):
        return
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (1400, 1400), "#0b0e11")
    dr = ImageDraw.Draw(im)
    def font(names, size):
        for n in names:
            try:
                return ImageFont.truetype(n, size)
            except OSError:
                pass
        return ImageFont.load_default(size)
    serif = font(["DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"], 200)
    mono = font(["DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"], 52)
    dr.rectangle([90, 90, 1310, 1310], outline="#ffb000", width=6)
    dr.text((160, 200), "CRE_GRIND >", fill="#ffb000", font=mono)
    dr.text((150, 470), "The CRE", fill="#ffffff", font=serif)
    dr.text((150, 700), "Grind", fill="#ffffff", font=serif)
    dr.line([160, 1010, 560, 1010], fill="#b3261e", width=10)
    dr.text((160, 1080), "COMMERCIAL REAL ESTATE,", fill="#d7dde4", font=mono)
    dr.text((160, 1150), "ONE TOPIC A WEEK", fill="#d7dde4", font=mono)
    im.save(path, optimize=True)


def main():
    data = json.load(open(os.path.join(ROOT, "episodes.json"), encoding="utf-8"))
    site = data["site"]
    eps = sorted(data["episodes"], key=lambda e: e["number"], reverse=True)
    released = {e["number"] for e in eps}
    data["upcoming"] = [u for u in data.get("upcoming", []) if u["number"] not in released]

    assets = os.path.join(OUT, "assets"); os.makedirs(assets, exist_ok=True)
    for f in ("style.css", "player.js"):
        shutil.copy(os.path.join(ROOT, "tools", f), os.path.join(assets, f))
    make_cover(os.path.join(assets, "cover.png"))

    def write(rel, text):
        p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(text)

    write("index.html", build_home(site, data, eps))
    write("episodes/index.html", build_archive(site, data, eps))
    for i, ep in enumerate(eps):
        write(f"episodes/{ep['slug']}/index.html", build_episode(site, data, eps, i))
    write("feed.xml", build_feed(site, eps))
    write(".nojekyll", "")
    print(f"Built {len(eps)} episode page(s) into docs/")


if __name__ == "__main__":
    main()
