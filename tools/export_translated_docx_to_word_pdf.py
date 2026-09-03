from __future__ import annotations

from pathlib import Path

import win32com.client


ROOT = Path(__file__).resolve().parents[1]
TMP_DOCX = ROOT / "tmp" / "translated_docx"
LAYOUT_DOCX = ROOT / "tmp" / "translated_docx_word_layout"
DOCS = ROOT / "assets" / "documents"


ITEMS = [
    {
        "docx": LAYOUT_DOCX / "drone-final-engineering-report-english.docx",
        "pdf": DOCS / "drone-final-engineering-report-english.pdf",
    },
    {
        "docx": LAYOUT_DOCX / "robot-dog-final-report-english.docx",
        "pdf": DOCS / "robot-dog-final-report-english.pdf",
    },
    {
        "docx": LAYOUT_DOCX / "foldable-mechanism-final-report-english.docx",
        "pdf": DOCS / "foldable-mechanism-final-report-english.pdf",
    },
    {
        "docx": LAYOUT_DOCX / "numerical-analysis-final-project-english.docx",
        "pdf": DOCS / "numerical-analysis-final-project-english.pdf",
    },
    {
        "docx": LAYOUT_DOCX / "numerical-analysis-midterm-project-english.docx",
        "pdf": DOCS / "numerical-analysis-midterm-project-english.pdf",
    },
    {
        "docx": LAYOUT_DOCX / "air-conditioning-refrigeration-final-report-english.docx",
        "pdf": DOCS / "air-conditioning-refrigeration-final-report-english.pdf",
    },
]


def export_all() -> None:
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        try:
            word.AutomationSecurity = 3
        except Exception:
            pass

        for item in ITEMS:
            docx = item["docx"].resolve()
            pdf = item["pdf"].resolve()
            if not docx.exists():
                raise FileNotFoundError(docx)

            pdf.parent.mkdir(parents=True, exist_ok=True)
            if pdf.exists():
                pdf.unlink()

            print(f"Opening {docx.name}")
            doc = word.Documents.Open(
                str(docx),
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False,
                Visible=False,
                OpenAndRepair=False,
                NoEncodingDialog=True,
            )
            try:
                pages = doc.ComputeStatistics(2)
                print(f"Exporting {pdf.name} ({pages} Word pages)")
                doc.ExportAsFixedFormat(
                    OutputFileName=str(pdf),
                    ExportFormat=17,
                    OpenAfterExport=False,
                    OptimizeFor=0,
                    Range=0,
                    Item=0,
                    IncludeDocProps=True,
                    KeepIRM=False,
                    CreateBookmarks=1,
                    DocStructureTags=True,
                    BitmapMissingFonts=True,
                    UseISO19005_1=False,
                )
                print(f"Wrote {pdf.name} ({pdf.stat().st_size:,} bytes)")
            finally:
                doc.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    export_all()
