#!/usr/bin/env python3
"""
Build script for ivorbenko.com (static, bilingual EN/HR).

    pip install markdown pillow
    python build.py          -> writes the finished site into ../site

New blog post: add a .md file to content/en/ and/or content/hr/ (copy an
existing one for the front matter). Posts that share the same `key` are
linked as translations of each other. Categories: sailing, skiing (add more
in CATEGORIES below).
"""
import html, json, re, shutil, datetime as dt
from pathlib import Path
import markdown
from markdown.extensions.toc import slugify_unicode

# ---------------------------------------------------------------- settings
SITE = "https://ivorbenko.com"
NAME = "Ivor Benko"
EMAIL = "ivorbenko0@gmail.com"
PHONE = "+385 99 590 7887"
PHONE_E164 = "+385995907887"
WHATSAPP = True          # set False if this number is not on WhatsApp
# Add your public profiles here (Instagram, LinkedIn, Facebook, YouTube,
# charter-platform profiles...). This is the single most important thing
# for AI search engines to connect "Ivor Benko" across the web.
SAME_AS = [
    # "https://www.instagram.com/…",
    # "https://www.linkedin.com/in/…",
]

ROOT = Path(__file__).parent
OUT = ROOT.parent / "site"
TODAY = dt.date.today().isoformat()

LANGS = ("en", "hr")
LOCALE = {"en": "en_US", "hr": "hr_HR"}
PAGES = {
    "home":    {"en": "/",         "hr": "/hr/"},
    "skipper": {"en": "/skipper/", "hr": "/hr/skiper/"},
    "about":   {"en": "/about/",   "hr": "/hr/o-meni/"},
    "blog":    {"en": "/blog/",    "hr": "/hr/blog/"},
}
CATEGORIES = {
    "sailing": {"en": "Sailing", "hr": "Jedrenje"},
    "skiing":  {"en": "Skiing",  "hr": "Skijanje"},
}
MONTHS_HR = ["siječnja", "veljače", "ožujka", "travnja", "svibnja", "lipnja", "srpnja",
             "kolovoza", "rujna", "listopada", "studenoga", "prosinca"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]

T = {
    "en": {
        "skip": "Skip to content", "skipper": "Skipper", "about": "About", "blog": "Blog",
        "other": "Hrvatski", "other_lang": "hr", "home": "Home",
        "read": "min read", "short": "Short answer", "by": "Written by",
        "author_bio": "Skipper on sailboats and catamarans in Croatia since 2020, ISIA ski instructor and web developer from Zagreb.",
        "more_posts": "More from the blog", "all_posts": "All posts",
        "coming": "Skiing posts are coming soon. For now, the blog is about sailing.",
        "translation": "Pročitaj na hrvatskom",
        "foot_role": "Skipper on sailboats and catamarans in Croatia",
        "foot_contact": "Contact", "foot_pages": "Pages",
        "email": "Email", "phone": "Phone", "whatsapp": "WhatsApp", "base": "Based in",
        "base_v": "Zagreb, Croatia", "write": "Send an email",
    },
    "hr": {
        "skip": "Preskoči na sadržaj", "skipper": "Skiper", "about": "O meni", "blog": "Blog",
        "other": "English", "other_lang": "en", "home": "Početna",
        "read": "min čitanja", "short": "Ukratko", "by": "Autor",
        "author_bio": "Skiper na jedrilicama i katamaranima u Hrvatskoj od 2020., ISIA instruktor skijanja i web developer iz Zagreba.",
        "more_posts": "Još s bloga", "all_posts": "Svi tekstovi",
        "coming": "Tekstovi o skijanju stižu uskoro. Za sada je blog o jedrenju.",
        "translation": "Read in English",
        "foot_role": "Skiper na jedrilicama i katamaranima u Hrvatskoj",
        "foot_contact": "Kontakt", "foot_pages": "Stranice",
        "email": "E-mail", "phone": "Telefon", "whatsapp": "WhatsApp", "base": "Baza",
        "base_v": "Zagreb, Hrvatska", "write": "Pošalji e-mail",
    },
}

SAILBOATS = ["Bénéteau First 45", "Bavaria 46", "Dufour 46"]
CATAMARANS = ["Lagoon 42", "Lagoon 450", "Lagoon 46"]

# ---------------------------------------------------------------- helpers
esc = html.escape

def fmt_date(iso, lang):
    d = dt.date.fromisoformat(iso)
    return f"{d.day}. {MONTHS_HR[d.month-1]} {d.year}." if lang == "hr" else f"{d.day} {MONTHS_EN[d.month-1]} {d.year}"

def post_path(lang, slug):
    return f"/blog/{slug}/" if lang == "en" else f"/hr/blog/{slug}/"

def abs_url(p): return SITE + p

# ---------------------------------------------------------------- posts
def load_posts():
    posts = {l: [] for l in LANGS}
    md = markdown.Markdown(extensions=["extra", "sane_lists", "toc", "smarty"],
                           extension_configs={"toc": {"slugify": slugify_unicode}})
    for lang in LANGS:
        for f in sorted((ROOT / "content" / lang).glob("*.md")):
            raw = f.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
            meta = {}
            for line in m.group(1).splitlines():
                k, v = line.split(":", 1)
                v = v.strip()
                if v.startswith('"') and v.endswith('"'): v = v[1:-1]
                meta[k.strip()] = v
            body = m.group(2).strip()
            md.reset()
            meta.update(lang=lang, body_md=body, html=md.convert(body),
                        words=len(re.findall(r"\w+", body)),
                        path=post_path(lang, meta["slug"]))
            meta.setdefault("updated", meta["date"])
            posts[lang].append(meta)
        posts[lang].sort(key=lambda p: p["date"], reverse=True)
    return posts

POSTS = load_posts()

def twin(post):
    other = "hr" if post["lang"] == "en" else "en"
    return next((p for p in POSTS[other] if p["key"] == post["key"]), None)

# ---------------------------------------------------------------- structured data
def person(lang):
    desc = {
        "en": "Ivor Benko is a Croatian skipper from Zagreb who has captained sailboats and catamarans on private and charter trips in the Adriatic Sea since 2020. He is also a licensed ISIA ski instructor and builds websites and apps.",
        "hr": "Ivor Benko je hrvatski skiper iz Zagreba koji od 2020. vodi jedrilice i katamarane na privatnim i charter plovidbama po Jadranu. Također je licencirani ISIA instruktor skijanja i izrađuje web stranice i aplikacije.",
    }[lang]
    p = {
        "@type": "Person", "@id": SITE + "/#person",
        "name": NAME, "givenName": "Ivor", "familyName": "Benko",
        "url": SITE + "/", "mainEntityOfPage": abs_url(PAGES["about"][lang]),
        "image": {"@type": "ImageObject", "url": SITE + "/assets/ivor-benko.jpg", "width": 240, "height": 240},
        "jobTitle": "Skipper" if lang == "en" else "Skiper",
        "description": desc,
        "email": "mailto:" + EMAIL, "telephone": PHONE_E164,
        "address": {"@type": "PostalAddress", "addressLocality": "Zagreb", "addressCountry": "HR"},
        "workLocation": {"@type": "Place", "name": "Adriatic Sea, Croatia"},
        "knowsLanguage": [
            {"@type": "Language", "name": "Croatian", "alternateName": "hr"},
            {"@type": "Language", "name": "English", "alternateName": "en"},
            {"@type": "Language", "name": "German", "alternateName": "de"}],
        "knowsAbout": ["Sailing", "Yacht skippering", "Catamaran sailing", "Yacht charter in Croatia",
                       "Adriatic Sea weather", "Bura (bora) wind", "Jugo (sirocco) wind", "Maestral wind",
                       "Kornati National Park", "Laser dinghy sailing", "Windsurfing", "Regatta sailing",
                       "Sailing instruction", "Skiing", "Ski instruction", "Kinesiology",
                       "Web development", "App development", "Digital marketing", "Copywriting"],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Faculty of Kinesiology, University of Zagreb",
                     "alternateName": "Kineziološki fakultet Sveučilišta u Zagrebu", "url": "https://www.kif.unizg.hr/"},
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential", "name": "Croatian boat licence, category C (voditelj brodice kategorije C)", "credentialCategory": "licence"},
            {"@type": "EducationalOccupationalCredential", "name": "Sail Week skipper academy course, completed with an A grade", "credentialCategory": "certificate", "dateCreated": "2024"},
            {"@type": "EducationalOccupationalCredential", "name": "ISIA ski instructor licence", "credentialCategory": "licence",
             "recognizedBy": {"@type": "Organization", "name": "International Ski Instructors Association (ISIA)"}}],
        "hasOccupation": [
            {"@type": "Occupation", "name": "Skipper", "description": "Captain and skipper on sailboats and catamarans for private guests and charters",
             "occupationLocation": {"@type": "Country", "name": "Croatia"}},
            {"@type": "Occupation", "name": "Ski instructor"},
            {"@type": "Occupation", "name": "Web and app developer"}],
    }
    if SAME_AS: p["sameAs"] = SAME_AS
    return p

