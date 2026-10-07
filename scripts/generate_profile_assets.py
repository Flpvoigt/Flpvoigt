"""Gera os SVGs animados exibidos no README do perfil."""

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
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BG, BG_TOP, BORDER = "#0d1117", "#111722", "#30363d"
TEXT, MUTED = "#c9d1d9", "#7d8590"
GREEN, BLUE, VIOLET = "#a8e6c1", "#a3d8e8", "#a9c9ff"


class Day(TypedDict):
    date: str
    count: int
    level: int


class ContributionsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cells: list[dict[str, str]] = []
        self.tips: dict[str, str] = {}
        self.target: str | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "td" and "ContributionCalendar-day" in values.get("class", "").split():
            self.cells.append(values)
        elif tag == "tool-tip" and values.get("for"):
            self.target, self.text = values["for"], []

    def handle_data(self, data: str) -> None:
        if self.target is not None:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self.target is not None:
            self.tips[self.target] = "".join(self.text).strip()
            self.target = None

    def days(self) -> list[Day]:
        result: list[Day] = []
        for cell in self.cells:
            date = cell.get("data-date")
            if not date:
                continue
            match = re.search(r"(\d+) contribution", self.tips.get(cell.get("id", ""), ""), re.I)
            result.append({"date": date, "count": int(match.group(1)) if match else 0, "level": int(cell.get("data-level", "0"))})
        return sorted(result, key=lambda day: day["date"])


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Flpvoigt-profile-readme/2.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def contributions() -> list[Day]:
    parser = ContributionsParser()
    parser.feed(get(f"https://github.com/users/{USERNAME}/contributions").decode())
    days = parser.days()
    if not days:
        raise RuntimeError("Calendário público de contribuições não encontrado.")
    return days


def terminal(title: str, gradient: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="568" viewBox="0 0 520 568" font-family="{FONT}" role="img">',
        f'<defs><linearGradient id="{gradient}" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="520" height="568" rx="12" fill="url(#{gradient})"/><rect x=".5" y=".5" width="519" height="567" rx="12" fill="none" stroke="{BORDER}"/>',
        f'<line x1="0" y1="30" x2="520" y2="30" stroke="{BORDER}"/><circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="52" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="260" y="19" fill="{MUTED}" font-size="12" text-anchor="middle">{html.escape(title)}</text>',
    ]


SPIDER_ART = """           ;               ,
         ,;                 '.
        ;:                   :;
       ::                     ::
       ::                     ::
       ':                     :
        :.                    :
     ;' ::                   ::  '
    .'  ';                   ;'  '.
   ::    :;                 ;:    ::
   ;      :;.             ,;:     ::
   :;      :;:           ,;\"      ::
   ::.      ':;  ..,.;  ;:'     ,.;:
    \"'\"...   '::,::::: ;:   .;.;\"\"'
        '\"\"\"....;:::::;,;.;\"\"\"
    .:::.....'\"':::::::'\",...;::::;.
   ;:' '\"\"'\"\";.,;:::::;.'\"\"\"\"\"\"  ':;
  ::'         ;::;:::;::..         :;
 ::         ,;:::::::::::;:..       ::
 ;'     ,;;:;::::::::::::::;\";..    ':.
::     ;:\"  ::::::::::::::::  \":     ::
 :.    ::   ::::::::::::::::   :     ;
  ;    ::   ::::::::::::::::   :    ;
   '   ::   :::::::::.:::::'  ,:   '
    '  ::    :::::::::::::\"   ::
       ::     ':::::::::\"'    ::
       ':       \"\"\"\"\"\"\"'      ::
        ::                   ;:
        ':;                 ;:\"
           ';              ,;'
            \"'           '\"
              '""".splitlines()

SPIDER_RED = {20: (17, 22), 21: (18, 21), 22: (19, 21), 23: (18, 21), 24: (17, 22)}


def spider_text(line: str, index: int) -> str:
    if index not in SPIDER_RED:
        return html.escape(line)
    start, end = SPIDER_RED[index]
    return (html.escape(line[:start]) + '<tspan fill="#ff4d6d">' +
            html.escape(line[start:end]) + "</tspan>" + html.escape(line[end:]))


