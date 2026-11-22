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
# Where each homepage block's "More ..." link goes, and which topic page a story's section belongs to
# (slugs from src/topics.json).
MORE_LINKS = {
    "edmonton": "edmonton", "st-albert": "st-albert", "sherwood-park": "strathcona-county", "tri-region": "tri-region",
    "south": "south", "north": "north", "crime": "crime", "business": "business", "sports": "sports",
    "living": "living", "history": "history", "opinion": "opinion", "neighbours": "neighbours",
}
SECTION_TOPIC = {**MORE_LINKS, "enoch": "enoch"}
TOPICS_FILE = SRC / "topics.json"
TOPIC_TEMPLATE = "topic.html"

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
        # article.html is the hand-written page for one story (leadId); links to that story go there.
        self.lead_href = data.get("leadHref", "")
        self.lead_id = data.get("leadId", "")
        leads = [s["id"] for s in stories if s.get("pin") == "lead"]
        if len(leads) > 1:
            raise SystemExit(f"src/stories.json: only one story can have \"pin\": \"lead\" (found {', '.join(leads)})")
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

    def href(self, s) -> str:
        # The story written up on article.html (leadId) links there everywhere; a story with its own page keeps it.
        if self.lead_href and s["id"] == self.lead_id and not s.get("body"):
            return esc(self.lead_href)
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
    def block(key, title, inner, more=None, title_extra="", href=None) -> str:
        # "More ..." goes to the matching topic page (src/topics.json); see MORE_LINKS.
        href = href or f"{MORE_LINKS.get(key, 'latest')}.html"
        more_html = (f'<a class="more-link" href="{esc(href)}">More {esc(more)} <span aria-hidden="true">&gt;</span></a>'
                     if more else "")
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
        href = self.href(lead)
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
                 f'<a class="more-link" href="latest.html">More Highlights <span aria-hidden="true">&gt;</span></a></div></div>')
        return f'<section class="block"><h2 class="block-title" id="sec-highlights">Highlights</h2>{inner}</section>'

    def trending(self) -> str:
        picks = sorted(self.pool(running=False, exclude=("history", "opinion")),
                       key=lambda s: (s.get("fun", 0), s["published"]), reverse=True)[:3]
        if len(picks) < 3:
            return ""
        items = "".join(
            f'<li><a class="story-link" href="{self.href(self.take(s))}">{self.media(s, "trend")}'
            f'<span class="rank" aria-hidden="true">{i} <svg aria-hidden="true"><use href="#i-trend"/></svg></span>'
            f'<h3 class="headline h-sm">{esc(s["headline"])}</h3><span class="meta">{self.meta(s)}</span></a></li>'
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

    def rows_block(self, key, sections, title, more, href=None) -> str:
        stories = [self.take(s) for s in self.pool(sections)[:4]]
        if key == "history":
            stories.sort(key=lambda s: s["published"])
        if not stories:
            return ""
        return self.block(key, title, '<div class="rows">' + "".join(self.row(s) for s in stories) + "</div>", more,
                          href=href)

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
        lead = next((s for s in self.all if s["id"] == self.lead_id), None) or next(iter(self.pinned("lead")), None)
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
        more = self.rows_block("more", ["edmonton"], "More Edmonton News", "Edmonton News", href="edmonton.html")
        return {"article-figure": figure, "article-more": more}

    def story_page(self, s, topics) -> dict:
        """Blocks for one of YEGToday's own stories (a story with a `body`), rendered from src/story.html.

        The breadcrumb, the "More ..." rows and their link all come from the same topic page, so they agree.
        """
        self.take(s)
        slug = SECTION_TOPIC.get(s["section"], "latest")
        title = topics.by_slug[slug]["title"]
        topic = f"{slug}.html"
        how = s.get("reported", "Reported by YEGToday")
        head = (
            '<nav aria-label="Breadcrumb"><ol class="crumbs"><li><a href="index.html">Home</a></li>'
            f'<li><a href="{topic}">{esc(title)}</a></li></ol></nav>'
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
                 'Spotted an error? <a href="about.html#contact">Tell us</a> or read our '
                 '<a href="about.html#corrections">corrections policy</a>.</div>'
                 if s.get("howReported") else "")
        self.eager = 0
        others = [x for x in topics.stories_for(slug) if x["url"] != s["url"]][:4]
        more = (self.block("more", f"More {title}", '<div class="rows">' + "".join(self.row(x) for x in others) + "</div>",
                           title, href=topic) if others else "")
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


# ----------------------------------------------------------------- topics ----

# Topic groups whose "All ..." page the breadcrumb links back to.
GROUP_HOME = {"communities": "communities", "sports": "sports", "business": "business",
              "opinion": "opinion", "crime": "crime"}


class Topics:
    """The topic pages and info pages described in src/topics.json."""

    def __init__(self, data: dict, spec: dict):
        self.data = data
        self.spec = spec
        self.place_of = spec["communityPlaces"]
        self.by_slug = {t["slug"]: t for t in spec["topics"]}
        self.stories = Homepage(data).all  # already de-duplicated by url
        self._found = {}
        for t in spec["topics"]:
            for ref in filter(None, [t.get("fallback")]):
                if ref not in self.by_slug:
                    raise SystemExit(f"src/topics.json: {t['slug']} falls back to unknown topic {ref!r}")
        # Catch typos in stories.json, which would otherwise quietly leave a story off its topic pages.
        tags = {tag for t in spec["topics"] for tag in t.get("tags", ())}
        slugs = set(self.place_of.values())
        problems = []
        for s in self.stories:
            for tag in s.get("topics", ()):
                if tag not in tags:
                    problems.append(f"{s['id']}: unknown topic tag {tag!r}")
            for place in s.get("places", ()):
                if place not in slugs:
                    problems.append(f"{s['id']}: unknown place {place!r}")
            if s.get("community") not in self.place_of and s.get("community") != "Region":
                problems.append(f"{s['id']}: community {s.get('community')!r} isn't in communityPlaces "
                                "(add it there, or use \"Region\" with a `places` list)")
        if problems:
            raise SystemExit("src/stories.json:\n  " + "\n  ".join(problems))

    def places(self, s) -> set:
        out = set(s.get("places", ()))
        if s.get("community") in self.place_of:
            out.add(self.place_of[s["community"]])
        return out

    def stories_for(self, slug) -> list:
        """Every story on a topic, newest first."""
        if slug not in self._found:
            t = self.by_slug[slug]
            sections, places, tags = set(t.get("sections", ())), set(t.get("places", ())), set(t.get("tags", ()))
            hits = [s for s in self.stories
                    if t.get("all") or s["section"] in sections or self.places(s) & places
                    or set(s.get("topics", ())) & tags]
            self._found[slug] = sorted(hits, key=lambda s: s["published"], reverse=True)
        return self._found[slug]

    def listed(self, group, skip=None):
        return [t for t in self.spec["topics"]
                if t["group"] == group and not t.get("hidden") and not t.get("hub") and t["slug"] != skip]

    @staticmethod
    def crumbs(*items) -> str:
        parts = "".join(f'<li><a href="{esc(href)}">{esc(label)}</a></li>' for label, href in items)
        return f'<nav aria-label="Breadcrumb"><ol class="crumbs"><li><a href="index.html">Home</a></li>{parts}</ol></nav>'

    def topic_page(self, t) -> dict:
        page = Homepage(self.data)  # fresh, so every matching story can be shown
        home = GROUP_HOME.get(t["group"])
        trail = [(self.by_slug[home]["title"], f"{home}.html")] if home and home != t["slug"] else []
        head = (self.crumbs(*trail) + f'<h1 class="article-title">{esc(t["title"])}</h1>'
                f'<p class="article-dek">{esc(t["intro"])}</p>')
        body = ""
        if t.get("hub"):
            links = "".join(f'<li><a href="{o["slug"]}.html">{esc(o["title"])}</a></li>' for o in self.listed(t["group"]))
            body += page.block("communities", "Pick a community", f'<ul class="hub-links">{links}</ul>')
        stories = self.stories_for(t["slug"])
        if stories:
            title = "Latest from around the region" if t.get("hub") else "Latest stories"
            body += page.block("topic", title, page.cards_and_rows(stories, len(stories)))
        else:
            note = t.get("empty") or f"We don't have any {t['title']} stories yet."
            body += f'<p class="topic-empty">{esc(note)}</p>'
            fb = t.get("fallback", "latest")
            more = self.stories_for(fb)[:6]
            if more:
                label = self.by_slug[fb]["title"]
                body += page.block("topic", "Latest news" if fb == "latest" else f"More from {label}",
                                   page.cards_and_rows(more, 4), more="news" if fb == "latest" else label,
                                   href=f"{fb}.html")
        group_label = self.spec["groups"][t["group"]]
        rail_title = group_label if t["group"] == "more" else f"More in {group_label}"
        items = "".join(
            f'<li><a href="{o["slug"]}.html"><span>{esc(o["title"])}</span>'
            f'<span class="count">{count(len(self.stories_for(o["slug"])))}</span></a></li>'
            for o in self.listed(t["group"], skip=t["slug"]))
        rail = (f'<section class="rail-block"><h2 class="block-title">{esc(rail_title)}</h2>'
                f'<ul class="topic-links">{items}</ul></section>') if items else ""
        return {"page-title": esc(t["title"]), "page-description": esc(t["intro"]), "page-head": head,
                "page-body": body, "page-rail": rail}

    def info_page(self, p) -> dict:
        head = self.crumbs() + f'<h1 class="article-title">{esc(p["title"])}</h1><p class="article-dek">{esc(p["intro"])}</p>'
        sections = "".join(
            f'<section class="info-section" id="{esc(sec["id"])}"><h2>{esc(sec["heading"])}</h2>'
            + "".join(f"<p>{esc(par)}</p>" for par in sec["body"]) + "</section>"
            for sec in p["sections"])
        toc = "".join(f'<li><a href="#{esc(sec["id"])}"><span>{esc(sec["heading"])}</span></a></li>' for sec in p["sections"])
        rail = (f'<section class="rail-block"><h2 class="block-title">On this page</h2>'
                f'<ul class="topic-links">{toc}</ul></section>')
        return {"page-title": esc(p.get("docTitle") or p["title"]), "page-description": esc(p["intro"]), "page-head": head,
                "page-body": f'<div class="article-body">{sections}</div>', "page-rail": rail}


def count(n: int) -> str:
    """A story count for the topic rail: the number shows, the word is for screen readers."""
    return f'{n}<span class="sr-only"> {"story" if n == 1 else "stories"}</span>'


def check_links(output: dict) -> list:
    """Every link and image on a built page must point at a built page (and an id on it) or a file that exists."""
    ids = {page: set(re.findall(r'\bid="([^"]+)"', html)) for page, html in output.items()}
    problems = []
    for page, html in output.items():
        urls = re.findall(r'\b(?:href|src)="([^"]*)"', html)
        urls += [part.split()[0] for srcset in re.findall(r'\bsrcset="([^"]*)"', html) for part in srcset.split(",")]
        for url in dict.fromkeys(urls):
            if re.match(r"[a-z][a-z0-9+.-]*:|//", url):
                continue  # another site (https:, mailto:, ...)
            path, _, frag = url.partition("#")
            path = path.split("?")[0]
            target = path or page
            if not path and not frag:
                problems.append(f"{page}: empty link {url!r}")
            elif target in output:
                if frag and frag not in ids[target]:
                    problems.append(f"{page}: {url!r} has no #{frag} to land on")
            elif path.endswith(".html"):
                # Pages must come from this build; an old .html left on disk doesn't count.
                problems.append(f"{page}: {url!r} isn't a page this build makes")
            elif not (ROOT / path).is_file():
                problems.append(f"{page}: {url!r} doesn't exist")
    return problems


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

    templates = {page: page for page in PAGES}
    topics = None
    if stories_file.exists() and TOPICS_FILE.exists():
        topics = Topics(data, json.loads(TOPICS_FILE.read_text(encoding="utf-8")))

    # YEGToday's own stories (those with a `body`) each get a page made from src/story.html.
    for s in by_id.values():
        if not s.get("body"):
            continue
        url = s.get("url", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.html", url) or url in templates:
            raise SystemExit(f"story {s['id']}: give it a page name of its own as its url, like 'porsche-crash.html'")
        if topics is None:
            raise SystemExit(f"story {s['id']}: story pages need src/topics.json for their breadcrumb and 'More' links")
        templates[url] = "story.html"
        page_blocks[url] = Homepage(data).story_page(s, topics)

    # Topic pages (one per menu topic) and info pages (About, Obituaries) from src/topics.json.
    if topics:
        made = [(t["slug"], topics.topic_page(t)) for t in topics.spec["topics"]]
        made += [(p["slug"], topics.info_page(p)) for p in topics.spec["pages"]]
        for slug, page_html in made:
            url = f"{slug}.html"
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug) or url in templates:
                raise SystemExit(f"src/topics.json: {slug!r} is not a usable page name, or another page already uses it")
            templates[url] = TOPIC_TEMPLATE
            page_blocks[url] = page_html

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
        # Mark the Home nav link as current only on the homepage, and on other pages any menu link to the page itself.
        html = html.replace("{{HOME_CURRENT}}", ' aria-current="page"' if page == "index.html" else "")
        if page != "index.html":
            html = re.sub(rf'href="{re.escape(page)}"(?! aria-current)', f'href="{page}" aria-current="page"', html)
        for key, value in values.items():
            html = html.replace("{{" + key + "}}", value)
        if "{{" in html:
            start = html.index("{{")
            raise SystemExit(f"{page} (from src/{template}): unreplaced token near {html[start:start + 30]!r}")
        output[page] = html

    problems = check_links(output)
    if problems:
        raise SystemExit("broken links, nothing written:\n  " + "\n  ".join(problems))

    # Write only after every page built cleanly.
    for page, html in output.items():
        (ROOT / page).write_text(html, encoding="utf-8")
    made = {"story": sum(t == "story.html" for t in templates.values()),
            "topic and info": sum(t == TOPIC_TEMPLATE for t in templates.values())}
    print(f"wrote {len(output)} pages: {', '.join(PAGES)}, {made['story']} story page(s), "
          f"{made['topic and info']} topic and info pages; all links check out")
    stale = sorted(p.name for p in ROOT.glob("*.html") if p.name not in output)
    if stale:
        print("note: these pages are no longer built and nothing links to them; delete them: " + ", ".join(stale))
    if blocks:
        print("homepage blocks: " + ", ".join(f"{k}{'' if v else ' (empty)'}" for k, v in blocks.items()))


if __name__ == "__main__":
    build()