def website():
    return {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME,
            "inLanguage": ["en", "hr"], "publisher": {"@id": SITE + "/#person"}}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(u)} for i, (n, u) in enumerate(items)]}

def webpage(lang, path, title, desc, typ="WebPage", extra=None):
    d = {"@type": typ, "@id": abs_url(path) + "#webpage", "url": abs_url(path), "name": title,
         "description": desc, "inLanguage": lang, "isPartOf": {"@id": SITE + "/#website"},
         "about": {"@id": SITE + "/#person"}, "dateModified": TODAY}
    if extra: d.update(extra)
    return d

# ---------------------------------------------------------------- layout
def head(lang, path, alt, title, desc, ld, og_type="website", og_image="/assets/og-image.jpg", extra_meta=""):
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{abs_url(u)}">' for l, u in alt.items())
    if "en" in alt: alts += f'<link rel="alternate" hreflang="x-default" href="{abs_url(alt["en"])}">'
    other = "hr" if lang == "en" else "en"
    oga = f'<meta property="og:locale:alternate" content="{LOCALE[other]}">' if other in alt else ""
    feed = "/blog/feed.xml" if lang == "en" else "/hr/blog/feed.xml"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{NAME}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{abs_url(path)}">
{alts}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{abs_url(path)}">
<meta property="og:image" content="{abs_url(og_image)}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{LOCALE[lang]}">{oga}
<meta name="twitter:card" content="summary_large_image">
{extra_meta}
<meta name="theme-color" content="#0F2D40">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{NAME} — Blog ({lang.upper()})" href="{feed}">
<link rel="preload" href="/assets/fonts/newsreader.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{T[lang]["skip"]}</a>
"""

def header(lang, current, alt):
    t = T[lang]
    def nav(key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{PAGES[key][lang]}"{cur}>{t[key]}</a>'
    other = t["other_lang"]
    switch = f'<a class="lang" href="{alt[other]}" hreflang="{other}" lang="{other}">{t["other"]}</a>' if other in alt else ""
    return f"""<header class="site-head"><div class="wrap">
<a class="brand" href="{PAGES['home'][lang]}">{NAME}</a>
<nav class="nav" aria-label="{'Glavna navigacija' if lang == 'hr' else 'Main navigation'}">{nav('skipper')}{nav('about')}{nav('blog')}</nav>
{switch}
</div></header>
<main id="main">
"""

def footer(lang):
    t = T[lang]
    wa = f'<p><a href="https://wa.me/{PHONE_E164[1:]}">WhatsApp</a></p>' if WHATSAPP else ""
    social = "".join(f'<p><a href="{u}" rel="me">{esc(u.split("//")[-1].split("/")[0].replace("www.", ""))}</a></p>' for u in SAME_AS)
    return f"""</main>
<footer class="site-foot"><div class="wrap">
<div><p><strong>{NAME}</strong></p><p>{t['foot_role']}</p><p>{t['base_v']}</p></div>
<div><p><strong>{t['foot_contact']}</strong></p><p><a href="mailto:{EMAIL}">{EMAIL}</a></p><p><a href="tel:{PHONE_E164}">{PHONE}</a></p>{wa}{social}</div>
<div><p><strong>{t['foot_pages']}</strong></p><p><a href="{PAGES['skipper'][lang]}">{t['skipper']}</a></p><p><a href="{PAGES['about'][lang]}">{t['about']}</a></p><p><a href="{PAGES['blog'][lang]}">{t['blog']}</a></p></div>
</div></footer>
</body>
</html>
"""

def contact_block(lang, anchor):
    t = T[lang]
    copy = {
        "en": ("Planning a week at sea?", "Tell me your dates, the boat or charter company if you already have one, how many of you there are and what kind of week you'd like. I'll reply with my availability."),
        "hr": ("Planirate tjedan na moru?", "Javite mi termin, brod ili charter tvrtku ako ih već imate, koliko vas je i kakav tjedan želite. Odgovorit ću vam s dostupnošću."),
    }[lang]
    wa = f'<dt>{t["whatsapp"]}</dt><dd><a href="https://wa.me/{PHONE_E164[1:]}">{PHONE}</a></dd>' if WHATSAPP else ""
    subject = "Skipper%20enquiry" if lang == "en" else "Upit%20za%20skipera"
    return f"""<section class="section" id="{anchor}" aria-labelledby="{anchor}-h"><div class="contact">
