#!/usr/bin/env python3
"""Build the tech stack rows in assets/stack/{light,dark}/<group>.svg.

Each group becomes one SVG: icons in a single row with their names below,
without borders or a background. The icons are read from assets/icons/,
which scripts/build_icons.py generates.

Usage:
    python3 scripts/build_stack.py
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

from theme import ORANGE_DARK, ORANGE_LIGHT

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons"
OUT = ROOT / "assets" / "stack"

# group file name -> [(icon file name, label)]
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

MAX_PER_ROW = 8
SLOT = 100  # 8 slots = 800px, within the ~830px README column on GitHub
ICON = 40
TOP = 4
LABEL_Y = TOP + ICON + 22
HEIGHT = LABEL_Y + 8
FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'


def embed_icon(svg: str, slug: str, x: float, y: float) -> str:
    """Place an icon SVG as a nested <svg> and keep its ids unique."""
    svg = svg.strip()
    svg = re.sub(r"<title>.*?</title>", "", svg)
    svg = svg.replace('id="m"', f'id="m-{slug}"').replace("url(#m)", f"url(#m-{slug})")
    svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', "")
    return svg.replace("<svg ", f'<svg x="{x}" y="{y}" width="{ICON}" height="{ICON}" ', 1)


def build(items: list[tuple[str, str]], mode: str, color: str) -> str:
    if len(items) > MAX_PER_ROW:
        raise ValueError(f"at most {MAX_PER_ROW} items per row")
    width = SLOT * len(items)
    names = ", ".join(label for _, label in items)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" '
        f'viewBox="0 0 {width} {HEIGHT}" role="img">',
        f"<title>{escape(names)}</title>",
        f'<g font-family=\'{FONT}\' font-size="12" fill="{color}" text-anchor="middle">',
    ]
    for i, (slug, label) in enumerate(items):
        center = SLOT * i + SLOT / 2
        icon = (ICONS / mode / f"{slug}.svg").read_text()
        parts.append(embed_icon(icon, slug, center - ICON / 2, TOP))
        parts.append(f'<text x="{center}" y="{LABEL_Y}">{escape(label)}</text>')
    parts.append("</g></svg>\n")
    return "".join(parts)


def main() -> None:
    for mode, color in (("light", ORANGE_LIGHT), ("dark", ORANGE_DARK)):
        out = OUT / mode
        out.mkdir(parents=True, exist_ok=True)
        for group, items in GROUPS.items():
            (out / f"{group}.svg").write_text(build(items, mode, color))


if __name__ == "__main__":
    main()
