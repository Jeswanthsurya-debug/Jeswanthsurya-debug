"""
Pulls your REAL public contribution calendar from GitHub and rebuilds
  data/contributions.json, assets/contrib-heatmap.svg, assets/info-card.svg
so the graph and the four stat tiles always match your actual profile.

  python scripts/live_stats.py            (username comes from profile.json)
"""
import datetime as dt
import html as htmlmod
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from config import load  # noqa: E402

USER = load()["github_username"]


def fetch_days():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-updater)"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    cells = {}
    for tag in re.findall(r"<td\b[^>]*ContributionCalendar-day[^>]*>", page):
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        i = re.search(r'\bid="([^"]+)"', tag)
        if d and i:
            cells[i.group(1)] = d.group(1)
    counts = {}
    for target, text in re.findall(r'<tool-tip\b[^>]*?\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        if target in cells:
            m = re.match(r"\s*(\d+)\s+contribution", htmlmod.unescape(text))
            counts[cells[target]] = int(m.group(1)) if m else 0
    if not cells:
        raise SystemExit("could not read the contribution calendar")
    data = sorted((dt.date.fromisoformat(d), counts.get(d, 0)) for d in cells.values())
    while data[0][0].weekday() != 6:                      # grid must start on a Sunday
        data.insert(0, (data[0][0] - dt.timedelta(days=1), 0))
    return data


def main():
    import make_heatmap as hm
    data = fetch_days()
    st = hm.stats(data)
    # current streak: today may still be empty, don't let that reset it
    cur, seq = 0, list(reversed(data))
    if seq and seq[0][1] == 0:
        seq = seq[1:]
    for _, c in seq:
        if not c:
            break
        cur += 1
    st["current_streak"] = cur

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    cj = os.path.join(ROOT, "data", "contributions.json")
    json.dump({"stats": st, "days": [[d.isoformat(), c] for d, c in data]}, open(cj, "w"), indent=1)
    os.environ["CONTRIB_JSON"] = cj
    open(os.path.join(ROOT, "assets", "contrib-heatmap.svg"), "w").write(hm.svg(data, st))

    import make_info_card as ic
    h = 500
    p = os.path.join(ROOT, "assets", "ascii-portrait.svg")
    if os.path.exists(p):
        m = re.search(r'height="(\d+)"', open(p).read())
        h = int(m.group(1)) if m else h
    svg, need = ic.card(h)
    if need > h:
        svg, _ = ic.card(need)
    open(os.path.join(ROOT, "assets", "info-card.svg"), "w").write(svg)
    print("synced:", st)


if __name__ == "__main__":
    main()
