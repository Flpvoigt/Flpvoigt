"""Gera os SVGs exibidos no README do perfil do GitHub."""

from __future__ import annotations

import datetime as dt
import html
import os
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = os.environ.get("GITHUB_PROFILE_USER", "Flpvoigt")


class Day(TypedDict):
    date: str
    count: int
    level: int


class ContributionsParser(HTMLParser):
    """Extrai dias e tooltips do calendário público do GitHub."""

    def __init__(self) -> None:
        super().__init__()
        self.cells: list[dict[str, str]] = []
        self.tooltips: dict[str, str] = {}
        self._tooltip_for: str | None = None
        self._tooltip_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        classes = attributes.get("class", "").split()

        if tag == "td" and "ContributionCalendar-day" in classes:
            self.cells.append(attributes)
        elif tag == "tool-tip" and attributes.get("for"):
            self._tooltip_for = attributes["for"]
            self._tooltip_text = []

    def handle_data(self, data: str) -> None:
        if self._tooltip_for is not None:
            self._tooltip_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self._tooltip_for is not None:
            self.tooltips[self._tooltip_for] = "".join(self._tooltip_text).strip()
            self._tooltip_for = None
            self._tooltip_text = []

    def days(self) -> list[Day]:
        result: list[Day] = []
        for cell in self.cells:
            date = cell.get("data-date")
            if not date:
                continue

            tooltip = self.tooltips.get(cell.get("id", ""), "")
            match = re.search(r"(\d+) contribution", tooltip, flags=re.IGNORECASE)
            count = int(match.group(1)) if match else 0
            result.append(
                {
                    "date": date,
                    "count": count,
                    "level": int(cell.get("data-level", "0")),
                }
            )

        return sorted(result, key=lambda day: day["date"])


def fetch_contributions() -> list[Day]:
    url = f"https://github.com/users/{USERNAME}/contributions"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Flpvoigt-profile-readme/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        document = response.read().decode("utf-8")

    parser = ContributionsParser()
    parser.feed(document)
    days = parser.days()
    if not days:
        raise RuntimeError(
            "O calendário de contribuições do GitHub não foi encontrado."
        )
    return days


def animation(content: str, index: int) -> str:
    delay = 0.12 + index * 0.07
    return f'<g class="line" style="animation-delay:{delay:.2f}s">{content}</g>'


def generate_profile_card() -> None:
    width, height = 900, 405
    bg = "#0d1117"
    panel = "#111827"
    border = "#30363d"
    text = "#e6edf3"
    muted = "#8b949e"
    blue = "#79c0ff"
    green = "#7ee787"
    violet = "#d2a8ff"

    rows = [
        ("Usuário", "Felipe Voigt"),
        ("Função", "Desenvolvedor de software"),
        ("Empresa", "JJW Sistemas"),
        ("Local", "Timbó · Santa Catarina · Brasil"),
        ("Foco", "Backend · APIs REST · integrações"),
        ("Estudos", "Engenharia de Software"),
        ("Backend", "Java · Spring Boot · Python · Go"),
        ("Dados", "PostgreSQL · SQL · JPA · Hibernate"),
        ("Web", "JavaScript · HTML · CSS"),
        ("Ferramentas", "Maven · Git · GitHub"),
    ]

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="Perfil profissional de Felipe Voigt">'
        ),
        "<style>",
        ".line{opacity:0;transform:translateY(5px);animation:show .45s ease forwards}",
        "@keyframes show{to{opacity:1;transform:translateY(0)}}",
        "</style>",
        f'<rect width="{width}" height="{height}" rx="14" fill="{bg}"/>',
        (
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" '
            f'fill="none" stroke="{border}"/>'
        ),
        f'<rect x="1" y="1" width="{width - 2}" height="36" rx="13" fill="{panel}"/>',
        f'<line x1="0" y1="36" x2="{width}" y2="36" stroke="{border}"/>',
    ]

    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{22 + index * 18}" cy="18" r="5" fill="{color}"/>')

    parts.extend(
        [
            (
                f'<text x="450" y="23" text-anchor="middle" fill="{muted}" font-size="12" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                "felipe@github: ~ $ neofetch</text>"
            ),
            f'<line x1="360" y1="55" x2="360" y2="382" stroke="{border}"/>',
            (
                f'<text x="180" y="125" text-anchor="middle" fill="{green}" font-size="62" '
                'font-weight="700" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                "&lt;/&gt;</text>"
            ),
            (
                f'<text x="180" y="169" text-anchor="middle" fill="{blue}" font-size="23" '
                'font-weight="700" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                "backend</text>"
            ),
            (
                f'<text x="180" y="202" text-anchor="middle" fill="{muted}" font-size="13" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                "APIs · dados · integrações</text>"
            ),
            f'<rect x="70" y="233" width="220" height="1" fill="{border}"/>',
            (
                f'<text x="180" y="270" text-anchor="middle" fill="{text}" font-size="13" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">código simples</text>'
            ),
            (
                f'<text x="180" y="294" text-anchor="middle" fill="{text}" font-size="13" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">regras claras</text>'
            ),
            (
                f'<text x="180" y="318" text-anchor="middle" fill="{text}" font-size="13" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">manutenção tranquila</text>'
            ),
        ]
    )

    y = 70
    for index, (key, value) in enumerate(rows):
        if index == 6:
            parts.append(
                animation(
                    f'<text x="392" y="{y}" fill="{violet}" font-size="13" font-weight="700" '
                    'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">— stack</text>',
                    index,
                )
            )
            y += 28

        row = (
            f'<text x="392" y="{y}" fill="{green}" font-size="13" font-weight="700" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
            f"{html.escape(key)}</text>"
            f'<text x="515" y="{y}" fill="{text}" font-size="13" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
            f"{html.escape(value)}</text>"
        )
        parts.append(animation(row, index))
        y += 27

    parts.append("</svg>")
    (ASSETS / "profile-card.svg").write_text("".join(parts), encoding="utf-8")


