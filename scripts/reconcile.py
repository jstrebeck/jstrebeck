#!/usr/bin/env python3
"""Render the Argo CD style application rows in img/apps/, the Grafana style
contribution heatmap in img/contributions.svg, and the latest-post cards in
img/posts/ (plus their grid in README.md) from live GitHub and RSS data.

Each entry in apps.json becomes one SVG row. Project, destination and path are
declared in apps.json; description, language, stars, last push and the latest
CI conclusion come from the GitHub API at render time. Run daily by the
reconcile workflow, or by hand:

    GH_TOKEN=$(gh auth token) scripts/reconcile.py
"""
import datetime as dt
import json
import os
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWNER = "jstrebeck"
API = "https://api.github.com"

# Argo CD dark palette
BG, ROW, BORDER = "#1c1c1c", "#262626", "#3a3a3a"
TEXT, MUTED, LINK = "#e6e6e6", "#8fa4b1", "#7fb3ff"
OK, WARN, BAD = "#18be94", "#f4c030", "#e96d76"  # WARN kept for future OutOfSync use
FONT = "Inter, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
W, H = 1100, 104


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "jstrebeck-profile-reconcile"})
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def repo_state(repo):
    meta = get(f"{API}/repos/{OWNER}/{repo}")
    branch = meta["default_branch"]
    runs = get(f"{API}/repos/{OWNER}/{repo}/actions/runs?branch={branch}&status=completed&per_page=10")
    # Skipped and cancelled runs say nothing about health; use the newest real result.
    decisive = [r for r in runs.get("workflow_runs", []) if r["conclusion"] in ("success", "failure", "timed_out")]
    if not decisive:
        health = ("Healthy", OK)          # nothing to fail: GitOps says healthy
    elif decisive[0]["conclusion"] == "success":
        health = ("Healthy", OK)
    else:
        health = ("Degraded", BAD)
    pushed = dt.datetime.fromisoformat(meta["pushed_at"].replace("Z", "+00:00"))
    return {
        "description": meta.get("description") or "",
        "language": meta.get("language") or "",
        "stars": meta.get("stargazers_count", 0),
        "branch": branch,
        "pushed": pushed.strftime("%Y-%m-%d"),
        "health": health,
    }


def clip(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def heart(x, y, color):
    return (f'<path transform="translate({x},{y}) scale(0.7)" fill="{color}" '
            'd="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 '
            '4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 '
            '11.54L12 21.35z"/>')


def check(x, y, color):
    return (f'<circle cx="{x+8}" cy="{y+8}" r="8" fill="{color}"/>'
            f'<polyline points="{x+4},{y+8.3} {x+7},{y+11.3} {x+12.3},{y+5}" fill="none" '
            'stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')


def row(app, st):
    hname, hcolor = st["health"]
    label = lambda x, y, t: f'<text x="{x}" y="{y}" font-size="15" fill="{MUTED}">{t}</text>'
    value = lambda x, y, t, c=TEXT, w="400", fs=16.5: f'<text x="{x}" y="{y}" font-size="{fs}" font-weight="{w}" fill="{c}">{escape(t)}</text>'
    src = f"{app['repo']}/{app['path']}"
    meta = f"last sync {st['pushed']}"
    if st["language"]:
        meta += f"  ·  {st['language']}"
    if st["stars"]:
        meta += f"  ·  ★ {st['stars']}"
    pill_w = max(60, int(9.5 * len(st["branch"])) + 24)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="3" fill="{ROW}" stroke="{BORDER}"/>',
           f'<rect x="0" y="0" width="6" height="{H}" fill="{hcolor}"/>',
           # column 1: project / name / meta
           label(28, 36, "Project:"), value(112, 36, app["project"]),
           label(28, 64, "Name:"), value(112, 64, app["name"], LINK, "600"),
           f'<text x="28" y="90" font-size="12.5" fill="{MUTED}">{escape(meta)}</text>',
           # column 2: source / destination / note
           label(385, 36, "Source:"), value(495, 36, clip(src, 46), TEXT, "400", 15.5),
           label(385, 64, "Destination:"), value(495, 64, app["destination"]),
           f'<text x="495" y="90" font-size="12.5" fill="{MUTED}">{escape(clip(app["note"], 60))}</text>',
           # column 3: revision pill, health, sync
           f'<rect x="935" y="16" width="{pill_w}" height="24" rx="12" fill="{BG}" stroke="{BORDER}"/>',
           f'<text x="{935 + pill_w/2}" y="33" font-size="14" fill="{TEXT}" text-anchor="middle">{escape(st["branch"])}</text>',
           heart(935, 48, hcolor), value(960, 64, hname, hcolor, "600", 16),
           check(936, 73, OK), value(960, 87, "Synced", OK, "600", 16),
           '</svg>']
    return "\n".join(out)


