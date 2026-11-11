#!/usr/bin/env python3
"""Render animated SVG cards for the GitHub profile README.

  python scripts/render_readme_cards.py            # animated cards -> cards/
  STATIC=1 python scripts/render_readme_cards.py   # final frame only (for screenshots)

Reads data/contributions.json:  {"days": [{"date": "2026-11-09", "count": 4}, ...]}
Also (re)writes README.md so the layout and the cards never drift apart.
Optional: fonts/serif.ttf, fonts/serif-italic.ttf, fonts/sans.ttf, fonts/mono.ttf
          (subset + embedded as base64 WOFF), assets/portrait.png|jpg|webp.
"""
import base64, datetime as dt, html, io, json, os, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"
DATA = Path(os.environ.get("DATA", ROOT / "data" / "contributions.json"))
STATIC = os.environ.get("STATIC") == "1"

# ───────────────────────── EDIT ME ─────────────────────────
USER = "Jeswanthsurya-debug"
NAME = ("Jeswanth", "Surya.")
TAGLINE = "Aspiring software engineer building practical AI, cloud and web projects."
STATUS = "OPEN TO INTERNSHIPS · 2026"
PORTFOLIO = "https://jeswanthsurya-debug.github.io/jeswanth-portfolio/"

INK, PAPER, BRAND, RED, YELLOW = "#111111", "#F4F3EF", "#2B44FF", "#E04B3A", "#F5C842"
RAMP = ["#E4E3DE", "#C9D0FF", "#97A5FF", "#5B6EFF", BRAND]  # contribution graph, light -> dark

SOCIALS = [  # (label, url, dot colour) - first one is the primary pill
    ("Portfolio", PORTFOLIO, BRAND),
    ("LinkedIn", "https://linkedin.com/in/jeswanth-surya-98517b339", "#0A66C2"),
    ("YouTube", "https://www.youtube.com/@SuryaBulids", RED),
    ("Instagram", "https://instagram.com/YOUR_HANDLE", "#C13584"),  # <- put your handle
    ("Snapchat", "https://snapchat.com/t/ouKeQW7a", YELLOW),
    ("LeetCode", "https://leetcode.com/u/Jeswanth_surya", "#F89F1B"),
    ("Email", "mailto:jeswanthsurya2005@gmail.com", INK),
    ("Call", "tel:+917569994975", "#1FA855"),
]

TILES = [  # three linked tiles in a row
    dict(file="tile-build", label="BUILD", big="4+", count=None, unit="projects shipped",
         desc="ContextFlow-AI, CarbonFlow-AI, a GenAI DevOps assistant and a from-scratch chess game.",
         bg=BRAND, fg="#FFFFFF", url=PORTFOLIO + "#projects"),
    dict(file="tile-youtube", label="YOUTUBE", big="Surya Builds", count=None, unit="on YouTube",
         desc="Build logs and walkthroughs of the AI, cloud and web projects I ship.",
         bg=RED, fg="#FFFFFF", url="https://www.youtube.com/@SuryaBulids"),
    dict(file="tile-learn", label="LEARN", big="1,286", count=1286, unit="Google Skills points",
         desc="Four Google Cloud skill badges: ADK, BigQuery, Security Command Center, Dataplex.",
         bg=YELLOW, fg=INK, url=PORTFOLIO + "#achievements"),
]

REPOS = [  # (repo name, one-liner, tags)  <- check the repo names match yours
    ("ContextFlow-AI", "A contextual AI workflow that routes prompts through a modular pipeline, so each stage adds context before the model answers.", "Python · Flask · Anthropic API"),
    ("GenAI-DevOps-Assistant", "An assistant built with Google's Agent Development Kit that answers DevOps questions with workflow-aware responses.", "Python · ADK · Vertex AI"),
    ("CarbonFlow-AI", "A carbon footprint awareness platform that shows the climate cost of everyday choices and suggests lower-impact alternatives.", "Python · AI"),
    ("Chess-Game", "Browser chess built from scratch: legal move validation, check and checkmate detection. No libraries, just logic.", "HTML · CSS · JavaScript"),
]
# ───────────────────────────────────────────────────────────

W = 900


def e(s):
    return html.escape(str(s), quote=True)