<img class="portrait" src="/assets/ivor-benko.jpg" width="240" height="240" alt="{NAME}" loading="lazy">
<div><h2 id="{anchor}-h">{copy[0]}</h2><p>{copy[1]}</p>
<dl class="kv"><dt>{t['email']}</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
<dt>{t['phone']}</dt><dd><a href="tel:{PHONE_E164}">{PHONE}</a></dd>{wa}
<dt>{t['base']}</dt><dd>{t['base_v']}</dd></dl>
<div class="actions"><a class="btn" href="mailto:{EMAIL}?subject={subject}">{t['write']}</a></div></div>
</div></section>"""

def post_list(lang, posts):
    items = "".join(f'<li><a href="{p["path"]}"><time datetime="{p["date"]}">{fmt_date(p["date"], lang)}</time>'
                    f'<span><span class="t">{esc(p["title"])}</span><span class="s">{esc(p["description"])}</span></span></a></li>'
                    for p in posts)
    return f'<ul class="posts">{items}</ul>'

# ---------------------------------------------------------------- the chart (hero)
def chart_svg(lang):
    W, H, M = 640, 520, 26
    islands = [
        # Kornat-like long island, NW–SE
        "M150 150 C190 160 260 210 330 270 C380 312 430 350 438 372 C442 384 428 386 414 378 C370 350 300 300 240 250 C200 216 160 190 142 168 C134 158 140 148 150 150Z",
        "M262 108 C302 118 362 158 402 194 C422 212 426 228 412 229 C382 227 342 196 302 170 C272 150 248 132 251 118 C253 112 257 108 262 108Z",
        "M170 272 C190 274 220 290 232 306 C238 316 226 318 214 312 C196 302 176 290 168 282 C162 276 164 270 170 272Z",
        "M252 362 C272 364 300 380 306 392 C310 400 298 402 286 396 C270 388 254 378 248 370 C244 364 246 360 252 362Z",
        "M100 228 C115 226 130 236 128 244 C126 250 112 250 102 244 C94 240 94 230 100 228Z",
        "M458 150 C472 150 490 162 488 170 C486 176 470 174 460 168 C452 163 450 152 458 150Z",
        # Murter + mainland on the right edge
        "M520 250 C545 236 590 228 624 230 L624 302 C600 300 570 294 548 288 C528 283 510 270 520 250Z",
        "M566 16 L624 16 L624 196 C610 178 592 156 584 126 C576 96 566 62 566 16Z",
    ]
    islets = [(360, 424, 6, 3), (470, 444, 5, 3), (206, 384, 4, 3), (92, 322, 5, 3), (512, 194, 4, 2), (60, 190, 4, 3)]
    shoal = "".join(f'<path class="shoal" d="{d}" stroke-width="34"/>' for d in islands)
    contour = "".join(f'<path d="{d}" fill="none" stroke="#8FBDB9" stroke-width="42" stroke-dasharray="2 4"/>'
                      f'<path d="{d}" fill="none" stroke="#FAFBF8" stroke-width="40"/>' for d in islands)
    land = "".join(f'<path class="land" d="{d}"/>' for d in islands) + "".join(
        f'<ellipse class="land" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>' for x, y, rx, ry in islets)
    route = ("M522 282 C502 306 486 332 466 346 C440 318 400 274 360 250 C330 232 290 208 240 172 "
             "C210 150 170 118 140 130 C112 140 108 176 138 210 C150 240 128 290 150 316 "
             "C166 336 200 340 240 342 C290 344 330 346 368 364 C392 376 396 398 430 406 "
             "C470 414 500 392 510 360 C518 336 520 310 522 282")
    stops = [(466, 346), (240, 172), (138, 210)]
    stops_svg = "".join(f'<circle class="stop" cx="{x}" cy="{y}" r="6"/>' for x, y in stops)
    # graduated latitude/longitude border, as on a sea chart
    grad = []
    for i, x in enumerate(range(M, W - M, 24)):
        if i % 2 == 0:
            grad.append(f'<rect class="grad" x="{x}" y="{M - 6}" width="{min(24, W - M - x)}" height="6"/>')
            grad.append(f'<rect class="grad" x="{x}" y="{H - M}" width="{min(24, W - M - x)}" height="6"/>')
    for i, y in enumerate(range(M, H - M, 24)):
        if i % 2 == 0:
            grad.append(f'<rect class="grad" x="{M - 6}" y="{y}" width="6" height="{min(24, H - M - y)}"/>')
            grad.append(f'<rect class="grad" x="{W - M}" y="{y}" width="6" height="{min(24, H - M - y)}"/>')
    sounds = [(90, 420, "57"), (236, 446, "72"), (330, 470, "64"), (420, 110, "38"), (500, 470, "41"), (60, 280, "68"),
              (380, 290, "33"), (300, 60, "44"), (470, 240, "29"), (560, 400, "36")]
    sounds_svg = "".join(f'<text class="sound" x="{x}" y="{y}">{s}</text>' for x, y, s in sounds)
    sea = "Adriatic Sea" if lang == "en" else "Jadransko more"
    label = "Route plotted around Kornati National Park, starting and ending on Murter" if lang == "en" else \
            "Ruta ucrtana oko Nacionalnog parka Kornati, s polaskom i povratkom na Murter"
    return f"""<svg viewBox="0 0 {W} {H}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">
<defs><mask id="plot"><path class="mask-path" d="{route}"/></mask><clipPath id="frame"><rect x="{M}" y="{M}" width="{W - 2*M}" height="{H - 2*M}"/></clipPath></defs>
<rect x="{M}" y="{M}" width="{W - 2*M}" height="{H - 2*M}" fill="#FAFBF8"/>
<g clip-path="url(#frame)">{shoal}{contour}{land}</g>{sounds_svg}
<text class="area-name" x="44" y="92">Kornati</text>
<text class="sea-name" x="56" y="{H - 46}">{sea}</text>
<text class="place" x="556" y="272">Murter</text>
<path class="route" d="{route}" mask="url(#plot)"/>
{stops_svg}
<rect x="{M}" y="{M}" width="{W - 2*M}" height="{H - 2*M}" fill="none" stroke="#0F2D40" stroke-width="1"/>
<rect x="{M - 6}" y="{M - 6}" width="{W - 2*M + 12}" height="{H - 2*M + 12}" fill="none" stroke="#0F2D40" stroke-width="1"/>
{''.join(grad)}
<text class="coord" x="166" y="{M - 9}">15°20′ E</text><text class="coord" x="406" y="{M - 9}">15°30′ E</text>
<text class="coord" x="12" y="150" text-anchor="middle" transform="rotate(-90 12 150)">43°50′ N</text>
<text class="coord" x="12" y="390" text-anchor="middle" transform="rotate(-90 12 390)">43°45′ N</text>
</svg>"""

# ---------------------------------------------------------------- pages
def page_home(lang):
    t = T[lang]; path = PAGES["home"][lang]; alt = PAGES["home"]
    if lang == "en":
        title = "Ivor Benko — Skipper on sailboats and catamarans in Croatia"
        desc = "Ivor Benko is a skipper from Zagreb who has captained sailboats and catamarans in the Croatian Adriatic since 2020. Private skipper for charters, sailing blog, skiing and web."
        role = "Skipper on sailboats and catamarans in the Croatian Adriatic"
        lede = "I plan the route around the weather, handle the marinas and anchorages, and make sure everyone on board has a good week at sea."
        cta1, cta2 = "Ask about availability", "Read the sailing blog"
        cap = "A week around the Kornati, as I'd plot it from Murter."
        facts = [("Skipper since", "2020, private guests and charters"), ("Boats", "Sailboats and catamarans, 42–46&nbsp;ft"),
                 ("Languages", "Croatian, English, German"), ("Sailing area", "The whole Croatian Adriatic")]
        on_board_h = "What I do on board"
        on_board = ("<p>As your skipper I'm responsible for the boat and for everyone on it. I read the forecast every morning and evening and choose the route and tonight's anchorage for tomorrow's wind. I handle the check-in with the charter base, every marina and every mooring, and I'm happy to teach anyone who wants to steer, trim or learn the knots.</p>"
                    "<p>I learned to sail at the Faculty of Kinesiology in Zagreb, worked as a sailing instructor on Murter and have been skippering since 2020.</p>")
        more = "How I work as a skipper"
        fleet_h = ("Sailboats I skipper", "Catamarans I skipper")
        blog_h = "Sailing blog"
        off_h = "Off the water"
        off = ("<div><h3>Skiing</h3><p>I've skied my whole life and hold an ISIA ski instructor licence. Skiing posts are coming to the blog.</p></div>"
               "<div><h3>Websites and apps</h3><p>I also build websites and apps, including this one. Write to me if you need one.</p></div>")
    else:
        title = "Ivor Benko — skiper na jedrilicama i katamaranima u Hrvatskoj"
        desc = "Ivor Benko je skiper iz Zagreba koji od 2020. vodi jedrilice i katamarane po hrvatskom Jadranu. Privatni skiper za chartere, blog o jedrenju, skijanje i web."
        role = "Skiper na jedrilicama i katamaranima na hrvatskom Jadranu"
        lede = "Planiram rutu prema vremenu, vodim marine i sidrenje i brinem se da svi na brodu imaju dobar tjedan na moru."
        cta1, cta2 = "Provjeri dostupnost", "Čitaj blog o jedrenju"
        cap = "Tjedan oko Kornata, kako bih ga ucrtao s Murtera."
        facts = [("Skiper od", "2020., privatni gosti i charteri"), ("Brodovi", "Jedrilice i katamarani, 42–46&nbsp;stopa"),
                 ("Jezici", "hrvatski, engleski, njemački"), ("Područje", "Cijeli hrvatski Jadran")]
        on_board_h = "Što radim na brodu"
        on_board = ("<p>Kao vaš skiper odgovoran sam za brod i za sve na njemu. Prognozu čitam svako jutro i večer, a rutu i večerašnje sidrište biram prema sutrašnjem vjetru. Vodim preuzimanje broda u charter bazi, svaku marinu i svaki vez, a rado podučim svakoga tko želi kormilariti, trimati jedra ili naučiti čvorove.</p>"
                    "<p>Jedriti sam naučio na Kineziološkom fakultetu u Zagrebu, radio sam kao instruktor jedrenja na Murteru i skiper sam od 2020.</p>")
        more = "Kako radim kao skiper"
        fleet_h = ("Jedrilice koje vodim", "Katamarani koje vodim")
        blog_h = "Blog o jedrenju"
        off_h = "Izvan mora"
        off = ("<div><h3>Skijanje</h3><p>Skijam cijeli život i imam licencu ISIA instruktora skijanja. Tekstovi o skijanju stižu na blog.</p></div>"
               "<div><h3>Web stranice i aplikacije</h3><p>Izrađujem i web stranice i aplikacije, uključujući ovu. Javite mi se ako vam treba.</p></div>")
    anchor = "contact" if lang == "en" else "kontakt"
    ld = [person(lang), website(), webpage(lang, path, title, desc, extra={"mainEntity": {"@id": SITE + "/#person"},
          "primaryImageOfPage": SITE + "/assets/ivor-benko.jpg"})]
    facts_html = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts)
    fleet = (f'<div class="fleet"><div><h3>{fleet_h[0]}</h3><ul>{"".join(f"<li>{b}</li>" for b in SAILBOATS)}</ul></div>'
             f'<div><h3>{fleet_h[1]}</h3><ul>{"".join(f"<li>{b}</li>" for b in CATAMARANS)}</ul></div></div>')
    body = f"""<div class="wrap">
