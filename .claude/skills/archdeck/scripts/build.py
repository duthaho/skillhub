#!/usr/bin/env python3
"""Assemble an archdeck folder into one self-contained index.html + notes.md, and lint it.

    python3 build.py out/archdeck/<slug>           # lint, then build
    python3 build.py out/archdeck/<slug> --check   # lint only, write nothing

Input:  <deck>/slides/NN-*.html (each one standalone, one <section class="slide">)
        <deck>/assets/deck.css, deck.js
Output: <deck>/index.html — every slide, CSS (plus each slide's <style>) and JS inlined; opens from file://
                            (fonts come from Google Fonts, cached after first open)
        <deck>/notes.md   — narration script per slide and step
        each slide's <section> gets data-sheet="n/total" (its title-block number)
Exit 1 on any ERROR; WARNs are advisory.
"""
import argparse
import html
import re
import sys
from pathlib import Path

SECTION = re.compile(r'<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>.*?</section>', re.S)
NOTES = re.compile(r'<aside\b[^>]*class="[^"]*\bnotes\b[^"]*"[^>]*>(.*?)</aside>', re.S)
NOTE_P = re.compile(r'<p\b([^>]*)>(.*?)</p>', re.S)
H1 = re.compile(r'<h1\b[^>]*>(.*?)</h1>', re.S)
STEP = re.compile(r'\bdata-(step|out)="(\d+)"')
ID = re.compile(r'\bid="([^"]+)"')
# Anything fetched from the network except Google Fonts (the deck's typefaces)
EXTERNAL = re.compile(r'''(?:\bsrc=|<link\b[^>]*\bhref=|url\(|@import\s)\s*["']?\s*(?:https?:)?//'''
                      r'''(?!fonts\.(?:googleapis|gstatic)\.com)''', re.I)
TAGS = re.compile(r'<[^>]+>')
WORDS_WARN = 120  # visible words; past this the slide is a document, not a scene


def text(fragment: str) -> str:
    return html.unescape(re.sub(r'\s+', ' ', TAGS.sub(' ', fragment))).strip()


