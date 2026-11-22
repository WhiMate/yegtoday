#!/usr/bin/env python3
"""Assemble the static prototype pages.

Reads src/*.html, swaps in the shared partials (sprite, header, footer), lays out
the stories in src/stories.json into the homepage blocks, fills in the brand
settings below, and writes the finished pages to the project root.

    python3 build.py

To update the news, edit src/stories.json and run it again.
To rename the site, change BRAND and run it again.
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

BRAND = {
    "NAME": "YEGToday",        # display name used in titles, alt text, footer and copy
    "SHORT": "YEGToday",       # prefix for newsletter names ("<SHORT> Daily")
    "LOGO_SRC": "assets/img/yegtoday-logo.svg",  # header and footer logo
}

PAGES = ["index.html", "article.html"]
MARKERS = {
    "<!--SPRITE-->": "partials/sprite.svg",
    "<!--HEADER-->": "partials/header.html",
    "<!--FOOTER-->": "partials/footer.html",
}

# ---------------------------------------------------------------- stories ----

# Illustration placeholder palettes that suit each scene (rotated for variety).
THEMES = {
    "skyline": ["dusk", "day"], "bridge": ["dusk", "winter"], "legislature": ["gold", "day"],
    "lrt": ["day", "night"], "snow": ["winter", "night"], "rink": ["night", "winter"],
    "pyramids": ["winter", "day"], "farm": ["gold"], "refinery": ["dusk", "night"],
    "court": ["day", "soft"], "festival": ["night", "dusk"], "trail": ["green"],
    "aurora": ["night"], "cityhall": ["day", "soft"], "person": ["soft", "day", "green", "gold"],
}
MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]

# How wide each photo slot is drawn (matches assets/css/styles.css), so phones and
# thumbnails can pick the 400px "-sm" file instead of the 800px one.
SIZES = {
    "card": "(max-width: 600px) calc(100vw - 32px), (max-width: 860px) calc(50vw - 31px), 300px",
    "trend": "(max-width: 600px) 112px, (max-width: 860px) calc(33vw - 31px), 190px",
    "row": "(max-width: 600px) 112px, 135px",
    "strip": "(max-width: 1000px) 112px, 72px",
}

# Homepage community/topic blocks: marker key -> (sections, title, "More ..." label)
SECTION_BLOCKS = {
    "edmonton": (["edmonton"], "Edmonton News", "Edmonton News"),
    "st-albert": (["st-albert"], "St. Albert News", "St. Albert News"),
    "sherwood-park": (["sherwood-park"], "Sherwood Park & Strathcona County News", "Sherwood Park News"),
    "tri-region": (["tri-region", "enoch"], "Spruce Grove, Stony Plain, Parkland & Enoch News", "Tri-Region News"),
    "south": (["south"], "Leduc, Beaumont & Devon News", "Leduc, Beaumont & Devon News"),
    "north": (["north"], "Fort Saskatchewan, Morinville & Sturgeon News", "North News"),
    "crime": (["crime"], "Cops, Crime & Court", "Cops, Crime & Court"),
    "business": (["business"], "Business & Energy", "Business & Energy"),
    "sports": (["sports"], "Sports", "Sports"),
    "living": (["living"], "Edmonton Living", "Edmonton Living"),
}
BADGE = {
    "edmonton": "Edmonton News", "st-albert": "St. Albert", "sherwood-park": "Sherwood Park",
    "tri-region": "Tri-Region", "south": "Leduc & area", "north": "North", "enoch": "Enoch Cree Nation",
    "crime": "Crime", "business": "Business", "sports": "Sports", "living": "Living",
}


def esc(text) -> str:
    return escape(str(text or ""), quote=True)


def fmt_date(iso: str, with_year: bool = False) -> str:
    y, m, d = (int(x) for x in iso[:10].split("-"))
    text = f"{MONTHS[m - 1]} {d}"
    return f"{text}, {y}" if with_year else text


class Homepage:
    def __init__(self, data: dict):
        stories, seen = [], set()
        for group in data["groups"].values():
            for s in group["stories"]:
                if s["url"] in seen:
                    continue
                seen.add(s["url"])
                stories.append(s)
        self.all = stories
        self.running_title = next((g["runningTitle"] for g in data["groups"].values() if g.get("runningTitle")), "")
        self.used = set()
        self.n = 0
        self.lead_href = data.get("leadHref", "")
        self.eager = 1          # load the first photo eagerly (it's above the fold)

    # -- selection helpers
    def pool(self, sections=None, running=None, exclude=()):
        out = [
            s for s in self.all
            if s["url"] not in self.used
            and (sections is None or s["section"] in sections)
            and s["section"] not in exclude
            and (running is None or bool(s.get("running")) == running)
        ]
        return sorted(out, key=lambda s: s["published"], reverse=True)

    def best(self, stories):
        return max(stories, key=lambda s: (s.get("fun", 0), s["published"])) if stories else None

    def take(self, s):
        self.used.add(s["url"])
        return s

    # -- pieces
    def media(self, s, kind="card") -> str:
        photo = s.get("photo")
        if photo:
            # Decorative inside the story link: the headline already names the story.
            loading = 'loading="eager" fetchpriority="high"' if self.eager > 0 else 'loading="lazy"'
            self.eager -= 1
            src = photo["src"]
            small = re.sub(r"\.webp$", "-sm.webp", src)
            srcset = (f' srcset="{esc(small)} 400w, {esc(src)} 800w" sizes="{SIZES[kind]}"'
                      if small != src and (ROOT / small).exists() else "")
            return (f'<span class="media"><img src="{esc(src)}"{srcset} alt="" width="800" height="533" '
                    f'{loading} decoding="async"></span>')
        scene = s.get("scene") if s.get("scene") in THEMES else "skyline"
        themes = THEMES[scene]
        self.n += 1
        return f'<span class="media t-{themes[self.n % len(themes)]}"><svg aria-hidden="true"><use href="#s-{scene}"/></svg></span>'

    @staticmethod
    def meta(s) -> str:
        if s["section"] == "history":
            return f'{esc(fmt_date(s["published"], True))} · {esc(s["source"])}'
        who = f'{esc(s["author"])} · ' if s.get("author") else ""
        return f'{who}{esc(s["source"])} · {esc(fmt_date(s["published"]))}'

    @staticmethod
    def href(s) -> str:
        return esc(s["url"])

    def card(self, s) -> str:
        return (f'<article class="card"><a class="story-link" href="{self.href(s)}">{self.media(s)}'
                f'<h3 class="headline h-lg">{esc(s["headline"])}</h3><p class="dek clamp-3">{esc(s["dek"])}</p>'
                f'<span class="meta">{self.meta(s)}</span></a></article>')

    def row(self, s) -> str:
        return (f'<a class="row story-link" href="{self.href(s)}">{self.media(s, "row")}<div>'
                f'<h3 class="headline h-md">{esc(s["headline"])}</h3><p class="dek clamp-2">{esc(s["dek"])}</p>'
                f'<span class="meta">{self.meta(s)}</span></div></a>')

    @staticmethod
    def block(key, title, inner, more=None, title_extra="") -> str:
        more_html = f'<a class="more-link" href="#">More {esc(more)} <span aria-hidden="true">&gt;</span></a>' if more else ""
        return (f'<section class="block"><h2 class="block-title" id="sec-{key}">{esc(title)}{title_extra}</h2>'
                f'{inner}{more_html}</section>')

    def cards_and_rows(self, stories, rows_max=4) -> str:
        stories = [self.take(s) for s in stories[: 2 + rows_max]]
        html = ""
        if len(stories) >= 2:
            html += '<div class="cols-2">' + "".join(self.card(s) for s in stories[:2]) + "</div>"
            rest = stories[2:]
        else:
            rest = stories
        if rest:
            html += '<div class="rows">' + "".join(self.row(s) for s in rest) + "</div>"
        return html

    # -- blocks
    def pinned(self, where):
        return [s for s in self.pool() if s.get("pin") == where]

    def highlights(self) -> str:
        # An editor's "pin" wins; otherwise the most interesting recent Edmonton story leads.
        lead = next(iter(self.pinned("lead")), None) or self.best(self.pool(["edmonton"])) \
            or self.best(self.pool(exclude=("history", "opinion")))
        if not lead:
            return ""
        self.take(lead)
        stack = [self.take(s) for s in self.pinned("highlights")[:3]]
        for sections in (["st-albert", "sherwood-park", "north"], ["tri-region", "south", "enoch"], ["living", "sports"]):
            if len(stack) >= 3:
                break
            pick = self.best(self.pool(sections, running=False))
            if pick:
                stack.append(self.take(pick))
        while len(stack) < 3:
            pick = self.best(self.pool(exclude=("history", "opinion")))
            if not pick:
                break
            stack.append(self.take(pick))
        href = esc(self.lead_href) if self.lead_href else self.href(lead)
        badge = BADGE.get(lead["section"], lead.get("community", "News"))
        lead_html = (
            f'<article class="lead"><a class="story-link" href="{href}"><span class="lead-media">{self.media(lead)}'
            f'<span class="badge">{esc(badge)}</span></span><h3 class="headline h-xl">{esc(lead["headline"])}</h3>'
            f'<p class="dek">{esc(lead["dek"])}</p><span class="meta">{self.meta(lead)}</span></a></article>'
        )
        stack_html = "".join(
            f'<article><a class="story-link" href="{self.href(s)}"><h3 class="headline h-md">{esc(s["headline"])}</h3>'
            f'<p class="dek clamp-2">{esc(s["dek"])}</p><span class="meta">{self.meta(s)}</span></a></article>'
            for s in stack
        )
        inner = (f'<div class="cols-2">{lead_html}<div><div class="stack">{stack_html}</div>'
                 f'<a class="more-link" href="#">More Highlights <span aria-hidden="true">&gt;</span></a></div></div>')
        return f'<section class="block"><h2 class="block-title" id="sec-highlights">Highlights</h2>{inner}</section>'

    def trending(self) -> str:
        picks = sorted(self.pool(running=False, exclude=("history", "opinion")),
                       key=lambda s: (s.get("fun", 0), s["published"]), reverse=True)[:3]
        if len(picks) < 3:
            return ""
        items = "".join(
            f'<li><a class="story-link" href="{self.href(self.take(s))}">{self.media(s, "trend")}'
            f'<span class="rank" aria-hidden="true">{i} <svg aria-hidden="true"><use href="#i-trend"/></svg></span>'
            f'<h3 class="headline h-sm">{esc(s["headline"])}</h3></a></li>'
            for i, s in enumerate(picks, 1)
        )
        return f'<section class="block"><h2 class="block-title" id="sec-trending">Trending Now</h2><ol class="cols-3 trend">{items}</ol></section>'

    def running(self) -> str:
        picks = self.pool(running=True)[:3]
        if len(picks) < 2:
            return ""
        items = "".join(
            f'<article><a class="story-link" href="{self.href(self.take(s))}">{self.media(s, "strip")}<div>'
            f'<h3 class="headline">{esc(s["headline"])}</h3><span class="meta">{self.meta(s)}</span></div></a></article>'
            for s in picks
        )
        title = self.running_title or "Ongoing story"
        dot = ' <span class="live-dot" aria-hidden="true"></span>'
        return self.block("running", title, f'<div class="cols-3 strip">{items}</div>', title_extra=dot)

    def section(self, key) -> str:
        sections, title, more = SECTION_BLOCKS[key]
        stories = self.pool(sections, running=False) if key == "crime" else self.pool(sections)
        if not stories:
            return ""
        rows_max = 9 if key == "edmonton" else 5  # the city block carries the most stories, like a provincial-news block
        return self.block(key, title, self.cards_and_rows(stories, rows_max), more)

    def rows_block(self, key, sections, title, more) -> str:
        stories = [self.take(s) for s in self.pool(sections)[:4]]
        if key == "history":
            stories.sort(key=lambda s: s["published"])
        if not stories:
            return ""
        return self.block(key, title, '<div class="rows">' + "".join(self.row(s) for s in stories) + "</div>", more)

    def render(self) -> dict:
        # Order matters: highlights and trending claim the strongest stories first.
        out = {"highlights": self.highlights(), "trending": self.trending(), "running": self.running()}
        for key in SECTION_BLOCKS:
            out[key] = self.section(key)
        out["history"] = self.rows_block("history", ["history"], "This Month in Edmonton History", "Edmonton History")
        out["opinion"] = self.rows_block("opinion", ["opinion"], "Opinion from Around the Region", "Opinion")
        out["neighbours"] = self.rows_block("neighbours", ["neighbours"], "Meet Your Neighbours", "Neighbours")
        return out

    def article(self) -> dict:
        """Blocks for the article page: the lead's hero figure, 'More Edmonton News', credits."""
        lead = next(iter(self.pinned("lead")), None)
        figure = ""
        if lead:
            self.take(lead)
            p = lead.get("photo")
            if p:
                figure = hero_figure(p)
            else:
                figure = (f'<figure class="article-figure">{self.media(lead)}'
                          f'<figcaption>Illustration placeholder</figcaption></figure>')
        self.eager = 0
        more = self.rows_block("more", ["edmonton"], "More Edmonton News", "Edmonton News")
        return {"article-figure": figure, "article-more": more}

    def story_page(self, s) -> dict:
        """Blocks for one of YEGToday's own stories (a story with a `body`), rendered from src/story.html."""
        self.take(s)
        sections, title, label = next((v for v in SECTION_BLOCKS.values() if s["section"] in v[0]),
                                      (["edmonton"], "Edmonton News", "Edmonton News"))
        how = s.get("reported", "Reported by YEGToday")
        head = (
            '<nav aria-label="Breadcrumb"><ol class="crumbs"><li><a href="index.html">Home</a></li>'
            f'<li><a href="#" aria-current="page">{esc(title)}</a></li></ol></nav>'
            f'<h1 class="article-title">{esc(s["headline"])}</h1><p class="article-dek">{esc(s["dek"])}</p>'
            '<div class="byline-row"><span class="author-pic"><svg aria-hidden="true" class="t-soft"><use href="#s-person"/></svg></span>'
            f'<div><span class="author-name">{esc(s.get("author") or "YEGToday staff")}</span>'
            f'<span class="author-time">{esc(fmt_date(s["published"], True))} · {esc(how)}</span></div>'
            '<div class="byline-actions"><button class="btn btn-outline" type="button" data-share>'
            '<svg aria-hidden="true"><use href="#i-share"/></svg><span>Share this</span></button>'
            '<p class="share-status" role="status" data-share-status></p></div></div>'
        )
        body = "".join(f"<p>{esc(par)}</p>" for par in s["body"])
        if s.get("unknowns"):
            items = "".join(f"<li>{esc(x)}</li>" for x in s["unknowns"])
            body += f'<div class="fact-box"><h2>Still unanswered</h2><ul>{items}</ul></div>'
        trust = (f'<div class="trust"><strong>How we reported this:</strong> {esc(s["howReported"])} '
                 'Spotted an error? <a href="#">Tell us</a> or read our <a href="#">corrections policy</a>.</div>'
                 if s.get("howReported") else "")
        self.eager = 0
        more = self.rows_block("more", sections, f"More {title}", label)
        return {"story-title": esc(s["headline"]), "story-description": esc(s["dek"]), "story-head": head,
                "article-figure": hero_figure(s["photo"]) if s.get("photo") else "",
                "story-body": body, "story-trust": trust, "article-more": more}


