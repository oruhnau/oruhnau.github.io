#!/usr/bin/env python3
"""Build the CV PDF from _data/cv.yml + _bibliography/papers.bib with RenderCV.

Usage (from the repository root):
    python bin/build_cv.py            # writes assets/pdf/Oliver_Ruhnau_CV.pdf

Requirements: pip install -r requirements.txt (RenderCV is pinned because
assets/rendercv/moderncv/ overrides some of its templates).
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import bibtexparser
import yaml
from pylatexenc.latex2text import LatexNodes2Text

ROOT = Path(__file__).resolve().parent.parent
CV_FILE = ROOT / "_data" / "cv.yml"
BIB_FILE = ROOT / "_bibliography" / "papers.bib"
CONFIG_DIR = ROOT / "assets" / "rendercv"
OUTPUT_PDF = ROOT / "assets" / "pdf" / "Oliver_Ruhnau_CV.pdf"

OWN_NAME = "Ruhnau, O."
MAX_AUTHORS = 7  # longer author lists are shortened to "A, B, C, et al."

# CV publication sections, in order. Section is chosen by the entry's
# `keywords` field, or else by its BibTeX type.
SECTIONS = [
    ("peer-reviewed", "Publications – full peer review"),
    ("working-paper", "Publications – working papers & works in progress"),
    ("proceedings", "Publications – proceedings, dissertation & book chapters"),
    ("report", "Publications – commissioned studies"),
    ("software", "Publications – software & data"),
    ("commentary", "Publications – commentaries"),
]
DEFAULT_SECTION_BY_TYPE = {"article": "peer-reviewed", "unpublished": "working-paper"}
INSERT_AFTER = "Research interests"

_latex = LatexNodes2Text()


def clean(text: str) -> str:
    """LaTeX -> plain unicode, collapse whitespace."""
    text = _latex.latex_to_text(text or "")
    return re.sub(r"\s+", " ", text).strip()


def format_authors(raw: str) -> str:
    names = [n.strip() for n in re.split(r"\s+and\s+", raw) if n.strip()]
    et_al = names and names[-1].lower() == "others"
    if et_al:
        names = names[:-1]
    names = [clean(n) for n in names]
    if len(names) > MAX_AUTHORS:
        # keep at least three names, and never cut off the own name
        keep = max(3, names.index(OWN_NAME) + 1 if OWN_NAME in names else 3)
        if keep < len(names):
            names, et_al = names[:keep], True
    names = [f"**{n}**" if n == OWN_NAME else n for n in names]
    return ", ".join(names) + (", et al." if et_al else "")


def venue(entry) -> str:
    f = {k: clean(v.value) for k, v in entry.fields_dict.items()}
    t = entry.entry_type.lower()
    if t == "article":
        return f"*{f.get('journal', '')}*"
    if t == "inproceedings":
        return f"*{f.get('booktitle', '')}*"
    if t == "incollection":
        parts = [p for p in (f.get("editor"), f.get("booktitle")) if p]
        pub = f" *{f['publisher']}*" if f.get("publisher") else ""
        return f"In: {', '.join(parts)}.{pub}"
    if t == "misc":
        return f"*{f.get('howpublished', f.get('note', ''))}*"
    return f"*{f.get('note', '')}*"


def format_entry(entry) -> str:
    f = {k: v.value for k, v in entry.fields_dict.items()}
    title = clean(f["title"])
    title_md = f"[**{title}**]({f['url']})" if f.get("url") else f"**{title}**"
    sep = "" if title[-1] in "?!." else "."
    text = f"{format_authors(f['author'])}, {f['year']}. {title_md}{sep} {venue(entry)}"
    if not text.endswith("."):
        text += "."
    if f.get("cv_note"):
        text += f" ({clean(f['cv_note'])})"
    return text


def section_of(entry) -> str:
    kw = entry.fields_dict.get("keywords")
    for k in (kw.value.split(",") if kw else []):
        k = k.strip()
        if k in dict(SECTIONS):
            return k
    return DEFAULT_SECTION_BY_TYPE.get(entry.entry_type.lower(), "working-paper")


def publication_sections() -> dict:
    text = BIB_FILE.read_text(encoding="utf-8")
    text = re.sub(r"\A---\s*\n---\s*\n", "", text)  # Jekyll front matter
    library = bibtexparser.parse_string(text)
    if library.failed_blocks:
        sys.exit(f"Could not parse {len(library.failed_blocks)} entries in {BIB_FILE}")
    by_section = {key: [] for key, _ in SECTIONS}
    for entry in library.entries:  # keep file order within each section
        by_section[section_of(entry)].append(entry)
    out, n = {}, 0
    for key, title in SECTIONS:
        items = []
        for entry in by_section[key]:
            n += 1
            items.append(f"{n}. {format_entry(entry)}")
        if items:
            out[title] = items
    return out


def main() -> None:
    cv = yaml.safe_load(CV_FILE.read_text(encoding="utf-8"))
    sections = cv["cv"]["sections"]
    merged = {}
    for name, entries in sections.items():
        merged[name] = entries
        if name == INSERT_AFTER:
            merged.update(publication_sections())
    cv["cv"]["sections"] = merged
    for part in ("design", "locale"):
        cfg = CONFIG_DIR / f"{part}.yaml"
        if cfg.exists():
            cv.update(yaml.safe_load(cfg.read_text(encoding="utf-8")))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # RenderCV looks next to the input file for fonts (./fonts) and for
        # template overrides (./<theme>/*.j2.typ), so copy those folders along.
        for folder in CONFIG_DIR.iterdir():
            if folder.is_dir():
                shutil.copytree(folder, tmp / folder.name)
        src = tmp / "cv.yaml"
        src.write_text(yaml.safe_dump(cv, allow_unicode=True, sort_keys=False, width=10_000), encoding="utf-8")
        cmd = ["rendercv", "render", str(src), "--pdf-path", str(tmp / "cv.pdf"),
               "--typst-path", str(tmp / "cv.typ"),
               "--dont-generate-markdown", "--dont-generate-html", "--dont-generate-png"]
        if "--keep-yaml" in sys.argv:  # for debugging: keep the merged input
            shutil.copyfile(src, ROOT / "cv_merged.yaml")
        subprocess.run(cmd, check=True, cwd=tmp)
        OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tmp / "cv.pdf", OUTPUT_PDF)
    print(f"Wrote {OUTPUT_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
