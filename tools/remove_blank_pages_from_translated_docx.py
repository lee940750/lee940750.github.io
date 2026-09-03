from __future__ import annotations

import shutil
import re
import zipfile
from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "tmp" / "translated_docx"
OUTPUT_DIR = ROOT / "tmp" / "translated_docx_word_layout"
FONT_NAME = "Times New Roman"

WD_STYLE_TYPE_PARAGRAPH = 1
WD_STYLE_TYPE_CHARACTER = 2
WD_GOTO_PAGE = 1
WD_GOTO_ABSOLUTE = 1
WD_ACTIVE_END_PAGE_NUMBER = 3
WD_ALIGN_PARAGRAPH_CENTER = 1
WD_ALIGN_PARAGRAPH_LEFT = 0
WD_ALIGN_TAB_RIGHT = 1
WD_ALIGN_TAB_LEFT = 0
WD_TAB_LEADER_DOTS = 1
WD_TAB_LEADER_SPACES = 0

BLANK_PAGE_CANDIDATES = {
    "drone-final-engineering-report-english.docx": [6, 8],
    "foldable-mechanism-final-report-english.docx": [5, 11, 43],
    "numerical-analysis-final-project-english.docx": [34],
}

FORCE_CONTENT_FONT_DOCS = {
    "air-conditioning-refrigeration-final-report-english.docx",
    "robot-dog-final-report-english.docx",
}


def is_blank_word_page(text: str) -> bool:
    return not text.replace("\r", "").replace("\x0c", "").replace("\x0b", "").strip()


def prepare_inputs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_DIR.glob("*.docx"):
        target = OUTPUT_DIR / source.name
        shutil.copy2(source, target)
        apply_times_new_roman_ooxml(target)


def apply_times_new_roman_ooxml(docx: Path) -> None:
    temp = docx.with_suffix(".tmp.docx")
    with zipfile.ZipFile(docx, "r") as zin, zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                try:
                    xml = data.decode("utf-8")
                    xml = patch_rfonts(xml)
                    data = xml.encode("utf-8")
                except UnicodeDecodeError:
                    pass
            zout.writestr(item, data)
    temp.replace(docx)


def patch_rfonts(xml: str) -> str:
    def patch_tag(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r'\s+w:(ascii|hAnsi|eastAsia|cs)(Theme)?="[^"]*"', "", tag)
        tag = re.sub(r'\s+w:hint="[^"]*"', "", tag)
        tag = tag[:-2] + (
            f' w:ascii="{FONT_NAME}"'
            f' w:hAnsi="{FONT_NAME}"'
            f' w:eastAsia="{FONT_NAME}"'
            f' w:cs="{FONT_NAME}"/>'
        )
        return tag

    xml = re.sub(r"<w:rFonts\b[^>]*/>", patch_tag, xml)
    if "<w:docDefaults>" in xml and "<w:rPrDefault>" in xml:
        if "<w:rPrDefault><w:rPr>" in xml and "<w:rFonts" not in xml.split("<w:rPrDefault><w:rPr>", 1)[1].split("</w:rPr>", 1)[0]:
            xml = xml.replace(
                "<w:rPrDefault><w:rPr>",
                (
                    "<w:rPrDefault><w:rPr>"
                    f'<w:rFonts w:ascii="{FONT_NAME}" w:hAnsi="{FONT_NAME}" '
                    f'w:eastAsia="{FONT_NAME}" w:cs="{FONT_NAME}"/>'
                ),
                1,
            )
    return xml


def usable_page_width(doc) -> float:
    return float(doc.PageSetup.PageWidth - doc.PageSetup.LeftMargin - doc.PageSetup.RightMargin)


def apply_times_new_roman(doc) -> None:
    for style in doc.Styles:
        try:
            if style.Type in (WD_STYLE_TYPE_PARAGRAPH, WD_STYLE_TYPE_CHARACTER):
                style.Font.Name = FONT_NAME
                style.Font.NameAscii = FONT_NAME
                style.Font.NameOther = FONT_NAME
                style.Font.NameFarEast = FONT_NAME
        except Exception:
            pass

    if Path(doc.FullName).name in FORCE_CONTENT_FONT_DOCS:
        font = doc.Content.Font
        font.Name = FONT_NAME
        font.NameAscii = FONT_NAME
        font.NameOther = FONT_NAME
        try:
            font.NameFarEast = FONT_NAME
        except Exception:
            pass