<section class="hero">
<div><h1>{NAME}</h1><p class="role">{role}</p><p class="lede">{lede}</p>
<div class="actions"><a class="btn" href="{PAGES['skipper'][lang]}#{anchor}">{cta1}</a><a class="textlink" href="{PAGES['blog'][lang]}">{cta2}</a></div></div>
<figure class="chart" style="margin:0">{chart_svg(lang)}<figcaption>{cap}</figcaption></figure>
</section>
<dl class="facts">{facts_html}</dl>
<section class="section split" aria-labelledby="onboard">
<div><h2 id="onboard">{on_board_h}</h2></div>
<div class="prose">{on_board}<p><a class="textlink" href="{PAGES['skipper'][lang]}">{more}</a></p>{fleet}</div>
</section>
<section class="section" aria-labelledby="blog-h"><div class="section-head"><h2 id="blog-h">{blog_h}</h2><a class="textlink" href="{PAGES['blog'][lang]}">{t['all_posts']}</a></div>
{post_list(lang, POSTS[lang][:4])}</section>
<section class="section split" aria-labelledby="off-h"><div><h2 id="off-h">{off_h}</h2></div><div class="fleet" style="margin:0">{off}</div></section>
{contact_block(lang, anchor)}
</div>"""
    return path, head(lang, path, alt, title, desc, ld) + header(lang, "home", alt) + body + footer(lang)

def page_skipper(lang):
    t = T[lang]; path = PAGES["skipper"][lang]; alt = PAGES["skipper"]
    anchor = "contact" if lang == "en" else "kontakt"
    if lang == "en":
        title = "Private skipper in Croatia for sailboat and catamaran charters — Ivor Benko"
        desc = "Hire Ivor Benko as a private skipper for your yacht or catamaran charter in Croatia. Skipper since 2020, speaks Croatian, English and German, knows the Adriatic weather."
        h1 = "Private skipper for sailboat and catamaran charters in Croatia"
        lede = "Book the boat with any charter company, and I'll skipper it. Or ask me first and I'll help you choose."
        does_h = "What you get with me as your skipper"
        does = ["<strong>A route built around the weather.</strong> Bura, jugo and maestral decide where it's safe and pleasant to be. I check the forecast every morning and evening.",
                "<strong>Marinas, buoys and anchoring handled.</strong> Mooring stern-to in a busy July marina is my job, not yours.",
                "<strong>Check-in and check-out with the charter base.</strong> Inventory, engine, sails and damage report, so there are no surprises at the end.",
                "<strong>Local knowledge.</strong> Which bay is sheltered from tonight's wind, where you can tie up for dinner, where the water is clearest in the morning.",
                "<strong>Sailing lessons if you want them.</strong> I've worked as a sailing instructor. Steering, sail trim, knots and mooring, at whatever pace suits you.",
                "<strong>Three languages.</strong> Croatian, English (C1) and German (B1)."]
        area_h = "Where I sail"
        area = "<p>The whole Croatian Adriatic, from Istria and Kvarner to central and southern Dalmatia. I know the Kornati and the Šibenik archipelago especially well, because I worked as a sailing instructor on Murter.</p>"
        steps_h = "How it works"
        steps = [("Tell me your plans", "Dates, number of guests, the boat or charter base if you have one, and what kind of week you want."),
                 ("I confirm availability", "We agree on my fee, meals on board and where I'll sleep, and I suggest a rough route."),
                 ("Check-in day", "I meet you at the base, take over the boat with the charter company and give everyone a short safety briefing."),
                 ("The week at sea", "We sail, swim and eat well. The route adapts to the forecast every day."),
                 ("Check-out", "I return the boat to the base and handle the handover with the charter company.")]
        qual_h = "Experience and qualifications"
        qual = [("Skipper", "Since 2020, on private and charter trips"), ("Sailboats", ", ".join(SAILBOATS)), ("Catamarans", ", ".join(CATAMARANS)),
                ("Training", "Sail Week skipper academy, completed with an A grade (2024)"), ("Licence", "Croatian boat licence, category C"),
                ("Background", "Faculty of Kinesiology, University of Zagreb, specialised in sailing and water sports; sailing instructor on Murter; Laser Radial, Optimist and Laser Stratos; regattas")]
        faq_h = "Questions guests ask"
        faq = [("Do I need a skipper to charter a boat in Croatia?", "If nobody in your group has a boat licence recognised in Croatia and a VHF radio certificate, yes. Even with licences, many groups hire a skipper so that everyone can relax. I wrote more about it in the blog post on whether you need a skipper."),
               ("Which boats do you skipper?", f"Monohull sailboats like the {', '.join(SAILBOATS)} and catamarans like the {', '.join(CATAMARANS)}. Similar boats of that size are fine too."),
               ("Can you teach us to sail during the week?", "Yes. I've worked as a sailing instructor, and I'm happy to teach steering, sail trim, knots and mooring to anyone who wants to learn."),
               ("Which languages do you speak?", "Croatian (native), English (C1) and German (B1)."),
               ("Where does the skipper sleep?", "Usually in a separate cabin or in the skipper's cabin that many catamarans have in the bow. We agree on this before you choose the boat."),
               ("What does a skipper cost?", "The skipper's fee is paid separately from the boat, and guests usually cover the skipper's meals. Send me your dates and I'll give you an exact figure."),
               ("Do you cook and clean?", "A skipper is responsible for the boat and your safety, not for cooking or cleaning guest cabins. If you'd like that, ask the charter company about a hostess.")]
    else:
        title = "Privatni skiper u Hrvatskoj za najam jedrilica i katamarana — Ivor Benko"
        desc = "Unajmite Ivora Benka kao privatnog skipera za charter jedrilice ili katamarana u Hrvatskoj. Skiper od 2020., govori hrvatski, engleski i njemački i poznaje jadransko vrijeme."
        h1 = "Privatni skiper za charter jedrilica i katamarana u Hrvatskoj"
        lede = "Rezervirajte brod kod bilo koje charter tvrtke, a ja ću biti skiper. Ili mi se javite prije i pomoći ću vam odabrati."
        does_h = "Što dobivate sa mnom kao skiperom"
        does = ["<strong>Rutu složenu prema vremenu.</strong> Bura, jugo i maestral određuju gdje je sigurno i ugodno biti. Prognozu provjeravam svako jutro i večer.",
                "<strong>Marine, bove i sidrenje.</strong> Vezivanje krmom u punoj marini u srpnju moj je posao, ne vaš.",
                "<strong>Preuzimanje i predaju broda.</strong> Inventar, motor, jedra i zapisnik o oštećenjima, bez iznenađenja na kraju.",
                "<strong>Lokalno znanje.</strong> Koja je uvala zaštićena od večerašnjeg vjetra, gdje se možete vezati za večeru, gdje je more ujutro najbistrije.",
                "<strong>Škola jedrenja ako želite.</strong> Radio sam kao instruktor jedrenja. Kormilarenje, trim jedara, čvorovi i vez, tempom koji vam odgovara.",
                "<strong>Tri jezika.</strong> Hrvatski, engleski (C1) i njemački (B1)."]
        area_h = "Gdje jedrim"
        area = "<p>Cijeli hrvatski Jadran, od Istre i Kvarnera do srednje i južne Dalmacije. Posebno dobro poznajem Kornate i šibenski arhipelag, jer sam radio kao instruktor jedrenja na Murteru.</p>"
        steps_h = "Kako to funkcionira"
        steps = [("Javite mi planove", "Termin, broj gostiju, brod ili charter bazu ako ih imate i kakav tjedan želite."),
                 ("Potvrđujem dostupnost", "Dogovaramo cijenu, obroke na brodu i gdje spavam, a ja predlažem okvirnu rutu."),
                 ("Dan preuzimanja", "Nalazimo se u bazi, preuzimam brod od charter tvrtke i svima dajem kratke sigurnosne upute."),
                 ("Tjedan na moru", "Jedrimo, kupamo se i dobro jedemo. Ruta se svaki dan prilagođava prognozi."),
                 ("Predaja broda", "Vraćam brod u bazu i obavljam primopredaju s charter tvrtkom.")]
        qual_h = "Iskustvo i kvalifikacije"
        qual = [("Skiper", "Od 2020., na privatnim i charter plovidbama"), ("Jedrilice", ", ".join(SAILBOATS)), ("Katamarani", ", ".join(CATAMARANS)),
                ("Edukacija", "Sail Week skiperska akademija, završena s ocjenom A (2024.)"), ("Ispit", "Voditelj brodice kategorije C"),
                ("Iskustvo", "Kineziološki fakultet Sveučilišta u Zagrebu, usmjerenje jedrenje i sportovi na vodi; instruktor jedrenja na Murteru; Laser Radial, Optimist i Laser Stratos; regate")]
        faq_h = "Pitanja koja gosti postavljaju"
        faq = [("Treba li mi skiper za najam broda u Hrvatskoj?", "Ako nitko u vašoj grupi nema ispit za voditelja brodice priznat u Hrvatskoj i VHF svjedodžbu, da. I s ispitom mnoge grupe unajme skipera da se svi mogu opustiti. Više o tome pisao sam na blogu."),
               ("Koje brodove vodite?", f"Jednotrupne jedrilice poput {', '.join(SAILBOATS)} i katamarane poput {', '.join(CATAMARANS)}. U redu su i slični brodovi te veličine."),
               ("Možete li nas naučiti jedriti tijekom tjedna?", "Da. Radio sam kao instruktor jedrenja i rado podučim kormilarenje, trim jedara, čvorove i vez svakoga tko želi učiti."),
               ("Koje jezike govorite?", "Hrvatski (materinski), engleski (C1) i njemački (B1)."),
               ("Gdje spava skiper?", "Obično u zasebnoj kabini ili u skiperskoj kabini koju mnogi katamarani imaju u pramcu. To dogovaramo prije odabira broda."),
               ("Koliko košta skiper?", "Skiper se plaća odvojeno od najma broda, a gosti obično pokrivaju skiperove obroke. Pošaljite mi termin i dat ću vam točan iznos."),
               ("Kuhate li i čistite?", "Skiper je odgovoran za brod i vašu sigurnost, a ne za kuhanje ili čišćenje kabina gostiju. Ako to želite, pitajte charter tvrtku za hostesu.")]
    service = {"@type": "Service", "@id": abs_url(path) + "#service", "name": h1, "description": desc,
               "serviceType": "Private yacht skipper" if lang == "en" else "Privatni skiper",
               "provider": {"@id": SITE + "/#person"}, "areaServed": [{"@type": "Country", "name": "Croatia"}, {"@type": "Place", "name": "Adriatic Sea"}],
               "availableLanguage": ["hr", "en", "de"], "url": abs_url(path)}
    faq_ld = {"@type": "FAQPage", "@id": abs_url(path) + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ld = [person(lang), website(), webpage(lang, path, title, desc, extra={"mainEntity": {"@id": abs_url(path) + "#service"}}),
          service, faq_ld, crumbs_ld([(t["home"], PAGES["home"][lang]), (t["skipper"], path)])]
    blog_link = next(p["path"] for p in POSTS[lang] if p["key"] == "skipper-needed")
    faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)
    faq_html = faq_html.replace(esc("blog post on whether you need a skipper."), f'<a href="{blog_link}">blog post on whether you need a skipper</a>.') \
                       .replace("pisao sam na blogu.", f'<a href="{blog_link}">pisao sam na blogu</a>.')
    body = f"""<div class="wrap">