# Grafana dark palette for the heatmap panel
G_BG, G_PANEL, G_BORDER, G_TEXT, G_MUTED = "#111217", "#181b1f", "#2c3235", "#ccccdc", "#9fa7b3"
G_EMPTY = "#22252b"
G_SCALE = ["#2f5d33", "#468f45", "#5fad57", "#73bf69", "#96d98d"]


def graphql(query, variables):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(f"{API}/graphql", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json",
                                          "User-Agent": "jstrebeck-profile-reconcile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]


def contribution_calendar():
    q = """query($login: String!) { user(login: $login) { contributionsCollection {
            contributionCalendar { totalContributions
              weeks { contributionDays { date contributionCount } } } } } }"""
    cal = graphql(q, {"login": OWNER})["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    return cal["totalContributions"], weeks


def heatmap(total, weeks):
    cell, gap, x0, y0 = 17, 3, 72, 60
    step = cell + gap
    W, H = 1180, y0 + 7 * step + 34
    # thresholds from the nonzero distribution so the scale tracks real activity
    counts = sorted(c for w in weeks for _, c in w if c > 0)
    def q(p):
        return counts[min(len(counts) - 1, int(p * len(counts)))] if counts else 1
    edges = [q(0.25), q(0.5), q(0.75), q(0.9)]
    def color(c):
        if c == 0:
            return G_EMPTY
        return G_SCALE[sum(c > e for e in edges)]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="3" fill="{G_PANEL}" stroke="{G_BORDER}"/>',
           f'<text x="14" y="24" font-size="13" fill="{G_TEXT}">Contributions · last 12 months</text>',
           f'<text x="{W-14}" y="27" font-size="22" font-weight="700" fill="#ffffff" text-anchor="end">{total:,}</text>',
           f'<text x="{W-14}" y="42" font-size="11" fill="{G_MUTED}" text-anchor="end">contributions</text>']
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        out.append(f'<text x="{x0-10}" y="{y0 + row*step + 13}" font-size="11" fill="{G_MUTED}" text-anchor="end">{label}</text>')
    last_month = None
    for wi, week in enumerate(weeks):
        x = x0 + wi * step
        month = week[0][0][:7]
        # Label the first week of each month, except a partial first week that
        # would collide with the label for the month starting right after it.
        starts_partial = wi == 0 and len(weeks) > 1 and weeks[1][0][0][:7] != month
        if month != last_month and wi < len(weeks) - 1 and not starts_partial:
            if True:
                out.append(f'<text x="{x}" y="{y0-8}" font-size="11" fill="{G_MUTED}">'
                           f'{dt.date.fromisoformat(week[0][0]).strftime("%b")}</text>')
            last_month = month
        for di, (date, c) in enumerate(week):
            y = y0 + (dt.date.fromisoformat(date).weekday() + 1) % 7 * step
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{color(c)}"><title>{date}: {c}</title></rect>')
    # legend
    lx = W - 14 - (len(G_SCALE) + 1) * (12 + 3) - 60
    ly = H - 22
    out.append(f'<text x="{lx-6}" y="{ly+10}" font-size="11" fill="{G_MUTED}" text-anchor="end">Less</text>')
    for i, col in enumerate([G_EMPTY] + G_SCALE):
        out.append(f'<rect x="{lx + i*15}" y="{ly}" width="12" height="12" rx="2" fill="{col}"/>')
    out.append(f'<text x="{lx + 6*15 + 4}" y="{ly+10}" font-size="11" fill="{G_MUTED}">More</text>')
    out.append(f'<text x="14" y="{H-12}" font-size="10.5" fill="{G_MUTED}">Source: GitHub GraphQL · rendered by scripts/reconcile.py</text>')
    out.append('</svg>')
    return "\n".join(out)


FEED = "https://strebeck.net/posts/index.xml"
POST_COUNT = 6
POSTS_START, POSTS_END = "<!-- POSTS:START -->", "<!-- POSTS:END -->"


def wrap(text, width, max_lines):
    """Greedy word wrap to roughly `width` characters, ellipsized at max_lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: width - 1].rstrip(" ,.;:") + "…"
    return lines


def latest_posts():
    req = urllib.request.Request(FEED, headers={"User-Agent": "jstrebeck-profile-reconcile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    posts = []
    for item in root.iter("item"):
        posts.append({
            "title": item.findtext("title", "").strip(),
            "url": item.findtext("link", "").strip(),
            "date": parsedate_to_datetime(item.findtext("pubDate")),
            "summary": " ".join(item.findtext("description", "").split()),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts[:POST_COUNT]


def post_card(post):
    W, H = 380, 168
    title = wrap(post["title"], 40, 2)
    summary = wrap(post["summary"], 60, 3)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="3" fill="{G_PANEL}" stroke="{G_BORDER}"/>',
           f'<rect x="0" y="0" width="{W}" height="3" rx="1.5" fill="#ff780a"/>',
           f'<text x="16" y="28" font-size="11" fill="{G_MUTED}">{post["date"].strftime("%b %d, %Y").upper()}</text>',
           f'<text x="{W-16}" y="28" font-size="11" fill="{G_MUTED}" text-anchor="end">strebeck.net</text>']
    y = 52
    for line in title:
        out.append(f'<text x="16" y="{y}" font-size="15" font-weight="600" fill="#ffffff">{escape(line)}</text>')
        y += 20
    y += 6
    for line in summary:
        out.append(f'<text x="16" y="{y}" font-size="12" fill="{G_TEXT}">{escape(line)}</text>')
        y += 16
    out.append(f'<text x="{W-16}" y="{H-14}" font-size="11.5" font-weight="600" fill="#ff780a" text-anchor="end">Read the post →</text>')
    out.append('</svg>')
    return "\n".join(out)


def post_grid(posts, cols=3):
    cells = []
    for i, post in enumerate(posts, 1):
        cells.append(f'    <td width="{100//cols}%" valign="top"><a href="{post["url"]}">'
                     f'<img src="img/posts/post-{i}.svg" alt="{escape(post["title"])}" width="100%"></a></td>')
    rows = ["  <tr>\n" + "\n".join(cells[i:i+cols]) + "\n  </tr>" for i in range(0, len(cells), cols)]
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def write_posts(posts):
    outdir = ROOT / "img" / "posts"
    outdir.mkdir(parents=True, exist_ok=True)
    for i, post in enumerate(posts, 1):
        (outdir / f"post-{i}.svg").write_text(post_card(post) + "\n")
    readme = ROOT / "README.md"
    text = readme.read_text()
    a, b = text.index(POSTS_START) + len(POSTS_START), text.index(POSTS_END)
    readme.write_text(text[:a] + "\n" + post_grid(posts) + "\n" + text[b:])


def main():
    apps = json.loads((ROOT / "apps.json").read_text())
    outdir = ROOT / "img" / "apps"
    outdir.mkdir(parents=True, exist_ok=True)
    for app in apps:
        st = repo_state(app["repo"])
        (outdir / f"{app['name']}.svg").write_text(row(app, st) + "\n")
        print(f"{app['name']:26} {st['health'][0]:11} last sync {st['pushed']}  {st['language']}")
    total, weeks = contribution_calendar()
    (ROOT / "img" / "contributions.svg").write_text(heatmap(total, weeks) + "\n")
    print(f"contributions              {total} over {len(weeks)} weeks")
    posts = latest_posts()
    write_posts(posts)
    print(f"posts                      {len(posts)} cards, newest {posts[0]['date']:%Y-%m-%d}")


if __name__ == "__main__":
    main()