def hero_figure(p) -> str:
    """The big photo at the top of a story page, with its credit as the caption."""
    # alt describes what's in the frame; the caption (read with the figure) says what it is
    # and who took it, so the two don't repeat each other.
    alt = esc(p.get("alt", ""))
    if p.get("hero"):
        img = (f'<img src="{esc(p["hero"])}" srcset="{esc(p["src"])} 800w, {esc(p["hero"])} 1280w" '
               f'sizes="(max-width: 860px) calc(100vw - 32px), 630px" alt="{alt}" width="1280" height="853" '
               f'fetchpriority="high">')
    else:
        img = f'<img src="{esc(p["src"])}" alt="{alt}" width="800" height="533" fetchpriority="high">'
    return (f'<figure class="article-figure"><span class="media">{img}</span>'
            f'<figcaption>{credit_line(p)}</figcaption></figure>')


def credit_line(p) -> str:
    """'What it shows. Photo: "Title" by Author, Licence, via Source (cropped and resized).'

    A photo licensed from a news agency sets `credit` instead (e.g. "Jane Doe / The Canadian Press"),
    which is printed as given.
    """
    depicts = esc(p["depicts"])
    if p.get("credit"):
        return f'{depicts}. Photo: {esc(p["credit"])}.'
    lic = (f'<a href="{esc(p["licenseUrl"])}">{esc(p["license"])}</a>' if p.get("licenseUrl") else esc(p["license"]))
    work = f'“{esc(p["title"])}” by {esc(p["author"])}' if p.get("title") else f'by {esc(p["author"])}'
    via = esc(p.get("via", "Wikimedia Commons"))
    source = f'<a href="{esc(p["filePage"])}">{via}</a>' if p.get("filePage") else via
    return f'{depicts}. Photo: {work}, {lic}, via {source} (cropped and resized).'