<section class="hero" style="grid-template-columns:1fr"><div><h1 style="max-width:52rem">{h1}</h1><p class="lede">{lede}</p>
<div class="actions"><a class="btn" href="#{anchor}">{'Ask about availability' if lang == 'en' else 'Provjeri dostupnost'}</a></div></div></section>
<section class="section split"><div><h2>{does_h}</h2></div><div class="prose"><ul>{''.join(f'<li>{d}</li>' for d in does)}</ul></div></section>
<section class="section split"><div><h2>{area_h}</h2></div><div class="prose">{area}</div></section>
<section class="section split"><div><h2>{steps_h}</h2></div><ol class="steps">{''.join(f'<li><span><strong>{a}</strong>{b}</span></li>' for a, b in steps)}</ol></section>
<section class="section split"><div><h2>{qual_h}</h2></div><dl class="kv">{''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in qual)}</dl></section>
<section class="section split"><div><h2>{faq_h}</h2></div><div class="faq">{faq_html}</div></section>
{contact_block(lang, anchor)}
</div>"""
    return path, head(lang, path, alt, title, desc, ld) + header(lang, "skipper", alt) + body + footer(lang)

def page_about(lang):
    t = T[lang]; path = PAGES["about"][lang]; alt = PAGES["about"]
    anchor = "contact" if lang == "en" else "kontakt"
    if lang == "en":
        title = "About Ivor Benko — skipper, ski instructor and web developer from Zagreb"
        desc = "Who is Ivor Benko? A Croatian skipper from Zagreb, sailing sailboats and catamarans in the Adriatic since 2020, ISIA ski instructor and web developer. Experience, education and qualifications."
        h1 = "About Ivor Benko"
        facts = [("Name", NAME), ("Based in", "Zagreb, Croatia"), ("Work", "Skipper on sailboats and catamarans (since 2020), ski instructor, web and app developer"),
                 ("Sailing area", "Croatian Adriatic, especially the Kornati and central Dalmatia"),
                 ("Boats", ", ".join(SAILBOATS + CATAMARANS)),
                 ("Qualifications", "Croatian boat licence (category C); Sail Week skipper academy, A grade (2024); ISIA ski instructor licence; driving licence (category B)"),
                 ("Education", "Faculty of Kinesiology, University of Zagreb (from 2017), specialised in sailing and water sports; secondary school of nutrition in Zagreb (2011–2015)"),
                 ("Languages", "Croatian (native), English (C1), German (B1)"),
                 ("Contact", f'<a href="mailto:{EMAIL}">{EMAIL}</a>, <a href="tel:{PHONE_E164}">{PHONE}</a>')]
        bio = ("<p>I'm a skipper from Zagreb. I've skied my whole life and became a licensed ski instructor. While studying at the Faculty of Kinesiology, where I specialised in sailing and water sports, I discovered sailing and fell in love with it straight away.</p>"
               "<p>Since then I've sailed small boat classes like the Laser Radial, Optimist and Laser Stratos, windsurfed, raced in regattas, worked as a sailing instructor for the faculty on Murter and sailed big boats all over the Adriatic. In 2020 I turned the hobby into my profession, and I've worked as a captain and skipper for private guests and charters ever since.</p>"
               "<p>I know the Adriatic weather well, and I've been organising sports activities for more than ten years, from skiing and windsurfing to fitness, acrobatics and breakdance. People tell me I'm communicative, cheerful and organised, which is most of what you want from someone you share a boat with for a week.</p>"
               "<p>Outside of sailing I build websites and apps and write, and in winter I'm back on the slopes.</p>")
        exp_h = "Experience"
        exp = [("2020–today", "Captain and skipper, private guests and charters", f"Sailboats: {', '.join(SAILBOATS)}. Catamarans: {', '.join(CATAMARANS)}."),
               ("2020–today", "Sailing", "Sailing instructor for the Faculty of Kinesiology on Murter. Laser Radial, Optimist and Laser Stratos. Big boats (45 ft and up) all over the Adriatic. Regattas."),
               ("2024", "Sail Week skipper academy", "Skipper course completed with an A grade."),
               ("10+ years", "Organising sports activities", "Windsurfing, skiing, fitness, acrobatics, breakdance and dinghy sailing.")]
        skills_h = "Other skills"
        skills = "Skiing and ski instruction (ISIA licence), web and app development, digital marketing, copywriting and storytelling, breakdance."
    else:
        title = "O meni — Ivor Benko, skiper, instruktor skijanja i web developer iz Zagreba"
        desc = "Tko je Ivor Benko? Hrvatski skiper iz Zagreba koji od 2020. vodi jedrilice i katamarane po Jadranu, ISIA instruktor skijanja i web developer. Iskustvo, obrazovanje i kvalifikacije."
        h1 = "O meni"
        facts = [("Ime", NAME), ("Baza", "Zagreb, Hrvatska"), ("Posao", "Skiper na jedrilicama i katamaranima (od 2020.), instruktor skijanja, izrada webova i aplikacija"),
                 ("Područje", "Hrvatski Jadran, posebno Kornati i srednja Dalmacija"),
                 ("Brodovi", ", ".join(SAILBOATS + CATAMARANS)),
                 ("Kvalifikacije", "Voditelj brodice kategorije C; Sail Week skiperska akademija, ocjena A (2024.); licenca ISIA instruktora skijanja; vozačka dozvola B kategorije"),
                 ("Obrazovanje", "Kineziološki fakultet Sveučilišta u Zagrebu (od 2017.), usmjerenje jedrenje i sportovi na vodi; srednja škola za nutricioniste u Zagrebu (2011.–2015.)"),
                 ("Jezici", "hrvatski (materinski), engleski (C1), njemački (B1)"),
                 ("Kontakt", f'<a href="mailto:{EMAIL}">{EMAIL}</a>, <a href="tel:{PHONE_E164}">{PHONE}</a>')]
        bio = ("<p>Ja sam skiper iz Zagreba. Skijam cijeli život i postao sam licencirani instruktor skijanja. Tijekom studija na Kineziološkom fakultetu, gdje sam se usmjerio na jedrenje i sportove na vodi, otkrio sam jedrenje i odmah se zaljubio u njega.</p>"
               "<p>Od tada sam jedrio u malim klasama poput Laser Radiala, Optimista i Laser Stratosa, windsurfao, sudjelovao na regatama, radio kao instruktor jedrenja za fakultet na Murteru i jedrio velikim brodovima po cijelom Jadranu. Godine 2020. hobi sam pretvorio u posao i od tada radim kao kapetan i skiper za privatne goste i chartere.</p>"
               "<p>Dobro poznajem jadransko vrijeme, a više od deset godina organiziram sportske aktivnosti, od skijanja i windsurfinga do fitnessa, akrobatike i breakdancea. Ljudi kažu da sam komunikativan, vedar i organiziran, a to je većina onoga što želite od osobe s kojom tjedan dana dijelite brod.</p>"
               "<p>Osim jedrenja izrađujem web stranice i aplikacije i pišem, a zimi sam opet na skijalištu.</p>")
        exp_h = "Iskustvo"
        exp = [("2020.–danas", "Kapetan i skiper, privatni gosti i charteri", f"Jedrilice: {', '.join(SAILBOATS)}. Katamarani: {', '.join(CATAMARANS)}."),
               ("2020.–danas", "Jedrenje", "Instruktor jedrenja za Kineziološki fakultet na Murteru. Laser Radial, Optimist i Laser Stratos. Veliki brodovi (od 45 stopa) po cijelom Jadranu. Regate."),
               ("2024.", "Sail Week skiperska akademija", "Skiperski tečaj završen s ocjenom A."),
               ("10+ godina", "Organizacija sportskih aktivnosti", "Windsurfing, skijanje, fitness, akrobatika, breakdance i jedrenje na malim brodicama.")]
        skills_h = "Ostale vještine"
        skills = "Skijanje i podučavanje skijanja (ISIA licenca), izrada web stranica i aplikacija, digitalni marketing, copywriting i pisanje priča, breakdance."
    profile = webpage(lang, path, title, desc, typ="ProfilePage",
                      extra={"mainEntity": {"@id": SITE + "/#person"}, "dateCreated": "2026-09-28"})
    ld = [person(lang), website(), profile, crumbs_ld([(t["home"], PAGES["home"][lang]), (t["about"], path)])]
    exp_html = "".join(f'<li><div class="row"><span class="when">{a}</span><span><span class="t">{b}</span><span class="s">{c}</span></span></div></li>' for a, b, c in exp)
    body = f"""<div class="wrap">