def streaks(days: list[Day]) -> tuple[int, int]:
    longest = run = 0
    for day in days:
        if day["count"]:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    index = len(days) - 1
    if index >= 0 and days[index]["count"] == 0:
        index -= 1
    current = 0
    while index >= 0 and days[index]["count"]:
        current += 1
        index -= 1
    return current, longest


def build_grid(days: list[Day]) -> list[list[Day | None]]:
    first = dt.date.fromisoformat(days[0]["date"])
    leading = (first.weekday() + 1) % 7
    flat: list[Day | None] = [None] * leading + list(days)
    while len(flat) % 7:
        flat.append(None)
    return [flat[index : index + 7] for index in range(0, len(flat), 7)]


def generate_contribution_graph(days: list[Day]) -> None:
    width, height = 900, 260
    padding = 22
    left = 48
    top = 68
    cell = 11
    gap = 3
    step = cell + gap
    palette = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")
    bg = "#0d1117"
    border = "#30363d"
    muted = "#8b949e"
    green = "#7ee787"
    blue = "#79c0ff"
    grid = build_grid(days)

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="Contribuições de {USERNAME} no GitHub">'
        ),
        "<style>",
        ".cell{opacity:0;animation:reveal .38s ease forwards}",
        "@keyframes reveal{to{opacity:1}}",
        "</style>",
        f'<rect width="{width}" height="{height}" rx="14" fill="{bg}"/>',
        (
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" '
            f'fill="none" stroke="{border}"/>'
        ),
        f'<line x1="0" y1="36" x2="{width}" y2="36" stroke="{border}"/>',
    ]

    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{22 + index * 18}" cy="18" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="450" y="23" text-anchor="middle" fill="{muted}" font-size="12" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        f"{USERNAME.lower()}@github: ~/contributions --graph</text>"
    )

    seen_months: set[tuple[int, int]] = set()
    for column_index, column in enumerate(grid):
        for day in column:
            if day is None:
                continue
            date = dt.date.fromisoformat(day["date"])
            marker = (date.year, date.month)
            if marker not in seen_months and date.day <= 7:
                seen_months.add(marker)
                parts.append(
                    f'<text x="{left + column_index * step}" y="57" fill="{muted}" font-size="10" '
                    'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                    f"{date.strftime('%b')}</text>"
                )
            break

    for row, label in ((1, "Seg"), (3, "Qua"), (5, "Sex")):
        parts.append(
            f'<text x="{padding}" y="{top + row * step + 9}" fill="{muted}" font-size="9" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{label}</text>'
        )

    for column_index, column in enumerate(grid):
        for row_index, day in enumerate(column):
            if day is None:
                continue
            x = left + column_index * step
            y = top + row_index * step
            level = min(max(day["level"], 0), len(palette) - 1)
            delay = column_index * 0.012 + row_index * 0.018
            word = "contribuição" if day["count"] == 1 else "contribuições"
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{palette[level]}" style="animation-delay:{delay:.3f}s">'
                f"<title>{day['date']}: {day['count']} {word}</title></rect>"
            )

    total = sum(day["count"] for day in days)
    active = sum(day["count"] > 0 for day in days)
    current, longest = streaks(days)
    best = max(days, key=lambda day: day["count"])
    separator_y = top + 7 * step + 16
    parts.extend(
        [
            (
                f'<line x1="{padding}" y1="{separator_y}" x2="{width - padding}" y2="{separator_y}" '
                f'stroke="{border}"/>'
            ),
            (
                f'<text x="{padding}" y="{separator_y + 27}" fill="{green}" font-size="13" font-weight="700" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                f'{total} contribuições <tspan fill="{muted}" font-weight="400">no último ano</tspan></text>'
            ),
            (
                f'<text x="{width - padding}" y="{separator_y + 27}" text-anchor="end" fill="{muted}" font-size="12" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                f'{active} dias ativos · melhor dia: <tspan fill="{blue}">{best["count"]}</tspan></text>'
            ),
            (
                f'<text x="{padding}" y="{separator_y + 51}" fill="{muted}" font-size="12" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">sequência atual '
                f'<tspan fill="{blue}" font-weight="700">{current} dias</tspan> · maior sequência '
                f'<tspan fill="{blue}" font-weight="700">{longest} dias</tspan></text>'
            ),
            (
                f'<text x="{width - padding}" y="{separator_y + 51}" text-anchor="end" fill="{muted}" font-size="11" '
                'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
                f"{days[0]['date']} → {days[-1]['date']}</text>"
            ),
        ]
    )

    parts.append("</svg>")
    (ASSETS / "contribution-graph.svg").write_text("".join(parts), encoding="utf-8")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_profile_card()
    generate_contribution_graph(fetch_contributions())
    print("Assets do perfil gerados em", ASSETS)


if __name__ == "__main__":
    main()