def photo_credits(html: str, by_id: dict) -> str:
    """Credits for the story photos on a finished page, numbered in the order they appear."""
    ids = dict.fromkeys(re.findall(r'assets/img/stories/(s\d+)(?:-lg|-sm)?\.webp', html))
    shown = [by_id[i] for i in ids if by_id.get(i, {}).get("photo")]
    if not shown:
        return ""
    items = "".join(f"<li>{credit_line(s['photo'])}</li>" for s in shown)
    agency = any(s["photo"].get("credit") for s in shown)
    intro = ("Where a freely licensed photo of a news event exists, the story shows it; otherwise the photo shows the "
             "place or subject involved. These are not the reporting outlets' own photos. We cropped and resized them, "
             "and our versions of CC BY-SA photos are shared under the same licence as the originals.")
    if agency:
        intro += " Photos credited to a news agency are used under licence and may not be reused."
    return ('<section class="photo-credits" aria-labelledby="photo-credits-title"><h2 id="photo-credits-title">Photo credits</h2>'
            f'<p>{esc(intro)}</p><ol>{items}</ol></section>')


# ------------------------------------------------------------------ build ----

def build() -> None:
    parts = {marker: (SRC / path).read_text(encoding="utf-8") for marker, path in MARKERS.items()}
    values = {key: escape(value, quote=True) for key, value in BRAND.items()}
    stories_file = SRC / "stories.json"
    page_blocks = {page: {} for page in PAGES}
    by_id = {}
    if stories_file.exists():
        data = json.loads(stories_file.read_text(encoding="utf-8"))
        by_id = {s["id"]: s for g in data["groups"].values() for s in g["stories"]}
        page_blocks["index.html"] = Homepage(data).render()
        page_blocks["article.html"] = Homepage(data).article()
    blocks = page_blocks["index.html"]

    # YEGToday's own stories (those with a `body`) each get a page made from src/story.html.
    templates = {page: page for page in PAGES}
    for s in by_id.values():
        if not s.get("body"):
            continue
        url = s.get("url", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.html", url) or url in templates:
            raise SystemExit(f"story {s['id']}: give it a page name of its own as its url, like 'porsche-crash.html'")
        templates[url] = "story.html"
        page_blocks[url] = Homepage(data).story_page(s)

    output = {}
    for page, template in templates.items():
        html = (SRC / template).read_text(encoding="utf-8")
        missing = [m for m in MARKERS if m not in html]
        if missing:
            raise SystemExit(f"src/{page}: missing markers {missing}")
        for marker, content in parts.items():
            html = html.replace(marker, content)
        for key, content in page_blocks[page].items():
            html = html.replace(f"<!--BLOCK:{key}-->", content)
        # Credits go in last, so they can follow the photos in the order the page shows them.
        html = html.replace("<!--BLOCK:credits-->", photo_credits(html, by_id))
        if "<!--BLOCK:" in html:
            start = html.index("<!--BLOCK:")
            raise SystemExit(f"src/{page}: no content for {html[start:start + 30]!r} (is src/stories.json present?)")
        # Mark the Home nav link as current only on the homepage.
        html = html.replace("{{HOME_CURRENT}}", ' aria-current="page"' if page == "index.html" else "")
        for key, value in values.items():
            html = html.replace("{{" + key + "}}", value)
        if "{{" in html:
            start = html.index("{{")
            raise SystemExit(f"src/{page}: unreplaced token near {html[start:start + 30]!r}")
        output[page] = html

    # Write only after every page built cleanly.
    for page, html in output.items():
        (ROOT / page).write_text(html, encoding="utf-8")
        print(f"wrote {page} ({len(html) // 1024} KB)")
    if blocks:
        print("homepage blocks: " + ", ".join(f"{k}{'' if v else ' (empty)'}" for k, v in blocks.items()))


if __name__ == "__main__":
    build()