<section class="hero"><div><h1>{h1}</h1><p class="lede">{t['author_bio']}</p></div>
<img class="portrait" style="width:14rem;height:14rem" src="/assets/ivor-benko.jpg" width="240" height="240" alt="{NAME}"></section>
<section class="section split"><div><h2>{'Quick facts' if lang == 'en' else 'Ukratko'}</h2></div><dl class="kv">{''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in facts)}</dl></section>
<section class="section split"><div><h2>{'My story' if lang == 'en' else 'Moja priča'}</h2></div><div class="prose">{bio}</div></section>
<section class="section split"><div><h2>{exp_h}</h2></div><ul class="posts">{exp_html}</ul></section>
<section class="section split"><div><h2>{skills_h}</h2></div><div class="prose"><p>{skills}</p></div></section>
{contact_block(lang, anchor)}
</div>"""
    return path, head(lang, path, alt, title, desc, ld, og_type="profile",
                      extra_meta='<meta property="profile:first_name" content="Ivor"><meta property="profile:last_name" content="Benko">') \
        + header(lang, "about", alt) + body + footer(lang)

def page_blog(lang):
    t = T[lang]; path = PAGES["blog"][lang]; alt = PAGES["blog"]
    if lang == "en":
        title = "Sailing blog — Ivor Benko, skipper in Croatia"
        desc = "Practical sailing guides for Croatia from skipper Ivor Benko: Adriatic winds, the Kornati, choosing a catamaran or sailboat, packing lists and more. Skiing posts coming soon."
        intro = "Practical notes from a skipper on sailing in Croatia: weather, routes, boats and what to expect on a charter week."
    else:
        title = "Blog o jedrenju — Ivor Benko, skiper u Hrvatskoj"
        desc = "Praktični vodiči za jedrenje u Hrvatskoj od skipera Ivora Benka: jadranski vjetrovi, Kornati, katamaran ili jedrilica, popis stvari i više. Uskoro i tekstovi o skijanju."
        intro = "Praktične bilješke skipera o jedrenju u Hrvatskoj: vrijeme, rute, brodovi i što očekivati na tjednu chartera."
    sections = ""
    for cat, names in CATEGORIES.items():
        ps = [p for p in POSTS[lang] if p["category"] == cat]
        inner = post_list(lang, ps) if ps else f'<p class="empty">{t["coming"]}</p>'
        sections += f'<section class="section" id="{cat}" aria-labelledby="{cat}-h"><div class="section-head"><h2 id="{cat}-h">{names[lang]}</h2></div>{inner}</section>'
    blog_ld = {"@type": "Blog", "@id": abs_url(path) + "#blog", "url": abs_url(path), "name": title, "inLanguage": lang,
               "author": {"@id": SITE + "/#person"}, "publisher": {"@id": SITE + "/#person"},
               "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": abs_url(p["path"]), "datePublished": p["date"]} for p in POSTS[lang]]}
    ld = [person(lang), website(), webpage(lang, path, title, desc, typ="CollectionPage", extra={"mainEntity": {"@id": abs_url(path) + "#blog"}}),
          blog_ld, crumbs_ld([(t["home"], PAGES["home"][lang]), (t["blog"], path)])]
    body = f"""<div class="wrap"><section class="hero" style="grid-template-columns:1fr"><div><h1>{t['blog']}</h1><p class="lede">{intro}</p></div></section>{sections}</div>"""
    return path, head(lang, path, alt, title, desc, ld) + header(lang, "blog", alt) + body + footer(lang)

def page_post(p):
    lang = p["lang"]; t = T[lang]; path = p["path"]
    tw = twin(p)
    alt = {lang: path}
    if tw: alt[tw["lang"]] = tw["path"]
    minutes = max(2, round(p["words"] / 200))
    title = f'{p["title"]} — {NAME}'
    ld = [person(lang), website(),
          {"@type": "BlogPosting", "@id": abs_url(path) + "#article", "mainEntityOfPage": abs_url(path),
           "headline": p["title"], "description": p["description"], "abstract": p["summary"],
           "datePublished": p["date"], "dateModified": p["updated"], "inLanguage": lang,
           "author": {"@id": SITE + "/#person"}, "publisher": {"@id": SITE + "/#person"},
           "image": SITE + "/assets/og-image.jpg", "wordCount": p["words"],
           "articleSection": CATEGORIES[p["category"]][lang],
           "isPartOf": {"@id": abs_url(PAGES["blog"][lang]) + "#blog"},
           **({"translationOfWork": {"@id": abs_url(tw["path"]) + "#article"}} if tw and tw["lang"] == "en" and lang != "en" else {})},
          crumbs_ld([(t["home"], PAGES["home"][lang]), (t["blog"], PAGES["blog"][lang]), (p["title"], path)])]
    more = [q for q in POSTS[lang] if q["key"] != p["key"]][:3]
    trans = f'<p class="translation"><a href="{tw["path"]}" hreflang="{tw["lang"]}" lang="{tw["lang"]}">{T[lang]["translation"]}</a></p>' if tw else ""
    body = f"""<div class="wrap"><article class="article">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{PAGES['home'][lang]}">{t['home']}</a></li><li><a href="{PAGES['blog'][lang]}">{t['blog']}</a></li><li aria-current="page">{esc(CATEGORIES[p['category']][lang])}</li></ol></nav>
