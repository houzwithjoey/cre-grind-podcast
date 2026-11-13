"""Build the CRE Deal Makers section (docs/deal-makers/) from deal-makers.json.

Called from tools/build.py. Shares the site's look, ticker and footer, but has its own
masthead, episode pages, feed (docs/deal-makers/feed.xml) and cover art.
"""
import os, json, datetime, html
from email.utils import format_datetime
import markdown

E = html.escape


def masthead(up, small=False):
    """up = path back to the site root."""
    return f"""<header class="masthead{' small' if small else ''}">
<div class="kicker" style="margin-bottom:6px">A Houz Real Estate podcast</div>
<a class="name" href="{up}deal-makers/index.html">CRE Deal Makers</a>
<nav class="nav" aria-label="Deal Makers"><a href="{up}deal-makers/index.html">Profiles</a><a href="{up}index.html">The CRE Grind</a><a href="{up}about/index.html">About</a><a class="sub" href="{up}deal-makers/feed.xml">Subscribe · RSS</a></nav>
</header>"""


def build(root, out, grind, page, nice_date, write):
    path = os.path.join(root, "deal-makers.json")
    if not os.path.exists(path):
        return
    dm = json.load(open(path, encoding="utf-8"))
    show = dm["show"]
    eps = sorted(dm["episodes"], key=lambda e: e["number"], reverse=True)
    grind_eps = {e["slug"]: e for e in grind["episodes"]}

    def audio(ep):
        return f"{show['audio_base']}/{ep['audio_file']}"

    def glance(ep, title="At a glance"):
        rows = "".join(f'<div class="prow"><span>{E(a)}</span><span style="text-align:right">{E(b)}</span></div>' for a, b in ep.get("glance", []))
        return f'<div class="panel"><div class="ptitle">// {E(title)} · {E(ep["company"])}</div>{rows}</div>'

    def chips(ep):
        return '<div style="display:flex;flex-wrap:wrap;gap:8px">' + "".join(
            f'<span style="font-family:var(--sans);font-size:12px;font-weight:600;border:1px solid var(--ink);border-radius:999px;padding:4px 10px">{E(p)}</span>'
            for p in ep.get("practices", [])) + "</div>"

    def deals_table(ep):
        rows = "".join(f"<tr><td><strong>{E(a)}</strong></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in ep.get("deals", []))
        return (f'<div class="table-scroll"><table class="ep-table"><thead><tr><th>DEAL</th><th>YEAR</th><th>KEY NUMBERS</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')

    def partners(ep):
        return "".join(f'<div class="stat"><div class="section-label" style="margin:0 0 4px">{E(a)}</div><div class="cap">{E(b)}</div></div>'
                       for a, b in ep.get("partners", []))

    # Show home
    up = "../"
    latest = eps[0]
    href = f"episodes/{latest['slug']}/index.html"
    cards = "".join(f"""<a href="episodes/{e['slug']}/index.html" style="text-decoration:none;border:1px solid var(--rule);border-top:4px solid var(--ink);padding:20px;display:flex;flex-direction:column;gap:8px">
<span class="kicker">Episode {e['number']} · {nice_date(e['date'], True)} · {e['duration_sec'] // 60} min</span>
<span style="font-family:var(--serif-display);font-size:26px;font-weight:700;line-height:1.15">{E(e['company'])}</span>
<span style="font-size:15px;color:#444;line-height:1.5">{E(e['headline'])}</span></a>""" for e in eps)
    body = f"""{masthead(up)}
<section class="lead">
<article>
<div class="kicker">Latest profile · Episode {latest['number']}</div>
<h1 class="headline"><a href="{href}" style="text-decoration:none">{E(latest['company'])}: {E(latest['headline'])}</a></h1>
<p class="dek">{E(latest['summary'])}</p>
{chips(latest)}
<div class="listen"><a class="btn-round" href="{href}" aria-label="Listen to the {E(latest['company'])} episode">▶</a><strong>Listen · {latest['duration_sec'] // 60} min</strong><span class="meta">{nice_date(latest['date'])}</span></div>
</article>
<aside>{glance(latest)}</aside>
</section>
<section class="archive"><h2 class="section-label">All company profiles</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px">{cards}</div></section>
<section class="about">
<div><h2 class="section-label">About the show</h2><p>{E(show['description'])} Every episode covers the company's history, what it actually does, its defining deals, who it works with, where it stands now, and what to know if you're interviewing there.</p></div>
<div><h2 class="section-label">Listen</h2><p>Play episodes here, or add the feed to Apple Podcasts or Overcast:</p>
<code style="display:block;margin-top:10px;font-family:var(--mono);font-size:13px;background:#f4f4f4;border:1px solid var(--rule);border-radius:6px;padding:12px;word-break:break-all">{E(show['url'])}/feed.xml</code></div>
</section>"""
    write("deal-makers/index.html", page(show, grind, f"{show['title']} — {show['tagline']}", body, 1))

    # Episode pages
    for i, ep in enumerate(eps):
        up = "../../../"
        notes = os.path.join(root, "deal-makers", ep["slug"], "notes.md")
        notes_html = markdown.markdown(open(notes, encoding="utf-8").read()) if os.path.exists(notes) else ""
        url = audio(ep)
        speeds = "".join(f'<button type="button" data-speed="{s}" aria-pressed="false">{s}×</button>' for s in ("1", "1.25", "1.5", "1.75"))
        links = "".join(
            f'<li><a href="{up}episodes/{s}/index.html">The CRE Grind E{grind_eps[s]["number"]:02d}: {E(grind_eps[s]["title"])}</a> <span style="color:var(--muted)">— {E(why)}</span></li>'
            for s, why in ep.get("grind_links", []) if s in grind_eps)
        links_html = f'<div><div class="section-label" style="margin-bottom:8px">Go deeper on The CRE Grind</div><ul style="margin:0;padding-left:18px;font-family:var(--sans);font-size:14px;line-height:1.6">{links}</ul></div>' if links else ""
        newer = eps[i - 1] if i > 0 else None
        older = eps[i + 1] if i + 1 < len(eps) else None
        pager = '<nav class="pager" aria-label="Profiles">'
        pager += f'<a href="../{older["slug"]}/index.html">← {E(older["company"])}</a>' if older else "<span></span>"
        pager += f'<a href="../{newer["slug"]}/index.html">{E(newer["company"])} →</a>' if newer else "<span></span>"
        pager += "</nav>"
        body = f"""{masthead(up, True)}
<section class="ep-head">
<div class="kicker">CRE Deal Makers · Episode {ep['number']} · {nice_date(ep['date'])} · {ep['duration_sec'] // 60} min</div>
<h1 class="headline">{E(ep['title'])}</h1>
<p class="dek">{E(ep['summary'])}</p>
{chips(ep)}
</section>
<div class="player">
<audio controls preload="metadata" src="{E(url)}" data-slug="dm-{E(ep['slug'])}">Your browser does not support audio. <a href="{E(url)}">Download the MP3</a>.</audio>
<div class="controls"><button type="button" data-skip="-15" aria-label="Back 15 seconds">−15s</button><button type="button" data-skip="30" aria-label="Forward 30 seconds">+30s</button>{speeds}<a class="dl" href="{E(url)}" download>Download MP3</a></div>
</div>
<section class="archive" style="border-bottom:none"><h2 class="section-label">Defining deals</h2>{deals_table(ep)}</section>
<div class="ep-body" style="margin-top:0">
<div class="notes">{notes_html}</div>
<aside class="side">{glance(ep)}
<div><div class="section-label" style="margin-bottom:8px">Who they work with</div>{partners(ep)}</div>
<div><div class="section-label" style="margin-bottom:8px">Networking line</div><p class="quote" style="margin:0">“{E(ep.get('interview_line', ''))}”</p></div>
{links_html}
</aside>
</div>
{pager}
<script src="{up}assets/player.js"></script>"""
        write(f"deal-makers/episodes/{ep['slug']}/index.html",
              page(show, grind, f"{ep['company']} — {show['title']}", body, 3, ep["summary"]))

    # Feed
    base = show["url"].rstrip("/")
    items = []
    for ep in eps:
        pub = format_datetime(datetime.datetime.combine(datetime.date.fromisoformat(ep["date"]), datetime.time(16, 0), datetime.timezone.utc))
        items.append(f"""<item>
<title>{E(f"E{ep['number']:02d}: {ep['title']}")}</title>
<link>{base}/episodes/{ep['slug']}/</link>
<guid isPermaLink="false">cre-deal-makers-e{ep['number']:02d}</guid>
<pubDate>{pub}</pubDate>
<description>{E(ep['summary'] + ' Hosts are AI-generated voices; researched and scripted with AI from public sources.')}</description>
<enclosure url="{E(audio(ep))}" length="{ep['size_bytes']}" type="audio/mpeg"/>
<itunes:duration>{ep['duration_sec']}</itunes:duration>
<itunes:episode>{ep['number']}</itunes:episode>
<itunes:explicit>false</itunes:explicit>
</item>""")
    write("deal-makers/feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>{E(show['title'])}</title>
<link>{base}/</link>
<atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>
<description>{E(show['description'] + ' Hosts are AI-generated voices.')}</description>
<language>{show['language']}</language>
<itunes:author>{E(show['author'])}</itunes:author>
<itunes:image href="{base}/cover.png"/>
<itunes:category text="{E(show['category'])}"/>
<itunes:explicit>false</itunes:explicit>
<itunes:type>episodic</itunes:type>
{''.join(items)}
</channel>
</rss>
""")
    make_cover(os.path.join(out, "deal-makers", "cover.png"))


def make_cover(path):
    if os.path.exists(path):
        return
    from PIL import Image, ImageDraw, ImageFont
    def font(n, size):
        for c in (n, "/usr/share/fonts/truetype/dejavu/" + n):
            try:
                return ImageFont.truetype(c, size)
            except OSError:
                pass
        return ImageFont.load_default(size)
    im = Image.new("RGB", (1400, 1400), "#ffffff")
    dr = ImageDraw.Draw(im)
    serif, mono = font("DejaVuSerif-Bold.ttf", 190), font("DejaVuSansMono.ttf", 52)
    dr.rectangle([0, 0, 1400, 120], fill="#0b0e11")
    dr.text((90, 32), "COMPANY PROFILES  ·  HOUZ", fill="#ffb000", font=mono)
    dr.text((90, 380), "CRE Deal", fill="#111111", font=serif)
    dr.text((90, 600), "Makers", fill="#111111", font=serif)
    dr.line([100, 900, 520, 900], fill="#b3261e", width=12)
    dr.text((100, 980), "ONE COMPANY", fill="#333333", font=mono)
    dr.text((100, 1050), "PER EPISODE", fill="#333333", font=mono)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)
