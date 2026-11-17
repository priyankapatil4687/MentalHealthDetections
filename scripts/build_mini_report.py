"""Build the Mini Project-I report (.docx) from the D. Y. Patil template."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.text.paragraph import Paragraph

import report_content1 as c1
import report_content2 as c2
import report_content3 as c3
from docx_builder import Builder, set_par_text

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = r"c:\Users\itvai\OneDrive\Desktop\M.Tech. Mini Project - I Report Format 026-2027.docx"
OUT = ROOT / "report" / "MiniProject_I_Report.docx"
F = ROOT / "report" / "figures"
UI = F / "ui"
STUDENT = "<Student Name>"
PRN = "<PRN No.>"
GUIDE = "<Guide Name>"


def replace_in_runs(par, old, new):
    for r in par.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return True
    full = par.text
    if old in full:
        set_par_text(par, full.replace(old, new))
        return True
    return False


def main():
    b = Builder(TEMPLATE)
    doc = b.doc
    els = b.children()
    P = lambda i: Paragraph(els[i], doc)

    set_par_text(P(2), c1.TITLE)
    set_par_text(P(10), "%s (%s)" % (STUDENT, PRN))
    set_par_text(P(13), GUIDE)
    set_par_text(P(29), c1.TITLE)
    set_par_text(P(33), "%s (%s)" % (STUDENT, PRN))
    g = P(38).runs
    for k in (0, 1, 2, 3):
        g[k].text = ""
    g[4].text = GUIDE
    g[5].text = ""
    g[6].text = ""
    g[7].text = ""
    replace_in_runs(P(50), "<Guide Name>", GUIDE)
    set_par_text(P(57), STUDENT)

    for sec in doc.sections:
        for par in sec.header.paragraphs:
            if "Project Title" in par.text:
                set_par_text(par, c1.TITLE)

    index_head = els[68]
    cert_empty = [els[i] for i in (47, 45, 41, 36) if not Paragraph(els[i], doc).text.strip()]
    abs_empty = els[62:67]
    # abstract: insert before the Keywords paragraph, drop the empty ones
    kw = els[67]
    for e in abs_empty + cert_empty:
        e.getparent().remove(e)
    for txt in c1.abstract_paragraphs():
        par = b.p(txt, size=12, line=1.5)
        kw.addprevious(par._p)
    kwp = Paragraph(kw, doc)
    kwp.paragraph_format.space_before = __import__("docx").shared.Pt(6)
    run = kwp.add_run(c1.KEYWORDS)
    run.font.name = "Times New Roman"
    run.font.size = __import__("docx").shared.Pt(12)

    # remove template body after the INDEX heading (keep final sectPr)
    els = b.children()
    for e in els[els.index(index_head) + 1:-1]:
        e.getparent().remove(e)

    b.toc('TOC \\t "Chapter Title,1,Section Head,2,Subsection Head,3" \\h \\z')
    b.plain_title("LIST OF FIGURES")
    b.toc('TOC \\h \\z \\c "Figure"')
    b.plain_title("LIST OF TABLES")
    b.toc('TOC \\h \\z \\c "Table"')
    b.plain_title("LIST OF ABBREVIATIONS")
    b.tbl(None, ["Abbreviation", "Full form"], [list(x) for x in c1.ABBREVIATIONS], widths=[1.4, 5.1], fs=10.5)

    c1.chapter1(b)
    c1.chapter2(b)
    c1.chapter3(b)
    c2.chapter4(b, F)
    c2.chapter5(b, F)
    c3.chapter6(b, F, UI)
    c3.chapter7(b)
    c3.references(b)
    c3.appendices(b, F, UI)

    OUT.parent.mkdir(exist_ok=True)
    doc.save(str(OUT))
    print("saved", OUT)


if __name__ == "__main__":
    main()
