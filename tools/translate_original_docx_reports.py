from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, unescape


ROOT = Path(__file__).resolve().parents[1]
TMP_DOCX = ROOT / "tmp" / "translated_docx"
DOCS = ROOT / "assets" / "documents"
CACHE_PATH = ROOT / "tmp" / "translation_cache_zh_tw_en.json"
REPORT_LOG = ROOT / "tmp" / "translation_report.json"

PARA_RE = re.compile(r"<w:p\b[\s\S]*?</w:p>")
TEXT_RE = re.compile(r"(<w:t\b[^>]*>)([\s\S]*?)(</w:t>)")
XML_UNESCAPE_MAP = {"&quot;": '"', "&apos;": "'"}

RESIDUAL_REPLACEMENTS = {
    "第1章、": "Chapter 1. ",
    "第2章、": "Chapter 2. ",
    "第3章、": "Chapter 3. ",
    "第4章、": "Chapter 4. ",
    "第5章、": "Chapter 5. ",
    "第%1章、": "Chapter %1. ",
    "%2、": "%2.",
    "%5、": "%5.",
    "%8、": "%8.",
    "飛行晃動": "flight oscillation",
    "面寬，傘齒輪若較窄取": "face width; use",
    "做保守計算": "for conservative calculation",
    "積分": "integration",
    "左端高度": "left-end height",
    "右端高度": "right-end height",
    "數值位移": "numerical displacement",
    "節點位移": "nodal displacement",
    "取": "use",
}


REPORTS = [
    {
        "source": ROOT / "檔案" / "無人機" / "機械工程實務期末報告_第五組new.docx",
        "docx": TMP_DOCX / "drone-final-engineering-report-english.docx",
        "pdf": DOCS / "drone-final-engineering-report-english.pdf",
        "label": "Drone final report",
    },
    {
        "source": ROOT / "檔案" / "機器狗" / "微處理期末專題.docx",
        "docx": TMP_DOCX / "robot-dog-final-report-english.docx",
        "pdf": DOCS / "robot-dog-final-report-english.pdf",
        "label": "Robot dog final report",
    },
    {
        "source": ROOT / "檔案" / "遠距離運球機構" / "機械設計原理期末Project 第九組.docx",
        "docx": TMP_DOCX / "foldable-mechanism-final-report-english.docx",
        "pdf": DOCS / "foldable-mechanism-final-report-english.pdf",
        "label": "Foldable mechanism final report",
    },
    {
        "source": ROOT / "檔案" / "數值分析" / "Numerical Analysis Final Project B12502027 李承軒.docx",
        "docx": TMP_DOCX / "numerical-analysis-final-project-english.docx",
        "pdf": DOCS / "numerical-analysis-final-project-english.pdf",
        "label": "Numerical analysis final project",
    },
    {
        "source": ROOT / "檔案" / "數值分析" / "Numerical Analysis Midterm Project B12502027 李承軒.docx",
        "docx": TMP_DOCX / "numerical-analysis-midterm-project-english.docx",
        "pdf": DOCS / "numerical-analysis-midterm-project-english.pdf",
        "label": "Numerical analysis midterm project",
    },
    {
        "source": ROOT / "檔案" / "冷凍空調" / "冷凍空調期末報告new.docx",
        "docx": TMP_DOCX / "air-conditioning-refrigeration-final-report-english.docx",
        "pdf": DOCS / "air-conditioning-refrigeration-final-report-english.pdf",
        "label": "Air-conditioning and refrigeration final report",
    },
]