# ---------- fonts ----------
def font_faces():
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        return ""
    text = "".join(chr(c) for c in range(32, 127)) + "→↗·—•’“”"
    spec = [("JS Serif", "serif", "normal"), ("JS Serif", "serif-italic", "italic"),
            ("JS Sans", "sans", "normal"), ("JS Mono", "mono", "normal")]
    css = ""
    for family, stem, style in spec:
        for ext in ("ttf", "otf", "woff", "woff2"):
            p = ROOT / "fonts" / f"{stem}.{ext}"
            if p.exists():
                opts = subset.Options()
                opts.layout_features = ["*"]
                f = TTFont(p)
                s = subset.Subsetter(opts)
                s.populate(text=text)
                s.subset(f)
                f.flavor = "woff"
                buf = io.BytesIO()
                f.save(buf)
                b64 = base64.b64encode(buf.getvalue()).decode()
                css += (f"@font-face{{font-family:'{family}';font-style:{style};"
                        f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
                break
    return css


ANIM = "" if STATIC else """
@keyframes rise{from{opacity:0;transform:translateY(14px)}}
@keyframes swing{from{opacity:0;transform:translateY(46px) rotate(5deg)}60%{opacity:1;transform:translateY(-6px) rotate(-1deg)}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}60%{transform:scale(1.15)}}
@keyframes fin{from{opacity:0}}
@keyframes sweep{0%,55%{transform:translateX(0)}100%{transform:translateX(1100px)}}
@keyframes pulse{0%{opacity:.9;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}
.r{animation:rise .7s cubic-bezier(.2,.8,.2,1) var(--d,0s) both}
.sw{transform-box:fill-box;transform-origin:50% 100%;animation:swing .95s cubic-bezier(.2,.9,.3,1) var(--d,0s) both}
.gr{transform-box:fill-box;transform-origin:50% 100%;animation:grow .8s cubic-bezier(.2,.8,.2,1) var(--d,0s) both}
.po{transform-box:fill-box;transform-origin:50% 50%;animation:pop .35s ease var(--d,0s) both}
.fin{animation:fin .01s linear var(--d,0s) both}
.sweep{animation:sweep 6s ease-in-out var(--d,0s) infinite}
.ring{transform-box:fill-box;transform-origin:50% 50%;animation:pulse 2s ease-out infinite}
.nudge{animation:nudge 2.2s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.smil{display:none}}
"""

CSS = (font_faces() + """
.serif{font-family:'JS Serif',Georgia,'Times New Roman',serif}
.sans{font-family:'JS Sans',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:'JS Mono',ui-monospace,Menlo,Consolas,monospace;letter-spacing:.12em}
.i{font-style:italic}
""" + ANIM)


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img"><style>{CSS}</style><defs>{defs}</defs>{body}</svg>')


def d(sec):
    return f' style="--d:{sec:.2f}s"'


def fmt(n):
    return f"{int(round(n)):,}"


def count(x, y, n, delay, cls, size, fill, anchor="start", frames=18, step=0.05):
    """Number that counts up: SMIL <set> frames (CSS can't change text) + a final text element."""
    a = f'x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"'
    if STATIC:
        return f'<text {a} class="{cls}">{fmt(n)}</text>'
    fr = []
    for i in range(frames - 1):
        v = n * (1 - (1 - (i + 1) / frames) ** 3)
        fr.append(f'<text {a} class="{cls}" visibility="hidden"><set attributeName="visibility" '
                  f'to="visible" begin="{delay + i * step:.2f}s" dur="{step}s"/>{fmt(v)}</text>')
    fin = f'<text {a} class="{cls} fin"{d(delay + (frames - 1) * step)}>{fmt(n)}</text>'
    return f'<g class="smil">{"".join(fr)}</g>{fin}'


def wrap(text, width):
    return textwrap.wrap(text, width=width)


# ---------- cards ----------
def hero():
    h = 330
    portrait = next((p for p in (ROOT / "assets").glob("portrait.*")), None) if (ROOT / "assets").exists() else None
    if portrait:
        mime = {"png": "png", "jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}[portrait.suffix[1:].lower()]
        b64 = base64.b64encode(portrait.read_bytes()).decode()
        art = (f'<clipPath id="pc"><circle cx="740" cy="165" r="105"/></clipPath>'
               f'<image href="data:image/{mime};base64,{b64}" x="635" y="60" width="210" height="210" '
               f'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>')
    else:
        art = (f'<circle cx="740" cy="165" r="105" fill="{BRAND}"/>'
               f'<text x="740" y="190" text-anchor="middle" class="serif i" font-size="78" fill="#fff">JS.</text>')
    lines = "".join(
        f'<text x="36" y="{262 + 24 * i}" class="sans r" font-size="17" fill="{INK}" fill-opacity=".62"{d(.9 + .1 * i)}>{e(t)}</text>'
        for i, t in enumerate(wrap(TAGLINE, 46)))
    name_attrs = 'x="34" y="214" font-size="92"'
    body = f"""
<rect width="{W}" height="{h}" rx="22" fill="{PAPER}"/>
<g class="r"{d(0)}><circle cx="44" cy="53" r="4.5" fill="{BRAND}"/><circle class="ring" cx="44" cy="53" r="4.5" fill="{BRAND}"/>
<text x="60" y="58" class="mono" font-size="12" fill="{INK}" fill-opacity=".7">{e(STATUS)}</text></g>
<text x="34" y="132" class="serif r" font-size="92" fill="{INK}"{d(.15)}>{e(NAME[0])}</text>
<text {name_attrs} fill="{BRAND}" style="--d:.35s" class="serif r">{e(NAME[1])}</text>
<g clip-path="url(#nm)"><rect class="sweep" x="-200" y="120" width="110" height="110" fill="url(#sh)"{d(2.2)}/></g>
{lines}
<g class="r"{d(1.2)}><text x="36" y="312" class="mono" font-size="11" fill="{INK}" fill-opacity=".5">{e(PORTFOLIO.replace("https://", "").rstrip("/"))}</text></g>
<g class="r"{d(.6)}>{art}</g>"""
    defs = (f'<clipPath id="nm"><text {name_attrs} class="serif">{e(NAME[1])}</text></clipPath>'
            '<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    return svg(W, h, body, defs)


def tile(t, i):
    w, h = 420, 300
    dl = 0.9 + i * 0.18
    big_size = 76 if t["count"] else 54
    if t["count"]:
        big = count(32, 150, t["count"], dl + 0.3, "serif", big_size, t["fg"])
    else:
        big = f'<text x="32" y="140" class="serif r" font-size="{big_size}" fill="{t["fg"]}"{d(dl + .3)}>{e(t["big"])}</text>'
    desc = "".join(
        f'<text x="32" y="{228 + 21 * k}" class="sans" font-size="14.5" fill="{t["fg"]}" fill-opacity=".88">{e(s)}</text>'
        for k, s in enumerate(wrap(t["desc"], 44)[:3]))
    body = f"""
<clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath>
<g class="sw"{d(dl)}>
<rect width="{w}" height="{h}" rx="24" fill="{t['bg']}"/>
<g clip-path="url(#c)"><rect class="sweep" x="-200" y="0" width="110" height="{h}" fill="url(#sh)"{d(dl + 2)}/></g>
<text x="32" y="46" class="mono" font-size="13" fill="{t['fg']}">{e(t['label'])}</text>
<text class="nudge" x="{w - 32}" y="47" text-anchor="end" font-size="20" fill="{t['fg']}">→</text>
{big}
<text x="32" y="{190 if t['count'] else 184}" class="serif i" font-size="30" fill="{t['fg']}">{e(t['unit'])}</text>
{desc}</g>"""
    defs = ('<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    return svg(w, h, body, defs)


def load_days():
    raw = json.loads(DATA.read_text())["days"]
    days = sorted((dt.date.fromisoformat(x["date"]), int(x["count"])) for x in raw)
    last = days[-1][0]
    return [x for x in days if x[0] > last - dt.timedelta(days=365)]


def activity(days):
    h = 360
    cnt = dict(days)
    last = days[-1][0]
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c > 0)
    run = longest = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    cur, day = 0, last
    if cnt.get(day, 0) == 0:
        day -= dt.timedelta(days=1)
    while cnt.get(day, 0) > 0:
        cur += 1
        day -= dt.timedelta(days=1)
    best_day = max(days, key=lambda x: x[1])
    # months
    months, (y, m) = [], (last.year, last.month)
    for _ in range(12):
        months.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    months.reverse()
    per = [sum(c for dd, c in days if (dd.year, dd.month) == ym) for ym in months]
    peak = max(per) or 1
    bars = ""
    for i, (ym, v) in enumerate(zip(months, per)):
        x, bh = 36 + i * 42, max(3, 120 * v / peak)
        top = v == max(per)
        dl = 1.0 + i * 0.06
        bars += (f'<rect class="gr" x="{x}" y="{320 - bh:.1f}" width="34" height="{bh:.1f}" rx="4" '
                 f'fill="{BRAND if top else INK}"{d(dl)}/>'
                 f'<text x="{x + 17}" y="342" text-anchor="middle" class="mono" font-size="10" fill="{INK}" fill-opacity=".55">'
                 f'{dt.date(ym[0], ym[1], 1).strftime("%b").upper()}</text>')
        if top:
            bars += (f'<text class="mono po" x="{x + 17}" y="{320 - bh - 10:.1f}" text-anchor="middle" font-size="13" '
                     f'fill="{BRAND}"{d(1.9)}>{fmt(v)}</text>')

    def block(k, label, value_svg, sub):
        top = 40 + k * 105
        line = f'<line x1="640" x2="864" y1="{top - 8}" y2="{top - 8}" stroke="{INK}" stroke-opacity=".12"/>' if k else ""
        return (f'{line}<g class="r"{d(1.2 + k * .2)}><text x="640" y="{top + 18}" class="mono" font-size="11" '
                f'fill="{INK}" fill-opacity=".55">{label}</text>{value_svg}'
                f'<text x="640" y="{top + 92}" class="sans" font-size="13" fill="{INK}" fill-opacity=".6">{sub}</text></g>')

    streak = count(640, 40 + 70, cur, 1.4, "serif", 52, INK)
    act = (f'<text x="640" y="{40 + 105 + 70}" class="serif" font-size="52" fill="{INK}">{active}'
           f'<tspan fill-opacity=".4"> / {len(days)}</tspan></text>')
    busy = (f'<text x="640" y="{40 + 210 + 70}" class="serif" font-size="52" fill="{BRAND}">{fmt(best_day[1])}</text>')
    body = f"""
<rect width="{W}" height="{h}" rx="22" fill="{PAPER}"/>
<text x="36" y="48" class="mono r" font-size="12" fill="{INK}" fill-opacity=".6"{d(.2)}>THE LAST 12 MONTHS ON GITHUB</text>
{count(34, 128, total, 0.4, "serif", 76, INK)}
<text x="36" y="164" class="serif i r" font-size="30" fill="{INK}"{d(.5)}>contributions</text>
{bars}
{block(0, "CURRENT STREAK", streak, f"days · longest run {longest}")}
{block(1, "ACTIVE DAYS", act, "days with a commit")}
{block(2, "BUSIEST DAY", busy, f"commits on {best_day[0].strftime('%b %-d, %Y')}")}"""
    return svg(W, h, body)


def repo(r, i):
    name, desc, tags = r
    h, col = 170, [BRAND, RED, YELLOW][i % 3]
    dl = 0.3 + i * 0.2
    lines = "".join(f'<text x="36" y="{122 + 22 * k}" class="sans" font-size="15" fill="{INK}" fill-opacity=".68">{e(s)}</text>'
                    for k, s in enumerate(wrap(desc, 100)[:2]))
    body = f"""
<g class="r"{d(dl)}>
<rect width="{W}" height="{h}" rx="20" fill="{PAPER}"/>
<rect x="0" y="28" width="6" height="{h - 56}" rx="3" fill="{col}"/>
<text x="36" y="44" class="mono" font-size="11" fill="{INK}" fill-opacity=".55">FEATURED REPO · {i + 1:02d}</text>
<text x="{W - 56}" y="44" text-anchor="end" class="mono" font-size="11" fill="{INK}" fill-opacity=".55">{e(tags.upper())}</text>
<text class="nudge" x="{W - 36}" y="46" text-anchor="end" font-size="18" fill="{INK}">→</text>
<text x="34" y="98" class="serif" font-size="40" fill="{INK}">{e(name)}</text>
{lines}</g>"""
    return svg(W, h, body)


def graph(days):
    last = days[-1][0]
    start = last - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    cnt = dict(days)
    vals = sorted(c for c in cnt.values() if c > 0)
    cuts = [vals[int(len(vals) * q)] for q in (.25, .5, .75)] if vals else [1, 2, 3]

    def lvl(c):
        return 0 if c == 0 else 1 + sum(c > t for t in cuts)

    cells, labels, prev, day = "", "", None, start
    while day <= last:
        col, row = (day - start).days // 7, (day.weekday() + 1) % 7
        if row == 0 and day.month != prev:
            labels += f'<text x="{26 + col * 16}" y="214" class="mono" font-size="10" fill="{INK}" fill-opacity=".55">{day.strftime("%b").upper()}</text>'
            prev = day.month
        cells += (f'<rect class="po" x="{26 + col * 16}" y="{82 + row * 16}" width="13" height="13" rx="3" '
                  f'fill="{RAMP[lvl(cnt.get(day, 0))]}"{d(.4 + col * .02)}/>')
        day += dt.timedelta(days=1)
    leg = "".join(f'<rect x="{718 + i * 17}" y="224" width="12" height="12" rx="3" fill="{c}"/>' for i, c in enumerate(RAMP))
    body = f"""
<rect width="{W}" height="252" rx="22" fill="{PAPER}"/>
<text x="26" y="52" class="serif" font-size="34" fill="{INK}">Every day, <tspan class="i" fill="{BRAND}">in blue</tspan></text>
<text x="{W - 26}" y="46" text-anchor="end" class="mono" font-size="11" fill="{INK}" fill-opacity=".55">REFRESHED DAILY</text>
{cells}{labels}
<text x="700" y="234" text-anchor="end" class="mono" font-size="10" fill="{INK}" fill-opacity=".55">LESS</text>{leg}
<text x="{718 + 5 * 17 + 6}" y="234" class="mono" font-size="10" fill="{INK}" fill-opacity=".55">MORE</text>"""
    return svg(W, 252, body)


def pill(i, label, color):
    w = 62 + len(label) * 9
    body = f"""
<g class="r"{d(1.6 + i * .08)}>
<rect x="1" y="1" width="{w - 2}" height="42" rx="21" fill="{INK if i == 0 else PAPER}"/>
<circle cx="24" cy="22" r="5.5" fill="{color}"/>
<text x="40" y="27" class="mono" font-size="12" fill="{'#fff' if i == 0 else INK}">{e(label.upper())}</text>
<text class="nudge" x="{w - 22}" y="27" text-anchor="end" font-size="14" fill="{'#fff' if i == 0 else INK}">↗</text></g>"""
    return w, svg(w, 44, body)


# ---------- main ----------
def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")


def main():
    if not DATA.exists():
        raise SystemExit(f"missing {DATA} - run scripts/fetch_contributions.py first")
    OUT.mkdir(exist_ok=True)
    days = load_days()
    write("hero.svg", hero())
    for i, t in enumerate(TILES):
        write(f"{t['file']}.svg", tile(t, i))
    write("activity.svg", activity(days))
    write("graph.svg", graph(days))
    for i, r in enumerate(REPOS):
        write(f"repo-{i + 1}.svg", repo(r, i))
    pills = []
    for label, url, color in SOCIALS:
        if "YOUR_HANDLE" in url:
            print(f"! skipping {label}: set its URL in SOCIALS")
            continue
        w, s = pill(len(pills), label, color)
        write(f"social-{label.lower()}.svg", s)
        pills.append((label, url, w))

    gh = f"https://github.com/{USER}"
    md = [f'<a href="{PORTFOLIO}"><img src="./cards/hero.svg" width="100%" alt="{NAME[0]} {NAME[1].rstrip(".")} - portfolio"/></a>\n',
          "<p>" + "\n".join(f'<a href="{u}"><img src="./cards/social-{l.lower()}.svg" height="40" alt="{l}"/></a>'
                            for l, u, _ in pills) + "</p>\n",
          "\n".join(f'<a href="{t["url"]}"><img src="./cards/{t["file"]}.svg" width="32.5%" alt="{t["label"]}"/></a>' for t in TILES) + "\n",
          f'<a href="{gh}"><img src="./cards/activity.svg" width="100%" alt="Contributions per month"/></a>\n']
    md += [f'<a href="{gh}/{r[0]}"><img src="./cards/repo-{i + 1}.svg" width="100%" alt="{r[0]}"/></a>\n' for i, r in enumerate(REPOS)]
    md.append(f'<a href="{gh}"><img src="./cards/graph.svg" width="100%" alt="Contribution graph"/></a>\n')
    (ROOT / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"rendered {len(list(OUT.glob('*.svg')))} cards{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()
