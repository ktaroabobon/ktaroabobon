#!/usr/bin/env python3
"""Build orange GitHub summary cards in assets/cards/{light,dark}/.

The cards are generated every day by vn7n24fzkq/github-profile-summary-cards
in ktaroabobon/github-profile-summary-cards-example. That action only offers
fixed themes, so this script downloads the "github" and "github_dark" themes
and replaces their accent colors with the profile's orange.

Usage:
    python3 scripts/build_cards.py
    CARDS_SOURCE_REF=some-branch python3 scripts/build_cards.py
"""

import os
import re
import urllib.request
from pathlib import Path

from theme import ORANGE_DARK, ORANGE_LIGHT

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cards"
# Set CARDS_SOURCE_REF to read the cards from another branch of the source repo.
SOURCE = (
    "https://raw.githubusercontent.com/ktaroabobon/github-profile-summary-cards-example/"
    f"{os.environ.get('CARDS_SOURCE_REF', 'master')}/profile-summary-card-output"
)
CARDS = [
    "0-profile-details",
    "1-repos-per-language",
    "2-most-commit-language",
    "3-stats",
    "4-productive-time",
]

PROFILE_TITLE = "ktaroabobon (Keitaro Watanabe)"

# Accent colors used by the upstream "github" and "github_dark" themes.
TITLE = "#0366d6"
CHART = "#40c463"


def mix(color: str, target: str, ratio: float) -> str:
    a = [int(color[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(target[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * ratio):02X}" for x, y in zip(a, b))


def ramp(base: str) -> list[str]:
    """Five distinguishable shades of one hue for the language charts."""
    return [
        base,
        mix(base, "#000000", 0.3),
        mix(base, "#FFFFFF", 0.4),
        mix(base, "#000000", 0.5),
        mix(base, "#FFFFFF", 0.65),
    ]


def recolor(svg: str, orange: str) -> str:
    shades = ramp(orange)

    def shade(index: str) -> str:
        return shades[int(index) % len(shades)]

    # Language legend squares and donut slices: color by position, not language.
    svg = re.sub(
        r'(<rect [^>]*--gpsc-i: (\d+); stroke-width: 1px;" fill=")#[0-9a-fA-F]{3,8}',
        lambda m: m.group(1) + shade(m.group(2)),
        svg,
    )
    svg = re.sub(
        r'(<g class="arc" style="--gpsc-i: (\d+);"><path [^>]*?style="fill: )#[0-9a-fA-F]{3,8}',
        lambda m: m.group(1) + shade(m.group(2)),
        svg,
    )
    # Icons next to the profile details and stats rows.
    svg = re.sub(
        r'(<g [^>]*width="14" height="14" fill=")#[0-9a-fA-F]{3,8}',
        lambda m: m.group(1) + orange,
        svg,
    )
    # Large GitHub mark on the stats card.
    svg = re.sub(
        r'(<g transform="scale\(6\)" style="fill: )#[0-9a-fA-F]{3,8}',
        lambda m: m.group(1) + orange,
        svg,
    )
    # The action cuts the profile title at 22 characters. The chart starts
    # below the title line, so the full title fits without overlapping it.
    svg = re.sub(
        r'(<text [^>]*font-size: 22px;[^>]*>)ktaroabobon \([^<]*\)(</text>)',
        lambda m: m.group(1) + PROFILE_TITLE + m.group(2),
        svg,
        count=1,
    )
    svg = re.sub(TITLE, orange, svg, flags=re.IGNORECASE)
    svg = re.sub(CHART, orange, svg, flags=re.IGNORECASE)
    return svg


def fetch(theme: str, card: str) -> str:
    with urllib.request.urlopen(f"{SOURCE}/{theme}/{card}.svg", timeout=30) as res:
        return res.read().decode("utf-8")


def main() -> None:
    for mode, theme, orange in (
        ("light", "github", ORANGE_LIGHT),
        ("dark", "github_dark", ORANGE_DARK),
    ):
        out = OUT / mode
        out.mkdir(parents=True, exist_ok=True)
        for card in CARDS:
            (out / f"{card}.svg").write_text(recolor(fetch(theme, card), orange))


if __name__ == "__main__":
    main()
