"""
Build Word versions of the manuscript and, if present, the cover letter.

From the repository root:
    pip install -r requirements-manuscript.txt
    python projects/p1-bfs-establishment-births/manuscript/build_docx.py

Reads manuscript/draft_v1.md and writes manuscript/submission/draft_v1.docx
(the submission folder is git-ignored). The Markdown file is the master
copy: edit it, then rebuild, rather than editing the Word file. HTML
comments are dropped, each <!-- pagebreak --> marker becomes a page break,
and figures are embedded from manuscript/figures/. If
manuscript/submission/cover_letter.md exists, it is converted as well.
"""

import re
from pathlib import Path

import pypandoc

MANUSCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = MANUSCRIPT_DIR / "submission"
PAGE_BREAK = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'


def convert(src: Path, out: Path) -> None:
    text = src.read_text(encoding="utf-8")
    text = text.replace("<!-- pagebreak -->", PAGE_BREAK)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # implicit_figures is off: each figure already has its own caption paragraph.
    pypandoc.convert_text(
        text, to="docx", format="markdown-implicit_figures", outputfile=str(out),
        extra_args=[f"--resource-path={MANUSCRIPT_DIR}"],
    )
    print(f"wrote {out}")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    convert(MANUSCRIPT_DIR / "draft_v1.md", OUT_DIR / "draft_v1.docx")
    letter = OUT_DIR / "cover_letter.md"
    if letter.exists():
        convert(letter, OUT_DIR / "cover_letter.docx")


if __name__ == "__main__":
    main()
