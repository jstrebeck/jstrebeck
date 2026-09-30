#!/usr/bin/env python3
"""Render the Argo CD style application rows in img/apps/ from live GitHub data.

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
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWNER = "jstrebeck"
API = "https://api.github.com"

# Argo CD dark palette
BG, ROW, BORDER = "#1c1c1c", "#262626", "#3a3a3a"
TEXT, MUTED, LINK = "#e6e6e6", "#8fa4b1", "#7fb3ff"
OK, WARN, BAD = "#18be94", "#f4c030", "#e96d76"  # WARN kept for future OutOfSync use
FONT = "Inter, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
W, H = 1180, 74


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
    return (f'<path transform="translate({x},{y}) scale(0.55)" fill="{color}" '
            'd="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 '
            '4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 '
            '11.54L12 21.35z"/>')


def check(x, y, color):
    return (f'<circle cx="{x+6}" cy="{y+6}" r="6" fill="{color}"/>'
            f'<polyline points="{x+3},{y+6.2} {x+5.3},{y+8.5} {x+9.2},{y+3.8}" fill="none" '
            'stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')


def row(app, st):
    hname, hcolor = st["health"]
    label = lambda x, y, t: f'<text x="{x}" y="{y}" font-size="12" fill="{MUTED}">{t}</text>'
    value = lambda x, y, t, c=TEXT, w="400": f'<text x="{x}" y="{y}" font-size="12.5" font-weight="{w}" fill="{c}">{escape(t)}</text>'
    src = f"github.com/{OWNER}/{app['repo']}/{app['path']}"
    meta = f"last sync {st['pushed']}"
    if st["language"]:
        meta += f"  ·  {st['language']}"
    if st["stars"]:
        meta += f"  ·  ★ {st['stars']}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="2" fill="{ROW}" stroke="{BORDER}"/>',
           f'<rect x="0" y="0" width="4" height="{H}" fill="{hcolor}"/>',
           # column 1: project / name
           label(22, 28, "Project:"), value(84, 28, app["project"]),
           label(22, 52, "Name:"), value(84, 52, app["name"], LINK, "600"),
           # column 2: source / destination
           label(330, 28, "Source:"), value(410, 28, clip(src, 68)),
           label(330, 52, "Destination:"), value(410, 52, app["destination"]),
           # column 3: revision pill + status
           f'<rect x="868" y="16" width="{max(44, 7*len(st["branch"])+16)}" height="18" rx="9" fill="{BG}" stroke="{BORDER}"/>',
           f'<text x="{868 + max(44, 7*len(st["branch"])+16)/2}" y="29" font-size="11.5" fill="{TEXT}" text-anchor="middle">{escape(st["branch"])}</text>',
           heart(960, 13, hcolor), value(980, 28, hname, hcolor, "600"),
           check(960, 41, OK), value(980, 52, "Synced", OK, "600"),
           # right: meta line
           f'<text x="{W-16}" y="66" font-size="10.5" fill="{MUTED}" text-anchor="end">{escape(meta)}</text>',
           # note under destination
           f'<text x="410" y="66" font-size="10.5" fill="{MUTED}">{escape(clip(app["note"], 80))}</text>',
           '</svg>']
    return "\n".join(out)


def main():
    apps = json.loads((ROOT / "apps.json").read_text())
    outdir = ROOT / "img" / "apps"
    outdir.mkdir(parents=True, exist_ok=True)
    for app in apps:
        st = repo_state(app["repo"])
        (outdir / f"{app['name']}.svg").write_text(row(app, st) + "\n")
        print(f"{app['name']:26} {st['health'][0]:11} last sync {st['pushed']}  {st['language']}")


if __name__ == "__main__":
    main()
