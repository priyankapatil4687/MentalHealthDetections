"""Small helper layer over python-docx used by build_mini_report.py."""
import copy
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Times New Roman"


def _fonts(run, name=FONT):
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]


class Builder:
    def __init__(self, template):
        self.doc = Document(template)
        self.body = self.doc.element.body
        self._styles()

    # ------------------------------------------------------------ styles
    def _mk(self, name, size, bold, align, outline, before, after):
        st = self.doc.styles.add_style(name, 1)
        st.base_style = self.doc.styles["Normal"]
        st.font.name = FONT
        st.font.size = Pt(size)
        st.font.bold = bold
        st.font.color.rgb = RGBColor(0, 0, 0)
        rf = st.element.get_or_add_rPr().find(qn("w:rFonts"))
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), FONT)
        pf = st.paragraph_format
        pf.alignment = align
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.keep_with_next = True
        ppr = st.element.get_or_add_pPr()
        ol = OxmlElement("w:outlineLvl")
        ol.set(qn("w:val"), str(outline))
        ppr.append(ol)
        return st

    def _styles(self):
        self._mk("Chapter Title", 20, True, AL.CENTER, 0, 0, 14)
        self._mk("Section Head", 14, True, AL.LEFT, 1, 12, 6)
        self._mk("Subsection Head", 12, True, AL.LEFT, 2, 8, 4)

    # ------------------------------------------------------------ text
    def _runs(self, par, text, size=12, bold=False, italic=False, mono=False):
        parts = re.split(r"(\*\*.+?\*\*|__.+?__)", text)
        for part in parts:
            if not part:
                continue
            b, i = bold, italic
            if part.startswith("**") and part.endswith("**"):
                part, b = part[2:-2], True
            elif part.startswith("__") and part.endswith("__"):
                part, i = part[2:-2], True
            r = par.add_run(part)
            _fonts(r, "Consolas" if mono else FONT)
            r.font.size = Pt(size)
            r.bold = b
            r.italic = i
        return par

    def p(self, text, align=AL.JUSTIFY, size=12, bold=False, italic=False, first=True, after=6,
          line=1.5, keep=False, left=None):
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.alignment = align
        pf.space_after = Pt(after)
        pf.space_before = Pt(0)
        pf.line_spacing = line
        if first and align == AL.JUSTIFY:
            pf.first_line_indent = Inches(0.0)
        if left is not None:
            pf.left_indent = Inches(left)
        pf.keep_with_next = keep
        self._runs(par, text, size, bold, italic)
        return par

    def bl(self, items, size=12, numbered=False):
        for n, it in enumerate(items, 1):
            par = self.doc.add_paragraph()
            pf = par.paragraph_format
            pf.alignment = AL.JUSTIFY
            pf.left_indent = Inches(0.5)
            pf.first_line_indent = Inches(-0.25)
            pf.space_after = Pt(3)
            pf.line_spacing = 1.3
            self._runs(par, ("%d.\t" % n if numbered else "\u2022\t") + it, size)
            pf.tab_stops.add_tab_stop(Inches(0.5))

    def chapter(self, num, title):
        par = self.doc.add_paragraph(style="Chapter Title")
        par.paragraph_format.page_break_before = True
        self._runs(par, ("CHAPTER %s" % num) if num else "", 20, True)
        if num:
            par.add_run().add_break()
        self._runs(par, title.upper(), 20, True)
        return par

    def plain_title(self, title, page_break=True):
        par = self.doc.add_paragraph(style="Heading 1")
        par.alignment = AL.CENTER
        par.paragraph_format.page_break_before = page_break
        r = par.add_run(title)
        _fonts(r)
        r.font.size = Pt(20)
        r.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return par

    def h2(self, text):
        par = self.doc.add_paragraph(style="Section Head")
        self._runs(par, text, 14, True)

    def h3(self, text):
        par = self.doc.add_paragraph(style="Subsection Head")
        self._runs(par, text, 12, True)

    def pb(self):
        self.doc.add_page_break()

    def code(self, text, size=9):
        for ln in text.strip("\n").split("\n"):
            par = self.doc.add_paragraph()
            pf = par.paragraph_format
            pf.left_indent = Inches(0.3)
            pf.space_after = Pt(0)
            pf.line_spacing = 1.0
            sh = OxmlElement("w:shd")
            sh.set(qn("w:val"), "clear")
            sh.set(qn("w:color"), "auto")
            sh.set(qn("w:fill"), "F2F2F2")
            par._p.get_or_add_pPr().append(sh)
            self._runs(par, ln if ln else " ", size, mono=True)
        self.p("", after=2, line=1.0)

    def eq(self, text, num=None):
        par = self.doc.add_paragraph()
        par.paragraph_format.alignment = AL.CENTER
        par.paragraph_format.space_after = Pt(6)
        par.paragraph_format.line_spacing = 1.3
        self._runs(par, text + (("        (%s)" % num) if num else ""), 12, italic=True)

    # ------------------------------------------------------------ fields
    def field(self, par, instr, result="", size=12, bold=False):
        def mk(kind):
            r = par.add_run()
            _fonts(r)
            r.font.size = Pt(size)
            r.bold = bold
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r._r.append(fc)
            return r

        mk("begin")
        r = par.add_run()
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = " %s " % instr
        r._r.append(it)
        mk("separate")
        rr = par.add_run(result)
        _fonts(rr)
        rr.font.size = Pt(size)
        rr.bold = bold
        mk("end")

    def toc(self, instr):
        par = self.doc.add_paragraph()
        self.field(par, instr, "Right-click and choose Update Field to build this list.", 11)

    def caption(self, kind, text, above=False):
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.alignment = AL.CENTER
        pf.space_before = Pt(6 if above else 2)
        pf.space_after = Pt(4 if above else 10)
        pf.keep_with_next = above
        self._runs(par, kind + " ", 11, True)
        self.field(par, "SEQ %s \\* ARABIC" % kind, "0", 11, True)
        self._runs(par, ": " + text, 11, True)
        return par

    def fig(self, path, caption, width=6.2):
        par = self.doc.add_paragraph()
        par.paragraph_format.alignment = AL.CENTER
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_after = Pt(0)
        par.add_run().add_picture(str(path), width=Inches(width))
        self.caption("Figure", caption)

    def tbl(self, caption, header, rows, widths=None, fs=10, align=None):
        if caption:
            self.caption("Table", caption, above=True)
        t = self.doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        t.alignment = 1
        t.autofit = False

        def fill(cell, text, bold=False, a=AL.LEFT, shade=None):
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.alignment = a
            par.paragraph_format.space_after = Pt(1)
            par.paragraph_format.space_before = Pt(1)
            par.paragraph_format.line_spacing = 1.0
            self._runs(par, str(text), fs, bold)
            if shade:
                tcpr = cell._tc.get_or_add_tcPr()
                sh = OxmlElement("w:shd")
                sh.set(qn("w:val"), "clear")
                sh.set(qn("w:color"), "auto")
                sh.set(qn("w:fill"), shade)
                tcpr.append(sh)

        for i, h in enumerate(header):
            fill(t.rows[0].cells[i], h, True, AL.CENTER, "BFE0EA")
        trpr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trpr.append(th)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                a = AL.LEFT
                if align and align[i] == "c":
                    a = AL.CENTER
                elif align and align[i] == "r":
                    a = AL.RIGHT
                fill(cells[i], v, a=a)
        for row in t.rows:
            cant = OxmlElement("w:cantSplit")
            row._tr.get_or_add_trPr().append(cant)
            if widths:
                for i, w in enumerate(widths):
                    row.cells[i].width = Inches(w)
        self.p("", after=4, line=1.0)
        return t

    # ------------------------------------------------------------ utils
    def children(self):
        return list(self.body)


def set_par_text(par, text):
    """Replace paragraph text, keeping the formatting of the first run that has text."""
    runs = [r for r in par.runs]
    keep = next((r for r in runs if r.text.strip()), runs[0] if runs else None)
    if keep is None:
        par.add_run(text)
        return
    keep.text = text
    for r in runs:
        if r is not keep:
            r._r.getparent().remove(r._r)