<h1>{esc(p['title'])}</h1>
<div class="meta"><span><time datetime="{p['date']}">{fmt_date(p['date'], lang)}</time></span><span>{minutes} {t['read']}</span><span>{t['by']} <a href="{PAGES['about'][lang]}" rel="author">{NAME}</a></span></div>
<aside class="answer" aria-labelledby="short"><h2 id="short">{t['short']}</h2><p>{esc(p['summary'])}</p></aside>
<div class="prose">{p['html']}</div>
<div class="author"><img src="/assets/ivor-benko.jpg" width="240" height="240" alt="{NAME}" loading="lazy"><p><a href="{PAGES['about'][lang]}"><strong>{NAME}</strong></a><br>{t['author_bio']}</p></div>
{trans}
</article>
<section class="section" aria-labelledby="more-h"><div class="section-head"><h2 id="more-h">{t['more_posts']}</h2><a class="textlink" href="{PAGES['blog'][lang]}">{t['all_posts']}</a></div>{post_list(lang, more)}</section>
</div>"""
    extra = (f'<meta property="article:published_time" content="{p["date"]}"><meta property="article:modified_time" content="{p["updated"]}">'
             f'<meta property="article:author" content="{abs_url(PAGES["about"][lang])}"><meta property="article:section" content="{CATEGORIES[p["category"]][lang]}">')
    return path, head(lang, path, alt, title, p["description"], ld, og_type="article", extra_meta=extra) + header(lang, "blog", alt) + body + footer(lang)

def page_404():
    ld = [website()]
    body = """<div class="wrap"><section class="hero" style="grid-template-columns:1fr"><div>
<h1>Page not found</h1><p class="lede">This page doesn't exist or has moved. Go to the <a href="/">home page</a> or the <a href="/blog/">blog</a>.</p>
<p class="lede" lang="hr">Ova stranica ne postoji ili je premještena. Idite na <a href="/hr/">početnu</a> ili na <a href="/hr/blog/">blog</a>.</p>
</div></section></div>"""
    h = head("en", "/404.html", {}, "Page not found — Ivor Benko", "Page not found.", ld).replace(
        'content="index, follow, max-image-preview:large, max-snippet:-1"', 'content="noindex"')
    return "/404.html", h + header("en", None, {"hr": "/hr/"}) + body + footer("en")

# ---------------------------------------------------------------- feeds, sitemap, robots, llms
def rss(lang):
    t = T[lang]
    items = "".join(f"""<item><title>{esc(p['title'])}</title><link>{abs_url(p['path'])}</link><guid>{abs_url(p['path'])}</guid>