def has_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def normalize_translation(text: str) -> str:
    replacements = {
        "Li Chengxuan": "CHENG-HSUAN LEE",
        "Lee Chengxuan": "CHENG-HSUAN LEE",
        "Lee Cheng-Hsuan": "CHENG-HSUAN LEE",
        "Cheng-Hsuan Lee": "CHENG-HSUAN LEE",
        "Chengxuan Li": "CHENG-HSUAN LEE",
        "Cheng Xuan Lee": "CHENG-HSUAN LEE",
        "Cheng Hsuan Lee": "CHENG-HSUAN LEE",
        "B12502027 CHENG-HSUAN LEE": "B12502027 CHENG-HSUAN LEE",
        "National Taiwan University": "National Taiwan University",
    }
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = cleaned.replace("\u2013", "-").replace("\u2014", "-")
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def google_translate(text: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": "zh-TW",
            "tl": "en",
            "dt": "t",
            "q": text,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            translated = "".join(part[0] for part in data[0] if part and part[0])
            return normalize_translation(translated)
        except Exception as exc:  # pragma: no cover - network failures are environment-specific.
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"translation failed: {last_error}")


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def translate_texts(texts: list[str], cache: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    unique = []
    seen = set()
    for text in texts:
        if text not in cache and text not in seen:
            unique.append(text)
            seen.add(text)

    failures: list[str] = []
    i = 0
    while i < len(unique):
        batch = []
        batch_len = 0
        while i < len(unique) and batch_len + len(unique[i]) < 3200 and len(batch) < 18:
            batch.append(unique[i])
            batch_len += len(unique[i]) + 24
            i += 1
        if not batch:
            batch.append(unique[i])
            i += 1

        marker_base = int(time.time() * 1000) % 1000000
        markers = [f"ZZZCHLSEP{marker_base + j:06d}ZZZ" for j in range(max(0, len(batch) - 1))]
        joined_parts = []
        for idx, text in enumerate(batch):
            joined_parts.append(text)
            if idx < len(markers):
                joined_parts.append(markers[idx])
        joined = "\n".join(joined_parts)

        try:
            translated_joined = google_translate(joined)
            pattern = r"\s*ZZZCHLSEP\d{6}ZZZ\s*"
            translated_parts = re.split(pattern, translated_joined)
            if len(translated_parts) != len(batch):
                raise ValueError(f"batch split mismatch: expected {len(batch)}, got {len(translated_parts)}")
            for original, translated in zip(batch, translated_parts):
                cache[original] = normalize_translation(translated) or original
        except Exception:
            for original in batch:
                try:
                    cache[original] = google_translate(original) or original
                except Exception:
                    cache[original] = original
                    failures.append(original)
        if len(cache) % 100 < len(batch):
            save_cache(cache)
        time.sleep(0.08)

    save_cache(cache)
    return cache, failures


def collect_paragraph_texts(xml_bytes: bytes) -> list[str]:
    xml = xml_bytes.decode("utf-8")
    texts = []
    for para_match in PARA_RE.finditer(xml):
        nodes = list(TEXT_RE.finditer(para_match.group(0)))
        if not nodes:
            continue
        text = "".join(unescape(node.group(2), XML_UNESCAPE_MAP) for node in nodes).strip()
        if text and has_chinese(text):
            texts.append(text)
    return texts


def replace_paragraph_texts(xml_bytes: bytes, translations: dict[str, str]) -> tuple[bytes, int, int]:
    xml = xml_bytes.decode("utf-8")
    translated_count = 0
    remaining_chinese = 0

    def replace_para(para_match: re.Match) -> str:
        nonlocal translated_count, remaining_chinese
        para_xml = para_match.group(0)
        nodes = list(TEXT_RE.finditer(para_xml))
        if not nodes:
            return para_xml
        original = "".join(unescape(node.group(2), XML_UNESCAPE_MAP) for node in nodes).strip()
        if not original or not has_chinese(original):
            return para_xml
        translated = translations.get(original, original)
        if translated != original:
            translated_count += 1
        if has_chinese(translated):
            remaining_chinese += 1

        index = 0

        def replace_text_node(text_match: re.Match) -> str:
            nonlocal index
            content = escape(translated) if index == 0 else ""
            index += 1
            return f"{text_match.group(1)}{content}{text_match.group(3)}"

        return TEXT_RE.sub(replace_text_node, para_xml)

    updated = PARA_RE.sub(replace_para, xml)
    return updated.encode("utf-8"), translated_count, remaining_chinese


def apply_residual_replacements(xml_bytes: bytes) -> bytes:
    xml = xml_bytes.decode("utf-8")
    for source, target in RESIDUAL_REPLACEMENTS.items():
        xml = xml.replace(escape(source), escape(target))
    return xml.encode("utf-8")


def text_parts(zip_file: zipfile.ZipFile) -> list[str]:
    names = []
    for name in zip_file.namelist():
        if not name.startswith("word/") or not name.endswith(".xml"):
            continue
        stem = Path(name).name
        if (
            stem == "document.xml"
            or stem.startswith("header")
            or stem.startswith("footer")
            or stem in {"footnotes.xml", "endnotes.xml", "comments.xml"}
        ):
            names.append(name)
    return names


def translate_docx(source: Path, output: Path, cache: dict[str, str]) -> dict:
    with zipfile.ZipFile(source, "r") as zin:
        parts = text_parts(zin)
        candidates = []
        for part in parts:
            candidates.extend(collect_paragraph_texts(zin.read(part)))

    cache, failures = translate_texts(candidates, cache)

    output.parent.mkdir(parents=True, exist_ok=True)
    translated_paragraphs = 0
    remaining_chinese_paragraphs = 0
    with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            is_word_xml = item.filename.startswith("word/") and item.filename.endswith(".xml")
            if item.filename in parts:
                try:
                    data, translated, remaining = replace_paragraph_texts(data, cache)
                    translated_paragraphs += translated
                    remaining_chinese_paragraphs += remaining
                except Exception:
                    pass
            if is_word_xml:
                data = apply_residual_replacements(data)
            zout.writestr(item, data)

    return {
        "source": str(source.relative_to(ROOT)),
        "output_docx": str(output.relative_to(ROOT)),
        "translated_paragraphs": translated_paragraphs,
        "remaining_chinese_paragraphs": remaining_chinese_paragraphs,
        "failed_segments": failures[:20],
        "failed_segment_count": len(failures),
    }


def main() -> None:
    missing = [str(report["source"].relative_to(ROOT)) for report in REPORTS if not report["source"].exists()]
    if missing:
        raise FileNotFoundError("Missing source DOCX files: " + ", ".join(missing))

    cache = load_cache()
    log = []
    for report in REPORTS:
        print(f"Translating {report['label']}...")
        entry = translate_docx(report["source"], report["docx"], cache)
        entry["label"] = report["label"]
        entry["target_pdf"] = str(report["pdf"].relative_to(ROOT))
        log.append(entry)
        print(
            f"  paragraphs translated={entry['translated_paragraphs']} "
            f"remaining_zh={entry['remaining_chinese_paragraphs']} "
            f"failures={entry['failed_segment_count']}"
        )

    REPORT_LOG.parent.mkdir(parents=True, exist_ok=True)
    REPORT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {REPORT_LOG.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
