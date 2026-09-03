from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from pathlib import Path

import mammoth


ROOT = Path(__file__).resolve().parents[1]
TMP_HTML = ROOT / "tmp" / "translated_html"
TMP_VECTOR = ROOT / "tmp" / "converted_vector_images"
DOCS = ROOT / "assets" / "documents"
CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

ITEMS = [
    {
        "key": "drone-final",
        "title": "Drone Final Engineering Report",
        "docx": ROOT / "tmp" / "translated_docx" / "drone-final-engineering-report-english.docx",
        "pdf": DOCS / "drone-final-engineering-report-english.pdf",
    },
    {
        "key": "robot-dog-final",
        "title": "Robot Dog Final Report",
        "docx": ROOT / "tmp" / "translated_docx" / "robot-dog-final-report-english.docx",
        "pdf": DOCS / "robot-dog-final-report-english.pdf",
    },
    {
        "key": "foldable-final",
        "title": "Foldable Mechanism Final Report",
        "docx": ROOT / "tmp" / "translated_docx" / "foldable-mechanism-final-report-english.docx",
        "pdf": DOCS / "foldable-mechanism-final-report-english.pdf",
    },
    {
        "key": "numerical-final",
        "title": "Numerical Analysis Final Project",
        "docx": ROOT / "tmp" / "translated_docx" / "numerical-analysis-final-project-english.docx",
        "pdf": DOCS / "numerical-analysis-final-project-english.pdf",
    },
    {
        "key": "numerical-midterm",
        "title": "Numerical Analysis Midterm Project",
        "docx": ROOT / "tmp" / "translated_docx" / "numerical-analysis-midterm-project-english.docx",
        "pdf": DOCS / "numerical-analysis-midterm-project-english.pdf",
    },
    {
        "key": "refrigeration-final",
        "title": "Air-Conditioning and Refrigeration Final Report",
        "docx": ROOT / "tmp" / "translated_docx" / "air-conditioning-refrigeration-final-report-english.docx",
        "pdf": DOCS / "air-conditioning-refrigeration-final-report-english.pdf",
    },
]


CSS = """
@page {
  size: Letter;
  margin: 0.62in 0.65in;
}

* {
  box-sizing: border-box;
}

html {
  color: #111827;
  font-family: Arial, "Noto Sans", "Microsoft JhengHei", sans-serif;
  font-size: 10.5pt;
  line-height: 1.38;
}

body {
  margin: 0;
  background: #fff;
}

.doc-shell {
  max-width: 7.2in;
  margin: 0 auto;
}

.translation-note {
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #475569;
  font-size: 9pt;
  line-height: 1.35;
  padding: 8pt 10pt;
  margin: 0 0 14pt;
}

h1, h2, h3, h4 {
  color: #073b4c;
  line-height: 1.18;
  page-break-after: avoid;
  break-after: avoid;
}

h1 {
  font-size: 20pt;
  margin: 0 0 12pt;
}

h2 {
  font-size: 15pt;
  margin: 18pt 0 8pt;
}

h3 {
  font-size: 12.5pt;
  margin: 14pt 0 6pt;
}

h4 {
  font-size: 11pt;
  margin: 10pt 0 5pt;
}

p {
  margin: 0 0 7pt;
}

ul, ol {
  margin-top: 0;
  margin-bottom: 8pt;
  padding-left: 20pt;
}

li {
  margin-bottom: 3pt;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 10pt 0 12pt;
  page-break-inside: auto;
  break-inside: auto;
}

tr {
  page-break-inside: avoid;
  break-inside: avoid;
}

td, th {
  border: 0.75pt solid #cbd5e1;
  padding: 5pt 6pt;
  vertical-align: top;
}

th {
  background: #0f766e;
  color: #fff;
  font-weight: 700;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 8pt auto 10pt;
  page-break-inside: avoid;
  break-inside: avoid;
}

figure {
  margin: 10pt 0;
  page-break-inside: avoid;
  break-inside: avoid;
}

pre {
  white-space: pre-wrap;
  font-family: Consolas, monospace;
  font-size: 8.5pt;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 8pt;
}

a {
  color: #0f766e;
}

.page-break {
  break-after: page;
}
"""


def find_browser() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Chrome or Edge executable not found")


def convert_image(image):
    with image.open() as image_bytes:
        raw = image_bytes.read()
    if image.content_type in {"image/x-wmf", "image/x-emf"}:
        ext = ".wmf" if image.content_type == "image/x-wmf" else ".emf"
        digest = hashlib.sha256(raw).hexdigest()
        TMP_VECTOR.mkdir(parents=True, exist_ok=True)
        vector_path = TMP_VECTOR / f"{digest}{ext}"
        png_path = TMP_VECTOR / f"{digest}.png"
        if not png_path.exists():
            vector_path.write_bytes(raw)
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "tools" / "convert_vector_image_to_png.ps1"),
                    "-InputPath",
                    str(vector_path),
                    "-OutputPath",
                    str(png_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
            if completed.returncode != 0 or not png_path.exists():
                svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="120" viewBox="0 0 720 120">
  <rect x="1" y="1" width="718" height="118" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <text x="360" y="52" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#334155">Original Word equation/object retained in source DOCX</text>
  <text x="360" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#64748b">Unsupported browser image type: {image.content_type}</text>
</svg>"""
                encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
                return {
                    "src": f"data:image/svg+xml;base64,{encoded}",
                    "alt": "Original Word equation or object retained in the source DOCX",
                }
        encoded = base64.b64encode(png_path.read_bytes()).decode("ascii")
        return {
            "src": f"data:image/png;base64,{encoded}",
            "alt": "Converted Word vector image",
        }
    encoded = base64.b64encode(raw).decode("ascii")
    return {
        "src": f"data:{image.content_type};base64,{encoded}",
    }


def wrap_html(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{title}</title>
    <style>{CSS}</style>
  </head>
  <body>
    <main class="doc-shell">
      <div class="translation-note">
        English translation generated from the original Word source file. Editable text was translated
        directly from the source DOCX; embedded images/screenshots retain their original visual content.
      </div>
      {body}
    </main>
  </body>
</html>
"""


def export_item(item: dict, browser: Path) -> dict:
    docx = item["docx"]
    pdf = item["pdf"]
    if not docx.exists():
        raise FileNotFoundError(docx)

    TMP_HTML.mkdir(parents=True, exist_ok=True)
    with docx.open("rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(convert_image))

    html = wrap_html(item["title"], result.value)
    html_path = TMP_HTML / f"{item['key']}.html"
    html_path.write_text(html, encoding="utf-8")

    pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}",
        html_path.resolve().as_uri(),
    ]
    completed = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    return {
        "key": item["key"],
        "docx": str(docx.relative_to(ROOT)),
        "html": str(html_path.relative_to(ROOT)),
        "pdf": str(pdf.relative_to(ROOT)),
        "warnings": [str(message) for message in result.messages],
        "pdf_bytes": pdf.stat().st_size,
    }


def main() -> None:
    browser = find_browser()
    print(f"Using browser: {browser}")
    log = []
    for item in ITEMS:
        print(f"Exporting {item['key']}...")
        entry = export_item(item, browser)
        log.append(entry)
        print(f"  wrote {entry['pdf']} ({entry['pdf_bytes']} bytes), warnings={len(entry['warnings'])}")
    (ROOT / "tmp" / "browser_pdf_export_report.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
