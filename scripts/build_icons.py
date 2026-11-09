#!/usr/bin/env python3
"""Build the single-color tech stack icons in assets/icons/{light,dark}/.

Usage:
    npm pack simple-icons && tar xzf simple-icons-*.tgz
    python3 scripts/build_icons.py package/icons

Icons come from Simple Icons (CC0). Technologies that Simple Icons does not
ship (C#, OpenAI, Playwright) get a monogram tile drawn here instead.
"""

import re
import sys
from pathlib import Path

from theme import ORANGE_DARK, ORANGE_LIGHT

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icons"

# output file name -> Simple Icons slug
SIMPLE_ICONS = {
    "typescript": "typescript",
    "go": "go",
    "python": "python",
    "javascript": "javascript",
    "html": "html5",
    "css": "css",
    "shell": "gnubash",
    "react": "react",
    "nextjs": "nextdotjs",
    "vite": "vite",
    "tailwindcss": "tailwindcss",
    "chakraui": "chakraui",
    "threejs": "threedotjs",
    "hono": "hono",
    "bun": "bun",
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "firebase": "firebase",
    "postgresql": "postgresql",
    "mysql": "mysql",
    "sqlite": "sqlite",
    "redis": "redis",
    "prisma": "prisma",
    "drizzle": "drizzle",
    "pandas": "pandas",
    "numpy": "numpy",
    "pytorch": "pytorch",
    "jupyter": "jupyter",
    "anthropic": "anthropic",
    "docker": "docker",
    "githubactions": "githubactions",
    "ansible": "ansible",
    "homeassistant": "homeassistant",
    "vitest": "vitest",
}

# output file name -> (title, stroked letter paths inside a 24x24 tile)
MONOGRAMS = {
    "csharp": (
        "C#",
        "M10.7 8.8A4.2 4.2 0 1 0 10.7 15.2"
        "M14.6 8.5V15.5M17.6 8.5V15.5M13.1 10.6H19.1M13.1 13.4H19.1",
    ),
    "openai": (
        "OpenAI",
        "M6 16.5L9.2 7.5L12.4 16.5M7.2 13.4H11.2"
        "M16.4 7.5V16.5M14.8 7.5H18M14.8 16.5H18",
    ),
    "playwright": (
        "Playwright",
        "M5 16.5V7.5H8.2A2.4 2.4 0 0 1 8.2 12.3H5"
        "M11.2 7.5L12.9 16.5L15.1 10.4L17.3 16.5L19 7.5",
    ),
}


def recolor_simple_icon(svg: str, color: str) -> str:
    svg = svg.replace(' role="img"', "")
    return re.sub(r"<svg ", f'<svg fill="{color}" ', svg, count=1)


def monogram(title: str, letters: str, color: str) -> str:
    return (
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        f"<title>{title}</title>"
        '<mask id="m"><rect width="24" height="24" fill="#fff"/>'
        f'<path d="{letters}" fill="none" stroke="#000" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round"/></mask>'
        f'<rect x="1" y="1" width="22" height="22" rx="4" fill="{color}" mask="url(#m)"/>'
        "</svg>\n"
    )


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    source = Path(sys.argv[1])
    for mode, color in (("light", ORANGE_LIGHT), ("dark", ORANGE_DARK)):
        out = OUT / mode
        out.mkdir(parents=True, exist_ok=True)
        for name, slug in SIMPLE_ICONS.items():
            svg = (source / f"{slug}.svg").read_text()
            (out / f"{name}.svg").write_text(recolor_simple_icon(svg, color) + "\n")
        for name, (title, letters) in MONOGRAMS.items():
            (out / f"{name}.svg").write_text(monogram(title, letters, color))


if __name__ == "__main__":
    main()