def lint(path: Path, src: str, errors: list, warns: list):
    name = path.name
    sections = SECTION.findall(src)
    if src.count('<section') != 1 or len(sections) != 1:
        errors.append(f'{name}: needs exactly one <section class="slide"> and no nested <section>')
        return None
    section = sections[0]
    if not H1.search(section):
        errors.append(f'{name}: no <h1 class="title"> — every slide states its claim')
    if EXTERNAL.search(src):
        errors.append(f'{name}: loads an external resource — only Google Fonts may come from the network')

    notes_m = NOTES.search(section)
    body = NOTES.sub('', section)
    steps = {int(v) for _, v in STEP.findall(body)} - {0}
    if steps and steps != set(range(1, max(steps) + 1)):
        missing = sorted(set(range(1, max(steps) + 1)) - steps)
        errors.append(f'{name}: step gap {missing} — a keypress that changes nothing')
    note_steps = set()
    if not notes_m:
        warns.append(f'{name}: no <aside class="notes"> — narration lives there')
    else:
        for attrs, _ in NOTE_P.findall(notes_m.group(1)):
            m = re.search(r'data-step="(\d+)"', attrs)
            note_steps.add(int(m.group(1)) if m else 0)
        silent = sorted(steps - note_steps)
        if silent:
            warns.append(f'{name}: no narration for step(s) {silent}')
    words = len(text(re.sub(r'<(style|script)\b.*?</\1>', ' ', body, flags=re.S)).split())
    if words > WORDS_WARN:
        warns.append(f'{name}: {words} visible words (> {WORDS_WARN}) — move prose into notes')
    return section, notes_m.group(1) if notes_m else '', max(steps) if steps else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deck', type=Path)
    ap.add_argument('--check', action='store_true', help='lint only')
    args = ap.parse_args()

    deck: Path = args.deck
    files = sorted((deck / 'slides').glob('*.html'))
    errors, warns = [], []
    if not files:
        print(f'ERROR: no slides in {deck / "slides"}')
        return 1
    for asset in ('deck.css', 'deck.js'):
        if not (deck / 'assets' / asset).is_file():
            errors.append(f'assets/{asset} missing — copy it from the skill\'s assets/')

    parsed, ids = [], {}
    for f in files:
        src = f.read_text(encoding='utf-8')
        res = lint(f, src, errors, warns)
        if res:
            parsed.append((f, src, *res))
            for i in ID.findall(res[0]):
                ids.setdefault(i, []).append(f.name)
    for i, where in ids.items():
        if len(where) > 1:
            errors.append(f'id "{i}" defined in {", ".join(where)} — prefix ids with the slide number')

    for w in warns:
        print(f'WARN: {w}')
    for e in errors:
        print(f'ERROR: {e}')
    if errors:
        print(f'FAIL — {len(errors)} error(s), {len(warns)} warning(s)')
        return 1

    first = parsed[0][1]
    title_m = re.search(r'<div\b[^>]*class="deck"[^>]*data-title="([^"]*)"', first)
    deck_title = html.unescape(title_m.group(1)) if title_m else deck.name
    lang_m = re.search(r'<html\b[^>]*lang="([^"]+)"', first)
    theme_m = re.search(r'<html\b[^>]*data-theme="([^"]+)"', first)
    total_steps = sum(p[4] for p in parsed)
    summary = f'{len(parsed)} slides, {total_steps} steps'

    if args.check:
        print(f'PASS — {summary} ({len(warns)} warning(s))')
        return 0

    # Stamp each slide's sheet number into its own file too, so a standalone
    # slide shows "Tờ 03 / 12" instead of "01 / 01".
    total = len(parsed)
    for n, p in enumerate(parsed, 1):
        f, src, section = p[0], p[1], p[2]
        stamped = re.sub(r'\sdata-sheet="[^"]*"', '', section.split('>', 1)[0]) + f' data-sheet="{n}/{total}">' \
            + section.split('>', 1)[1]
        if stamped != section:
            f.write_text(src.replace(section, stamped), encoding='utf-8', newline='\n')
        parsed[n - 1] = (f, src, stamped, *p[3:])

    # Slide-scoped <style> blocks sit outside the <section>; carry them over too.
    css = (deck / 'assets' / 'deck.css').read_text(encoding='utf-8')
    for f, src, section, *_ in parsed:
        for block in re.findall(r'<style\b[^>]*>(.*?)</style>', src.replace(section, ''), re.S):
            css += f'\n/* {f.name} */\n{block.strip()}\n'
    js = (deck / 'assets' / 'deck.js').read_text(encoding='utf-8').replace('</script', '<\\/script')
    sections = '\n'.join(p[2] for p in parsed)
    lang = lang_m.group(1) if lang_m else 'vi'
    theme = f' data-theme="{theme_m.group(1)}"' if theme_m else ''
    out = (
        f'<!doctype html>\n<html lang="{lang}"{theme}>\n<head>\n<meta charset="utf-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{html.escape(deck_title)}</title>\n<style>\n{css}\n</style>\n</head>\n<body>\n'
        f'<div class="deck" data-title="{html.escape(deck_title)}">\n{sections}\n</div>\n'
        f'<script>\n{js}\n</script>\n</body>\n</html>\n'
    )
    (deck / 'index.html').write_text(out, encoding='utf-8')

    lines = [f'# {deck_title} — narration', '']
    for n, (f, _, section, notes_html, last) in enumerate(parsed, 1):
        h1 = H1.search(section)
        lines += [f'## {n:02d} · {text(h1.group(1)) if h1 else f.stem}', f'`{f.name}` · {last} step(s)', '']
        for attrs, body in NOTE_P.findall(notes_html):
            m = re.search(r'data-step="(\d+)"', attrs)
            lines.append(f'- **[{m.group(1) if m else 0}]** {text(body)}')
        lines.append('')
    (deck / 'notes.md').write_text('\n'.join(lines), encoding='utf-8')

    print(f'PASS — {summary} ({len(warns)} warning(s)) → {deck / "index.html"}, {deck / "notes.md"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
