#!/usr/bin/env python3
"""Build the tech stack rows in assets/stack/{light,dark}/<group>.svg.

Each group becomes one SVG: logos in a single row with their names below,
without borders or a background. The logos are the projects' own artwork in
their original colors, stored in assets/logos/ (see assets/logos/SOURCES.md).

Dark theme handling, in order of preference:
1. Use the project's own dark-background file (<slug>-dark.svg) when it exists.
2. Recolor a black logo to white only when no guideline forbids it (RECOLOR).
3. Otherwise keep the logo as is and put it on a light tile (TILE).

Usage:
    python3 scripts/build_stack.py
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "logos"
OUT = ROOT / "assets" / "stack"

# group file name -> [(logo file name, label)]
GROUPS = {
    "languages": [
        ("typescript", "TypeScript"),
        ("go", "Go"),
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("html", "HTML"),
        ("css", "CSS"),
        ("shell", "Shell"),
        ("csharp", "C#"),
    ],
    "frontend": [
        ("react", "React"),
        ("nextjs", "Next.js"),
        ("vite", "Vite"),
        ("tailwindcss", "Tailwind CSS"),
        ("chakraui", "Chakra UI"),
        ("threejs", "Three.js"),
    ],
    "backend": [
        ("hono", "Hono"),
        ("bun", "Bun"),
        ("fastapi", "FastAPI"),
        ("flask", "Flask"),
        ("django", "Django"),
        ("firebase", "Firebase"),
    ],
    "database": [
        ("postgresql", "PostgreSQL"),
        ("mysql", "MySQL"),
        ("sqlite", "SQLite"),
        ("redis", "Redis"),
        ("prisma", "Prisma"),
        ("drizzle", "Drizzle"),
    ],
    "data-and-ai": [
        ("pandas", "pandas"),
        ("numpy", "NumPy"),
        ("pytorch", "PyTorch"),
        ("jupyter", "Jupyter"),
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
    ],
    "infra-and-tools": [
        ("docker", "Docker"),
        ("githubactions", "GitHub Actions"),
        ("ansible", "Ansible"),
        ("homeassistant", "Home Assistant"),
        ("vitest", "Vitest"),
        ("playwright", "Playwright"),
    ],
}

# Logos drawn in the default (black) fill or with currentColor need an
# explicit color. Anthropic's mark uses currentColor on anthropic.com.
BASE_COLOR = {"threejs": "#000000", "openai": "#000000", "anthropic": "#191919"}

# Black logos recolored to white on the dark theme. No guideline found for
# these projects forbids it.
RECOLOR = {
    "threejs": {"#000000": "#FFFFFF"},
    "flask": {"#010101": "#FFFFFF"},
    "prisma": {"#2d3748": "#FFFFFF"},
}

# Dark logos whose guidelines forbid recoloring (Django: keep the official
# colors; MySQL: use unaltered; OpenAI: do not add color; Anthropic: no
# alterations). They stay as they are and get a light tile on the dark theme.
TILE = {"django", "mysql", "openai", "anthropic"}
TILE_COLOR = "#E6EDF3"

# Label colors: GitHub's muted foreground colors.
LABEL = {"light": "#59636E", "dark": "#9198A1"}

MAX_PER_ROW = 8
SLOT = 100  # 8 slots = 800px, within the ~830px README column on GitHub
ICON = 40
TOP = 6
LABEL_Y = TOP + ICON + 22
HEIGHT = LABEL_Y + 8
FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'


def strip_prolog(svg: str) -> str:
    svg = re.sub(r"<\?xml.*?\?>", "", svg, flags=re.S)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<(title|desc|metadata)\b.*?</\1>", "", svg, flags=re.S)
    # Illustrator exports declare namespaces through DOCTYPE entities.
    svg = re.sub(r'\s[\w:]+="&[\w.]+;"', "", svg)
    svg = re.sub(r'\s(?:i|x|graph|a):[\w-]+="[^"]*"', "", svg)
    return svg[svg.index("<svg") :].strip()


def prefix_names(svg: str, prefix: str) -> str:
    """Make ids and class names unique, since all logos share one document."""
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}{m.group(1)})", svg)
    svg = re.sub(r'((?:xlink:)?href)="#([^"]+)"', lambda m: f'{m.group(1)}="#{prefix}{m.group(2)}"', svg)
    svg = re.sub(
        r'\bclass="([^"]+)"',
        lambda m: 'class="' + " ".join(prefix + c for c in m.group(1).split()) + '"',
        svg,
    )
    return re.sub(
        r"<style\b[^>]*>(.*?)</style>",
        lambda m: "<style>" + re.sub(r"\.([A-Za-z_][\w-]*)", rf".{prefix}\1", m.group(1)) + "</style>",
        svg,
        flags=re.S,
    )


def rect_bbox(attrs: str) -> list[tuple[float, float]]:
    w = float(re.search(r'width="([\d.]+)"', attrs).group(1))
    h = float(re.search(r'height="([\d.]+)"', attrs).group(1))
    a, b, c, d, e, f = map(float, re.search(r"matrix\(([^)]+)\)", attrs).group(1).split())
    return [(a * x + c * y + e, b * x + d * y + f) for x, y in ((0, 0), (w, 0), (0, h), (w, h))]


def drizzle_mark(svg: str) -> str:
    """The official Drizzle files are mark + wordmark. Keep the mark (the rects)."""
    rects = re.findall(r"<rect\b[^>]*transform=\"matrix[^>]*/>", svg)
    points = [p for r in rects for p in rect_bbox(r)]
    x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
    x1, y1 = max(p[0] for p in points), max(p[1] for p in points)
    return f'<svg viewBox="{x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f}">' + "".join(rects) + "</svg>"


def load(slug: str, mode: str) -> str:
    dark = LOGOS / f"{slug}-dark.svg"
    path = dark if mode == "dark" and dark.exists() else LOGOS / f"{slug}.svg"
    svg = strip_prolog(path.read_text(encoding="utf-8"))
    if slug == "drizzle":
        svg = drizzle_mark(svg)
    if mode == "dark":
        for old, new in RECOLOR.get(slug, {}).items():
            svg = re.sub(re.escape(old), new, svg, flags=re.IGNORECASE)
    return svg


def embed(slug: str, mode: str, x: float, y: float) -> str:
    svg = prefix_names(load(slug, mode), f"{slug}-")
    root = re.match(r"<svg\b[^>]*>", svg).group(0)
    if "viewBox" not in root:
        w = re.search(r'width="([\d.]+)', root).group(1)
        h = re.search(r'height="([\d.]+)', root).group(1)
        root_new = root.replace("<svg", f'<svg viewBox="0 0 {w} {h}"', 1)
    else:
        root_new = root
    root_new = re.sub(r'\s(?:width|height|x|y|class|data-name)="[^"]*"', "", root_new)
    color = BASE_COLOR.get(slug)
    if color and mode == "dark" and slug in RECOLOR:
        color = RECOLOR[slug].get(color, color)
    paint = f' fill="{color}" color="{color}"' if color and "fill=" not in root_new else (
        f' color="{color}"' if color else ""
    )
    root_new = root_new.replace("<svg", f'<svg x="{x}" y="{y}" width="{ICON}" height="{ICON}"{paint}', 1)
    out = svg.replace(root, root_new, 1)
    if mode == "dark" and slug in TILE:
        pad = 6
        tile = (
            f'<rect x="{x - pad}" y="{y - pad}" width="{ICON + 2 * pad}" height="{ICON + 2 * pad}" '
            f'rx="8" fill="{TILE_COLOR}"/>'
        )
        out = tile + out.replace(
            f'x="{x}" y="{y}" width="{ICON}" height="{ICON}"',
            f'x="{x + 2}" y="{y + 2}" width="{ICON - 4}" height="{ICON - 4}"',
            1,
        )
    return out


def build(items: list[tuple[str, str]], mode: str) -> str:
    if len(items) > MAX_PER_ROW:
        raise ValueError(f"at most {MAX_PER_ROW} items per row")
    # Every group has the same width, so the rows scale by the same ratio on
    # narrow screens and the logos keep one size. Shorter rows stay left-aligned.
    width = SLOT * MAX_PER_ROW
    names = ", ".join(label for _, label in items)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{HEIGHT}" viewBox="0 0 {width} {HEIGHT}" role="img">',
        f"<title>{escape(names)}</title>",
    ]
    for i, (slug, label) in enumerate(items):
        center = SLOT * i + SLOT / 2
        parts.append(embed(slug, mode, center - ICON / 2, TOP))
        parts.append(
            f'<text x="{center}" y="{LABEL_Y}" font-family=\'{FONT}\' font-size="12" '
            f'fill="{LABEL[mode]}" text-anchor="middle">{escape(label)}</text>'
        )
    parts.append("</svg>\n")
    return "".join(parts)


def main() -> None:
    for mode in ("light", "dark"):
        out = OUT / mode
        out.mkdir(parents=True, exist_ok=True)
        for group, items in GROUPS.items():
            (out / f"{group}.svg").write_text(build(items, mode), encoding="utf-8")


if __name__ == "__main__":
    main()