def portrait() -> None:
    parts = terminal(f"{USERNAME.lower()}@github: ~$ ./portrait.sh", "portrait-bg")
    cell_width, left = 8, (520 - max(map(len, SPIDER_ART)) * 8) / 2
    parts.append('<defs><filter id="red-glow"><feGaussianBlur stdDeviation="1.2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    for index, line in enumerate(SPIDER_ART):
        y, begin, duration = 51 + index * 15, index * .11, .11
        width = max(len(line), 1) * cell_width
        parts += [
            f'<clipPath id="l{index}"><rect x="{left:.1f}" y="{y - 12}" height="15" width="0"><animate attributeName="width" from="0" to="{width:.1f}" begin="{begin:.3f}s" dur="{duration}s" fill="freeze"/></rect></clipPath>',
            f'<g clip-path="url(#l{index})" filter="url(#red-glow)"><text xml:space="preserve" x="{left:.1f}" y="{y}" fill="{TEXT}" font-size="13">{spider_text(line, index)}</text></g>',
            f'<rect y="{y - 11}" width="8" height="13" fill="{TEXT}" opacity="0"><animate attributeName="x" from="{left:.1f}" to="{left + width:.1f}" begin="{begin:.3f}s" dur="{duration}s" fill="freeze"/><set attributeName="opacity" to=".85" begin="{begin:.3f}s"/><set attributeName="opacity" to="0" begin="{begin + duration:.3f}s"/></rect>',
        ]
    parts.append("</svg>")
    parts.insert(-1, f'<line x1="0" y1="535" x2="520" y2="535" stroke="{BORDER}"/><text x="20" y="556" fill="{MUTED}" font-size="11">spider-sense: <tspan fill="#ff4d6d">online</tspan> · web-slinger mode</text><rect x="333" y="545" width="7" height="12" fill="{TEXT}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    (ASSETS / "spider-terminal.svg").write_text("".join(parts), encoding="utf-8")


def row(y: int, label: str, value: str, delay: float) -> str:
    return (f'<g opacity="0" transform="translate(0,5)"><text x="20" y="{y}" fill="{GREEN}" font-size="12.5" font-weight="700">{html.escape(label)}</text><text x="120" y="{y}" fill="{TEXT}" font-size="12.5">{html.escape(value)}</text>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".4s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{delay:.2f}s" dur=".4s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></g>')


def section(y: int, name: str, delay: float) -> str:
    start = 32 + len(name) * 7.5
    return (f'<g opacity="0" transform="translate(0,5)"><text x="20" y="{y}" fill="{VIOLET}" font-size="12.5" font-weight="700">— {name}</text><line x1="{start:.0f}" y1="{y - 4}" x2="500" y2="{y - 4}" stroke="{BORDER}"/>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".4s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{delay:.2f}s" dur=".4s" fill="freeze"/></g>')


def info_card() -> None:
    parts = terminal(f"{USERNAME.lower()}@github: ~$ neofetch", "info-bg")
    parts.append(f'<g opacity="0" transform="translate(0,5)"><text x="20" y="60" font-size="14" font-weight="700"><tspan fill="{GREEN}">felipe</tspan><tspan fill="{MUTED}">@</tspan><tspan fill="{BLUE}">github</tspan></text><line x1="128" y1="56" x2="500" y2="56" stroke="{BORDER}"/><animate attributeName="opacity" from="0" to="1" begin=".15s" dur=".4s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin=".15s" dur=".4s" fill="freeze"/></g>')
    groups = [
        ([(82, "Now", "Desenvolvedor @ JJW Sistemas"), (104, "Edu", "Engenharia de Software"), (126, "Local", "Timbó, SC · Brasil")], .21),
        ([(180, "Backend", "Java, Spring Boot, Python, Go"), (202, "Data", "PostgreSQL, SQL, JPA, Hibernate"), (224, "Web", "JavaScript, HTML, CSS"), (246, "Tools", "Maven, Git, GitHub")], .51),
        ([(302, "Build", "APIs REST e integrações"), (324, "Care", "Código limpo e manutenção simples"), (346, "Learn", "Arquitetura e automação")], .87),
        ([(402, "GitHub", "github.com/Flpvoigt"), (424, "Instagram", "instagram.com/flpvoigt")], 1.17),
    ]
    parts += [row(y, label, value, start + index * .06) for rows, start in groups for index, (y, label, value) in enumerate(rows)]
    parts += [section(158, "Stack", .45), section(280, "Focus", .81), section(380, "Links", 1.11)]
    parts.append('<g opacity="0"><rect x="20" y="462" width="18" height="18" rx="3" fill="#a8e6c1"/><rect x="43" y="462" width="18" height="18" rx="3" fill="#5c9e78"/><rect x="66" y="462" width="18" height="18" rx="3" fill="#3d6f52"/><rect x="89" y="462" width="18" height="18" rx="3" fill="#a3d8e8"/><rect x="112" y="462" width="18" height="18" rx="3" fill="#a9c9ff"/><animate attributeName="opacity" from="0" to="1" begin="1.35s" dur=".5s" fill="freeze"/></g>')
    parts.append(f'<text x="20" y="510" fill="{MUTED}" font-size="11" opacity="0">Automatizando tarefas para ter mais tempo<tspan x="20" dy="16">de complicar outras.</tspan><animate attributeName="opacity" from="0" to="1" begin="1.5s" dur=".5s" fill="freeze"/></text>')
    parts.append(f'<g opacity="0"><text x="20" y="554" fill="{GREEN}" font-size="11">felipe@github</text><text x="108" y="554" fill="{MUTED}" font-size="11">:~$</text><rect x="137" y="544" width="7" height="12" fill="{TEXT}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect><animate attributeName="opacity" from="0" to="1" begin="1.8s" dur=".4s" fill="freeze"/></g></svg>')
    (ASSETS / "info-card-v2.svg").write_text("".join(parts), encoding="utf-8")


def grid(days: list[Day]) -> list[list[Day | None]]:
    first = dt.date.fromisoformat(days[0]["date"])
    flat: list[Day | None] = [None] * ((first.weekday() + 1) % 7) + list(days)
    flat += [None] * ((-len(flat)) % 7)
    return [flat[index:index + 7] for index in range(0, len(flat), 7)]


def heatmap(days: list[Day]) -> None:
    current_year = max(dt.date.fromisoformat(day["date"]).year for day in days)
    days = [day for day in days if dt.date.fromisoformat(day["date"]).year == current_year]
    data = grid(days)
    palette = ("#20272b", "#176b42", "#219653", "#3dcc6f", "#8ff0ae")
    width, height, left, top, step, cell = 1040, 260, 56, 42, 24, 19
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}" role="img" aria-label="Contribuições de {USERNAME}">', '<style>.c{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .55s ease-out both}.g{animation:pop .55s ease-out both,flash .7s ease-out both}@keyframes pop{0%{opacity:0;transform:scale(.2)}60%{opacity:1;transform:scale(1.1)}100%{opacity:1;transform:scale(1)}}@keyframes flash{0%,45%{filter:brightness(2.4)}100%{filter:brightness(1)}}@media(prefers-reduced-motion:reduce){.c{opacity:1!important;animation:none!important}}</style>']
    seen: set[tuple[int, int]] = set()
    for column, week in enumerate(data):
        for day in week:
            if day is None:
                continue
            date = dt.date.fromisoformat(day["date"])
            marker = (date.year, date.month)
            if marker not in seen and date.day <= 7:
                seen.add(marker)
                parts.append(f'<text x="{left + column * step}" y="25" fill="{MUTED}" font-size="14">{date.strftime("%b")}</text>')
            break
    for line, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="8" y="{top + line * step + 15}" fill="{MUTED}" font-size="14">{label}</text>')
    for column, week in enumerate(data):
        for line, day in enumerate(week):
            if day is None:
                continue
            level = min(max(day["level"], 0), 4)
            parts.append(f'<rect class="c{" g" if level else ""}" x="{left + column * step}" y="{top + line * step}" width="{cell}" height="{cell}" rx="3.5" fill="{palette[level]}" style="animation-delay:{column * .073 + line * .011:.3f}s"><title>{day["date"]}: {day["count"]} contribuições</title></rect>')
    total = sum(day["count"] for day in days)
    footer_y = top + 7 * step + 30
    parts += [f'<text x="{left}" y="{footer_y}" fill="{TEXT}" font-size="17" font-weight="700">{total:,} contribuições em {current_year}</text>', f'<text x="{width - 18}" y="{footer_y}" text-anchor="end" fill="{MUTED}" font-size="12">menos  <tspan fill="{palette[0]}">■</tspan>  <tspan fill="{palette[1]}">■</tspan>  <tspan fill="{palette[2]}">■</tspan>  <tspan fill="{palette[3]}">■</tspan>  <tspan fill="{palette[4]}">■</tspan>  mais</text>', '</svg>']
    (ASSETS / "contrib-heatmap-v3.svg").write_text("".join(parts), encoding="utf-8")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    heatmap(contributions())
    portrait()
    info_card()
    print("Assets do perfil gerados em", ASSETS)


if __name__ == "__main__":
    main()
