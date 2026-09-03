from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "tmp" / "translated_docx"
OUTPUT_DIR = ROOT / "tmp" / "translated_docx_word_layout"

BLANK_PAGE_CANDIDATES = {
    "drone-final-engineering-report-english.docx": [8],
    "foldable-mechanism-final-report-english.docx": [5, 11, 43],
}


def is_blank_word_page(text: str) -> bool:
    return not text.replace("\r", "").replace("\x0c", "").replace("\x0b", "").strip()


def prepare_inputs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_DIR.glob("*.docx"):
        target = OUTPUT_DIR / source.name
        shutil.copy2(source, target)


def remove_blank_pages() -> None:
    prepare_inputs()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        for filename, pages in BLANK_PAGE_CANDIDATES.items():
            docx = (OUTPUT_DIR / filename).resolve()
            if not docx.exists():
                raise FileNotFoundError(docx)

            print(f"Checking blank pages in {filename}")
            for reopen_pass in range(2):
                doc = word.Documents.Open(
                    str(docx),
                    ConfirmConversions=False,
                    ReadOnly=False,
                    AddToRecentFiles=False,
                    Visible=False,
                    OpenAndRepair=False,
                    NoEncodingDialog=True,
                )
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
                                print(f"  pass {reopen_pass + 1}: skipped page {page_num}: not blank")
                                continue
                            page_range.Delete()
                            doc.Repaginate()
                            removed_in_pass = True
                            print(f"  pass {reopen_pass + 1}: removed blank page {page_num}")
                        if not removed_in_pass:
                            break
                    doc.Save()
                finally:
                    doc.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    remove_blank_pages()