<pubDate>{dt.datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y 08:00:00 +0000')}</pubDate><description>{esc(p['summary'])}</description></item>""" for p in POSTS[lang])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{NAME} — {t['blog']}</title><link>{abs_url(PAGES['blog'][lang])}</link>
<description>{esc(T[lang]['foot_role'])}</description><language>{lang}</language>{items}</channel></rss>"""

def sitemap(entries):
    urls = ""
    for alt, lastmod in entries:
        for lang, path in alt.items():
            links = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{abs_url(u)}"/>' for l, u in alt.items())
            if len(alt) > 1 and "en" in alt: links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(alt["en"])}"/>'
            urls += f"<url><loc>{abs_url(path)}</loc><lastmod>{lastmod}</lastmod>{links}</url>\n"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
{urls}</urlset>"""

ROBOTS = f"""# Search engines and AI assistants are welcome to read and cite this site.
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: CCBot
Allow: /

Sitemap: {SITE}/sitemap.xml
"""

def llms_txt():
    en = POSTS["en"]; hr = POSTS["hr"]
    lines = [f"# {NAME}", "",
             "> Ivor Benko is a Croatian skipper from Zagreb who has captained sailboats and catamarans on private and charter trips in the Croatian Adriatic since 2020. He is also a licensed ISIA ski instructor and a web and app developer. This site (English and Croatian) is the authoritative source for information about him.", "",
             "Key facts:",
             "- Occupation: skipper / captain on sailboats and catamarans for private guests and charters in Croatia (since 2020); ski instructor; web and app developer",
             f"- Boats: {', '.join(SAILBOATS)} (monohulls); {', '.join(CATAMARANS)} (catamarans)",
             "- Sailing area: the whole Croatian Adriatic; especially Kornati National Park, Murter and central Dalmatia",
             "- Qualifications: Croatian boat licence, category C; Sail Week skipper academy course completed with an A grade (2024); ISIA ski instructor licence; driving licence category B",
             "- Sailing background: sailing instructor for the Faculty of Kinesiology (University of Zagreb) on Murter; Laser Radial, Optimist and Laser Stratos; regattas; windsurfing; big boats (45 ft+) across the Adriatic",
             "- Education: Faculty of Kinesiology, University of Zagreb (from 2017), specialised in sailing and water sports; secondary school of nutrition in Zagreb (2011–2015)",
             "- Languages: Croatian (native), English (C1), German (B1)",
             "- Based in: Zagreb, Croatia",
             f"- Contact: {EMAIL}, {PHONE}", ""]
    if SAME_AS: lines += ["- Profiles: " + ", ".join(SAME_AS), ""]
    lines += ["## Pages", "",
              f"- [About Ivor Benko]({SITE}/about/): biography, experience, qualifications",
              f"- [Private skipper in Croatia]({SITE}/skipper/): skipper services, boats, sailing area, FAQ",
              f"- [Blog]({SITE}/blog/): sailing guides for Croatia", "", "## Blog posts (English)", ""]
    lines += [f"- [{p['title']}]({abs_url(p['path'])}): {p['summary']}" for p in en]
    lines += ["", "## Croatian version (Hrvatski)", "",
              f"- [O meni]({SITE}/hr/o-meni/)", f"- [Privatni skiper]({SITE}/hr/skiper/)", f"- [Blog]({SITE}/hr/blog/)"]
    lines += [f"- [{p['title']}]({abs_url(p['path'])})" for p in hr]
    lines += ["", "## Optional", "", f"- [Full text of all posts]({SITE}/llms-full.txt)", ""]
    return "\n".join(lines)

def llms_full():
    out = [llms_txt(), "\n---\n"]
    for lang in LANGS:
        for p in POSTS[lang]:
            out.append(f"# {p['title']}\n\nURL: {abs_url(p['path'])}\nAuthor: {NAME}\nPublished: {p['date']}\nLanguage: {lang}\n\n"
                       f"Short answer: {p['summary']}\n\n{p['body_md']}\n\n---\n")
    return "\n".join(out)

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0F2D40"/><path d="M30 10 L30 46 L12 46 Z" fill="#FAFBF8"/><path d="M34 16 L34 46 L50 46 Z" fill="#E09A12"/><path d="M10 50 H54 L48 56 H16 Z" fill="#FAFBF8"/></svg>"""

# ---------------------------------------------------------------- images
def make_images(assets):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed, skipping og-image"); return
    fonts = ROOT / "static" / "fonts-src"
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#0F2D40")
    d = ImageDraw.Draw(img)
    def font(fname, size, axes=None):
        f = ImageFont.truetype(str(fonts / fname), size)
        if axes:
            try: f.set_variation_by_axes(axes)
            except Exception: pass
        return f
    serif = font("Newsreader[opsz,wght].ttf", 118, [72, 400])
    ital = font("Newsreader-Italic[opsz,wght].ttf", 46, [36, 400])
    sans = font("HankenGrotesk[wght].ttf", 28, [500])
    for i in range(0, W, 40):  # graduated border
        if (i // 40) % 2 == 0:
            d.rectangle([i, 0, i + 39, 9], fill="#FAFBF8"); d.rectangle([i, H - 10, i + 39, H], fill="#FAFBF8")
    d.text((80, 150), NAME, font=serif, fill="#FAFBF8")
    d.text((84, 300), "Skipper on sailboats and catamarans", font=ital, fill="#8FD3CC")
    d.text((84, 356), "Skiper na jedrilicama i katamaranima", font=ital, fill="#8FD3CC")
    d.text((84, 500), "ivorbenko.com", font=sans, fill="#C9D8DA")
    portrait = Image.open(ROOT / "static" / "ivor-benko.jpg").convert("RGB").resize((300, 300), Image.LANCZOS)
    mask = Image.new("L", (300, 300), 0); ImageDraw.Draw(mask).ellipse([0, 0, 299, 299], fill=255)
    img.paste(portrait, (830, 165), mask)
    d.ellipse([826, 161, 1133, 468], outline="#E09A12", width=4)
    img.save(assets / "og-image.jpg", quality=88)
    Image.open(ROOT / "static" / "ivor-benko.jpg").convert("RGB").resize((180, 180), Image.LANCZOS).save(assets / "apple-touch-icon.png")

# ---------------------------------------------------------------- build
def write(path, content):
    f = OUT / (path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    assets = OUT / "assets"; (assets / "fonts").mkdir(parents=True)
    for f in (ROOT / "static" / "fonts").glob("*.woff2"): shutil.copy(f, assets / "fonts" / f.name)
    shutil.copy(ROOT / "static" / "style.css", assets / "style.css")
    shutil.copy(ROOT / "static" / "ivor-benko.jpg", assets / "ivor-benko.jpg")
    make_images(assets)
    entries = []
    for fn in (page_home, page_skipper, page_about, page_blog):
        for lang in LANGS:
            path, htm = fn(lang); write(path, htm)
        key = fn.__name__.replace("page_", "")
        entries.append((PAGES[key], TODAY))
    seen = set()
    for lang in LANGS:
        for p in POSTS[lang]:
            path, htm = page_post(p); write(path, htm)
            if p["key"] in seen: continue
            seen.add(p["key"]); alt = {p["lang"]: p["path"]}
            tw = twin(p)
            if tw: alt[tw["lang"]] = tw["path"]
            entries.append((alt, p["updated"]))
    path, htm = page_404(); write(path, htm)
    write("/blog/feed.xml", rss("en")); write("/hr/blog/feed.xml", rss("hr"))
    write("/sitemap.xml", sitemap(entries)); write("/robots.txt", ROBOTS)
    write("/llms.txt", llms_txt()); write("/llms-full.txt", llms_full())
    write("/favicon.svg", FAVICON)
    n = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {n} pages into {OUT}")

if __name__ == "__main__":
    main()