def format_toc_paragraphs(range_obj, width: float) -> None:
    paragraphs = range_obj.Paragraphs
    for idx in range(1, paragraphs.Count + 1):
        para = paragraphs(idx)
        try:
            para.Range.Font.Name = FONT_NAME
            para.Range.Font.NameAscii = FONT_NAME
            para.Range.Font.NameOther = FONT_NAME
            try:
                para.Range.Font.NameFarEast = FONT_NAME
            except Exception:
                pass
            para.Range.Font.Size = 8.5
            para.Format.LeftIndent = 0
            para.Format.RightIndent = 0
            para.Format.FirstLineIndent = 0
            para.Format.SpaceBefore = 0
            para.Format.SpaceAfter = 3
            para.TabStops.ClearAll()
            if para.Range.Text.count("\t") >= 2:
                para.TabStops.Add(Position=36, Alignment=WD_ALIGN_TAB_LEFT, Leader=WD_TAB_LEADER_SPACES)
            para.TabStops.Add(Position=width, Alignment=WD_ALIGN_TAB_RIGHT, Leader=WD_TAB_LEADER_DOTS)
        except Exception:
            pass


def refresh_automatic_tocs(doc) -> None:
    if doc.TablesOfContents.Count == 0:
        return

    width = usable_page_width(doc)
    for idx in range(1, doc.TablesOfContents.Count + 1):
        toc = doc.TablesOfContents(idx)
        try:
            toc.IncludePageNumbers = True
            toc.RightAlignPageNumbers = True
            toc.UseHyperlinks = True
            toc.TabLeader = WD_TAB_LEADER_DOTS
            toc.Update()
            toc.UpdatePageNumbers()
        except Exception:
            pass
        format_toc_paragraphs(toc.Range, width)


def page_number_for_text(doc, needle: str, start_page: int = 1) -> int | None:
    search_range = doc.Content.Duplicate
    if start_page > 1:
        search_range.Start = doc.GoTo(What=WD_GOTO_PAGE, Which=WD_GOTO_ABSOLUTE, Count=start_page).Start
    found = search_range.Find.Execute(FindText=needle, MatchCase=True, MatchWholeWord=True)
    if not found:
        return None
    return int(search_range.Information(WD_ACTIVE_END_PAGE_NUMBER))


def replace_foldable_manual_directory(doc) -> None:
    if "foldable-mechanism-final-report-english.docx" not in str(Path(doc.FullName).name):
        return

    entries = [
        ("Summary", "Summary", 2),
        ("Chapter 1. Device Introduction and Design Goals", "Chapter 1", 3),
        ("Chapter 2. Design Ideas and System Architecture", "Chapter 2", 3),
        ("Chapter 3. Detailed Design and Calculation", "Chapter 3", 3),
        ("Chapter 4. Experimental Verification and Discussion", "Chapter 4", 3),
        ("Chapter 5. Conclusion and Future Feedback", "Chapter 5", 3),
        ("References", "References", 3),
        ("Appendix", "Appendix", 3),
    ]
    lines = ["Directory"]
    for label, needle, start_page in entries:
        page = page_number_for_text(doc, needle, start_page=start_page)
        if page is None:
            continue
        lines.append(f"{label}\tP.{page}")

    page2_start = doc.GoTo(What=WD_GOTO_PAGE, Which=WD_GOTO_ABSOLUTE, Count=2).Start
    page3_start = doc.GoTo(What=WD_GOTO_PAGE, Which=WD_GOTO_ABSOLUTE, Count=3).Start
    page2 = doc.Range(page2_start, page3_start)
    directory = page2.Duplicate
    if not directory.Find.Execute(FindText="Directory", MatchCase=False, MatchWholeWord=False):
        return

    start = directory.Start
    replacement = doc.Range(start, page3_start)
    replacement.Delete()
    replacement.InsertAfter("\r".join(lines) + "\r")

    formatted = doc.Range(start, start + len("\r".join(lines) + "\r"))
    formatted.Font.Name = FONT_NAME
    formatted.Font.NameAscii = FONT_NAME
    formatted.Font.NameOther = FONT_NAME
    try:
        formatted.Font.NameFarEast = FONT_NAME
    except Exception:
        pass

    width = usable_page_width(doc)
    for idx in range(1, formatted.Paragraphs.Count + 1):
        para = formatted.Paragraphs(idx)
        try:
            para.Format.Alignment = WD_ALIGN_PARAGRAPH_LEFT
            para.Format.LeftIndent = 0
            para.Format.RightIndent = 0
            para.Format.FirstLineIndent = 0
            para.Format.SpaceBefore = 0
            para.Format.SpaceAfter = 6 if idx == 1 else 4
            para.TabStops.ClearAll()
            para.TabStops.Add(Position=width, Alignment=WD_ALIGN_TAB_RIGHT, Leader=WD_TAB_LEADER_DOTS)
            para.Range.Font.Size = 12
            para.Range.Font.Bold = False
        except Exception:
            pass

    title = formatted.Paragraphs(1).Range
    title.Font.Size = 18
    title.Font.Bold = False
    title.ParagraphFormat.Alignment = WD_ALIGN_PARAGRAPH_CENTER


