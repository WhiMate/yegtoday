# YEGToday — Edmonton & area news (design prototype)

A static, clickable prototype for an independent news site covering Edmonton and the
communities around it. The layout follows [SaskToday.ca](https://www.sasktoday.ca/) as requested.
The logo is yours (traced to `assets/img/yegtoday-logo.svg`; the original is kept as
`yegtoday-logo-original.webp`). The colours, icons and illustrations are original; the story
photos are freely licensed images from Wikimedia Commons and Flickr, credited on each page (see Photos below).

Open `index.html` (homepage) or `article.html` (story page) in a browser, or serve the folder:

```bash
python3 -m http.server 8123
```

## News content

The homepage carries **63 real Edmonton-region stories published Oct. 23 – Nov. 20, 2026**. Each one is
summarized in our own words and links to the outlet that reported it (CTV, CBC, the Journal, Global, Daily Hive,
Sherwood Park News, Taproot, TSN and others). Every item was fact-checked against its source page for the
date, facts and original wording, and one that couldn't be verified was dropped. The lead story
(`article.html`) is a short YEGToday summary of CBC News's report, with links to the original.

Still placeholders: obituaries (no real people's notices), the poll results, the weather box and
the ads.

To update the news, edit `src/stories.json` and run `python3 build.py`. Each story has `headline`,
`dek`, `section` (which homepage block it goes in), `community`, `published`, `source`, `url`, `scene`
(fallback illustration), `fun` (1–5, used to pick Trending) and an optional `photo`. Set `"pin": "lead"` or
`"pin": "highlights"` to choose the top stories yourself.

## Photos

Story photos are real, freely licensed pictures of the places and subjects in each story (and of the event
itself where one exists), mostly from Wikimedia Commons, with two from Flickr. They are **not** the news
outlets' own photos, which are copyrighted. Every licence was checked at its source and only CC0, public
domain or no-known-restrictions archive photos, CC BY and CC BY-SA files were used. NC, ND
and GFDL-only files were left out, and so were photos of murals, because Canada's freedom of panorama
covers buildings and sculptures but not murals. Each was also checked by eye so a picture doesn't suggest
something it doesn't show. For example, a Christmas house from another city wasn't used for the Griswold
House story, so that one keeps its illustration.

- Files are 800×533 WebP crops in `assets/img/stories/` (`<id>.webp`), each with a 400×267 `<id>-sm.webp`
  that thumbnails and phones pick through `srcset`, plus `s03-lg.webp` (1280×853) for the article hero.
- Each story's `photo` in `src/stories.json` holds `src`, `depicts` (what the photo shows, in our words),
  `title` (the source's title), `author`, `license`, `licenseUrl` and `filePage` (the source page). `via`
  names the source when it isn't Wikimedia Commons (e.g. `"Flickr"`), and `kind` notes whether the photo
  shows the `event` or the `subject`. The lead also has `hero` and an optional `alt` (a visual description).
- `build.py` prints a numbered **Photo credits** list at the bottom of each page, in the order the photos
  appear, with this pattern: *What it shows. Photo: "Title" by Author, Licence, via Wikimedia Commons
  (cropped and resized).* The intro notes that our crops of CC BY-SA photos are shared under the same licence.
  The article hero carries the same credit in its caption.
- A story without a `photo` falls back to its illustrated `scene`. Two stories use that on purpose: the
  Griswold House (no fair photo) and the Spruce Grove first responders' game on ice (its only option was a
  near-copy of the Leduc grain elevator photo).
- After a review pass, a few photos were swapped or recropped. The Duchess Bake Shop story had a baker
  identifiable in a controversy story, and the pierogi-farm story showed an unrelated farm; both now use
  plain food photos. Other recrops removed a plane engine, another restaurant's name on a plate, and a white
  edge.

### News (event) photos

On 2026-11-21 we searched for freely licensed photos of the actual events in all 63 stories: Wikimedia
Commons, Openverse, Flickr's licence-filtered search and tag feeds, and government photo accounts. Each
candidate was then re-checked at its source by a second reviewer. **Almost none exist.** The Government of Alberta,
Legislative Assembly and City of Edmonton Flickr accounts are non-commercial or all rights reserved, no
Creative Commons photographer covered the Grey Cup, the Elks' rally or the snowfall, and Openverse's index
stops around August 2026. Two stories got better photos:

- **Nov. 27, 1954 Grey Cup (history):** a real photo from that day of Edmonton fans cheering at the radio
  broadcast, by Frank Oliver Studios, from the Provincial Archives of Alberta's Flickr Commons collection
  ("No known copyright restrictions").
- **Mexico City freighter route:** the actual airline's A330 freighter (at LAX, Feb. 2026, CC BY-SA 4.0 on
  Flickr), instead of an unrelated cargo jet.

Everything else keeps its place or subject photo. Real photos of current events have to come from a news
agency licence (for example The Canadian Press Images or Getty Images editorial), a deal with a local
outlet, or your own photographer. To add one, put the crop in `assets/img/stories/<id>.webp` (800×533, plus
`<id>-sm.webp` at 400×267) and give the story a `photo` like this:

```json
"photo": {
  "src": "assets/img/stories/s43.webp",
  "depicts": "Elks quarterback Cody Fajardo lifts the Grey Cup in Calgary, Nov. 15, 2026",
  "credit": "Jane Doe / The Canadian Press",
  "kind": "event"
}
```

`credit` is printed as given, in place of the Creative Commons credit. When any agency photo is on a page,
the credits intro adds that those photos are used under licence and can't be reused. Keep the licence
terms and expiry dates for each one somewhere outside the site.

---

## Name

**Chosen: YEGToday** (your pick, 2026-11-20). yegtoday.ca and yegtoday.news were unregistered on
that date. yegtoday.com is registered but serves no site.

Things to check before launch:
- **"YEG"** is Edmonton International Airport's code and brand ("YEG Edmonton International Airport").
  Plenty of local businesses use it, but have a trademark agent look at CIPO for YEG marks.
- **"-Today"** is the naming pattern of the SaskToday network (Village Media) and of other Alberta
  outlets (Town & Country Today, Todayville, Fort McMurray Today). Combined with a layout modelled on
  SaskToday, readers may assume YEGToday is part of that network. A distinctive logo and colours (already
  original here) help; get legal advice on passing-off before launch.
- Register the domains and the @yegtoday social handles the same day.

## Shortlisted alternatives

Two rounds: about 70 unique names from 7 independent angles, scored by three judges
(brand strength · local resonance · collision risk), then trademark/media/handle checks on the top 8.
Domains checked on 2026-11-20 via the .ca registry (CIRA), Verisign (.com) and RDAP (.news).

| Rank | Name | Tagline | Scores (brand/local/risk) | Collision check | Free domains |
|---|---|---|---|---|---|
| 1 | **The Sundog** | The region's watchdog, in plain sight. | 8 / 7 / 5 | Caution — SUNDOG marks exist for beer and sunglasses (not news); Sundog Organic Farm is in Sturgeon County; "Sun" echoes the Edmonton Sun | thesundog.ca, sundog.news, sundognews.ca |
| 2 | **Coldlight** | News in the cold light of day. | 6 / 6 / 8 | Clear (no Canadian marks or media found); coldlight.com is a gambling site | coldlight.ca, coldlight.news |
| 3 | **Riverwire** | Edmonton and region, as it happens. | 7 / 6 / 7 | Clear, but riverwire.ca belongs to a wiring company | riverwire.news, riverwirenews.ca |
| 4 | **Winterwire** | Edmonton region news, all year round. | 6 / 5 / 8 | Clear | winterwire.ca, winterwire.news |
| 5 | **Waxwing** | News that travels town to town. | 7 / 5 / 7 | Mild caution — Shimano fishing-lure and Quebec gin marks; often misheard as "waxing" | waxwing.news, waxwingnews.ca |

**Why The Sundog:** sun dogs hang over Leduc, Morinville and downtown on the same −25° morning, so the
name covers the whole region — unlike river names, which leave out half the towns. "Sundog" carries a
built-in *watchdog* meaning, gives you a ready-made logo (a sun flanked by its two sun dogs), and fits
the Canadian animal-and-place naming pattern of The Narwhal and The Tyee. Always use "The Sundog"
(sundog.ca is taken).

**Safest alternative:** Coldlight — nothing found in Canada and the exact .ca is free, but it reads
cooler and less neighbourly.

**Ruled out by the naming research (before you chose YEGToday):** anything with *Today* (Todayville, Town & Country Today, the Edmonton News Today podcast),
*YEG* (the airport's brand), *Capital*, *Gateway*, *High Level* (a town in northern Alberta), *Journal*,
*Gazette*, *Record*, *Examiner* or "[Place] News" (all taken in the region); Kestrel (slang for
ketamine, crowded register); Earshot (the national campus-radio chart !earshot).

**Before you commit:** have a trademark agent search CIPO in classes 16, 38 and 41 (an agent couldn't
run every check), and register the domains and social handles the same day.

To swap the name everywhere, edit `BRAND` at the top of `build.py` and run `python3 build.py`.

---

## Design (matched to SaskToday's layout)

| Element | Spec |
|---|---|
| Page | Light grey `#f0f0f0` page, one 990px white card (8px radius), 630px story column + 300px right rail split by a 1px rule |
| Header | Sticky white bar: wordmark left, "Sign in or register for your free account" + round avatar right; nav row below with a small coloured icon per section and ▾ dropdowns, then search |
| Section labels | 12.6px bold uppercase with a 1px black rule above (HIGHLIGHTS, TRENDING NOW, …) |
| Type | Source Sans 3 throughout · lead headline 28px · card 21px · row 17px · body 14px `#333` · article body 17.5/28px |
| Colour | From the logo: ink `#070707` and dot red `#f60202`; UI red `#d90000` for buttons and badges (dark enough for AA text contrast); link blue `#1665a8` |
| Homepage order | Highlights (lead with category badge + 3 headlines) → Trending Now (ranked) → Edmonton News → Winter Storm Watch strip → St. Albert → This Month in History → Sherwood Park & Strathcona → Community Discussion → Newsletters carousel → Crime → Business & Energy → Spruce Grove/Stony Plain/Parkland → Leduc/Beaumont/Devon → Fort Sask/Morinville/Sturgeon → Sports → Opinion → Edmonton Living → Meet Your Neighbours |
| Right rail | Ad · Edmonton weather · "Your Vote Matters" poll · "We Remember" obituaries · ad · sticky skyscraper |
| Article page | Breadcrumb → 37px headline → dek → byline with Share + newsletter buttons → hero + caption → "Listen to this article" → body with fact box, pull quote and in-story ad → topic tags → "How we reported this" note → comments → More Edmonton News |
| Mobile | Below 1000px the nav becomes a slide-in drawer; below 860px the rail stacks; below 600px everything is one column with thumbnail rows |

Edmonton-specific additions on top of the SaskToday pattern: communities for all 12+ municipalities
around the city (the biggest gap in local coverage), a weather box, a Council Tracker newsletter, and a
"How we reported this" trust note on stories.

Accessibility and behaviour were audited and fixed: keyboard-operable menus with Escape and
focus handling, a focus-trapped and `inert`-backed mobile drawer, WCAG AA contrast on text, 24px
minimum targets, reduced-motion support, and a no-JavaScript fallback.

## Files

```
index.html, article.html     built pages (don't edit — run build.py)
src/index.html, src/article.html   page sources (homepage blocks are <!--BLOCK:...--> markers)
src/stories.json             the news: verified stories that fill the homepage blocks
src/partials/                header, footer, SVG sprite (icons + fallback illustrations)
assets/img/                  logo (SVG trace + your original)
assets/img/stories/          story photos (Commons and Flickr, credited on the page)
assets/css/styles.css        all styles; colour tokens at the top
assets/js/main.js            menus, drawer, search, poll, newsletters, share/listen
build.py                     assembles the pages, lays out the stories, fills in the brand
```

## Next steps

- Pick the name, register the domains and handles, and get a trademark search.
- Get news photos of current events: a news agency licence (The Canadian Press Images, Getty editorial),
  a photo-sharing deal with a local outlet, or your own photographer. They drop in with a `credit` field
  (see News photos above). No freely licensed photos of these Oct.–Nov. 2026 events exist yet.
- Before going public with aggregated headlines, settle a linking/summary policy, and ideally
  syndication deals, with the outlets you draw from. Original reporting is what will set YEGToday apart.
- Move the templates into a CMS (WordPress, Ghost or a headless CMS) — the layout maps directly to
  homepage "blocks" per community and topic.