def open_document(word, docx: Path, read_only: bool):
    return word.Documents.Open(
        str(docx.resolve()),
        ConfirmConversions=False,
        ReadOnly=read_only,
        AddToRecentFiles=False,
        Visible=False,
        OpenAndRepair=False,
        NoEncodingDialog=True,
    )


def run_word_pass(word, operation) -> None:
    for docx in sorted(OUTPUT_DIR.glob("*.docx")):
        print(f"Preparing {docx.name}", flush=True)
        doc = open_document(word, docx, read_only=False)
        try:
            operation(doc)
            doc.Repaginate()
            doc.Save()
        finally:
            doc.Close(False)


def remove_blank_pages() -> None:
    prepare_inputs()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        def initial_format(doc) -> None:
            apply_times_new_roman(doc)
            refresh_automatic_tocs(doc)

        run_word_pass(word, initial_format)

        for filename, pages in BLANK_PAGE_CANDIDATES.items():
            docx = (OUTPUT_DIR / filename).resolve()
            if not docx.exists():
                raise FileNotFoundError(docx)

            print(f"Checking blank pages in {filename}", flush=True)
            for reopen_pass in range(2):
                doc = open_document(word, docx, read_only=False)
                try:
                    for _ in range(3):
                        doc.Repaginate()
                        removed_in_pass = False
                        for page_num in sorted(pages, reverse=True):
                            total_pages = doc.ComputeStatistics(2)
                            if page_num > total_pages:
                                continue
                            start = doc.GoTo(What=1, Which=1, Count=page_num).Start
                            end = (
                                doc.GoTo(What=1, Which=1, Count=page_num + 1).Start
                                if page_num < total_pages
                                else doc.Content.End
                            )
                            page_range = doc.Range(start, end)
                            if not is_blank_word_page(page_range.Text):
                                print(f"  pass {reopen_pass + 1}: skipped page {page_num}: not blank", flush=True)
                                continue
                            page_range.Delete()
                            doc.Repaginate()
                            removed_in_pass = True
                            print(f"  pass {reopen_pass + 1}: removed blank page {page_num}", flush=True)
                        if not removed_in_pass:
                            break
                    doc.Save()
                finally:
                    doc.Close(False)

        def final_format(doc) -> None:
            apply_times_new_roman(doc)
            refresh_automatic_tocs(doc)
            replace_foldable_manual_directory(doc)
            refresh_automatic_tocs(doc)

        run_word_pass(word, final_format)

        for docx in sorted(OUTPUT_DIR.glob("*.docx")):
            print(f"Final font patch {docx.name}", flush=True)
            apply_times_new_roman_ooxml(docx)
    finally:
        word.Quit()


if __name__ == "__main__":
    remove_blank_pages()
