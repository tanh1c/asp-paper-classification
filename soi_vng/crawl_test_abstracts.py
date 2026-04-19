import argparse
import json
import re
import time
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT_DIR / "dataset_stage1" / "test (2).csv"
DEFAULT_OUTPUT = ROOT_DIR / "dataset_stage1" / "test_with_abstract.csv"
DEFAULT_CACHE = Path(__file__).resolve().parent / "doi_abstract_cache.json"
UNKNOWN_ABSTRACT = ""


class AbstractPageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = []
        self.json_ld = []
        self.abstract_blocks = []
        self._script_type = ""
        self._script_chunks = []
        self._capture_depth = 0
        self._capture_chunks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()

        if tag == "meta":
            self.meta.append({str(k).lower(): v for k, v in attrs.items()})
            return

        if tag == "script":
            self._script_type = str(attrs.get("type", "")).lower()
            if "ld+json" in self._script_type:
                self._script_chunks = []
            return

        marker = " ".join(
            str(attrs.get(key, "")) for key in ("id", "class", "name", "property")
        ).lower()
        if "abstract" in marker:
            self._capture_depth += 1
            self._capture_chunks.append(" ")
        elif self._capture_depth:
            self._capture_depth += 1

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == "script":
            if "ld+json" in self._script_type and self._script_chunks:
                self.json_ld.append("".join(self._script_chunks))
            self._script_type = ""
            self._script_chunks = []
            return

        if self._capture_depth:
            self._capture_depth -= 1
            if self._capture_depth == 0:
                text = normalize_text(" ".join(self._capture_chunks))
                if text:
                    self.abstract_blocks.append(text)
                self._capture_chunks = []

    def handle_data(self, data):
        if "ld+json" in self._script_type:
            self._script_chunks.append(data)
        if self._capture_depth:
            self._capture_chunks.append(data)


def normalize_text(value):
    if value is None:
        return ""
    text = unescape(str(value))
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(abstract|summary)\s*[:.\-]?\s*", "", text, flags=re.I)
    return text.strip()


def looks_like_abstract(value):
    text = normalize_text(value)
    if len(text) < 80:
        return False
    lowered = text.lower()
    if lowered.startswith(("http://", "https://")):
        return False
    if "cookie" in lowered and "privacy" in lowered:
        return False
    return True


def iter_json_values(value):
    if isinstance(value, dict):
        for key in ("abstract", "description"):
            if key in value:
                yield value[key]
        for nested in value.values():
            yield from iter_json_values(nested)
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_values(item)


def extract_from_json_ld(json_ld_blocks):
    for block in json_ld_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for value in iter_json_values(data):
            if isinstance(value, list):
                value = " ".join(str(part) for part in value)
            text = normalize_text(value)
            if looks_like_abstract(text):
                return text
    return ""


def extract_from_meta(meta_tags):
    preferred_names = (
        "citation_abstract",
        "dc.description",
        "dcterms.abstract",
        "description",
        "og:description",
        "twitter:description",
    )

    candidates = []
    for meta in meta_tags:
        key = (
            meta.get("name")
            or meta.get("property")
            or meta.get("itemprop")
            or meta.get("http-equiv")
            or ""
        ).lower()
        content = meta.get("content", "")
        if key in preferred_names:
            candidates.append((preferred_names.index(key), content))

    for _, content in sorted(candidates, key=lambda item: item[0]):
        text = normalize_text(content)
        if looks_like_abstract(text):
            return text
    return ""


def extract_from_abstract_blocks(blocks):
    for block in blocks:
        text = normalize_text(block)
        if looks_like_abstract(text):
            return text
    return ""


def extract_abstract(html):
    parser = AbstractPageParser()
    parser.feed(html)

    for source, extractor in (
        ("meta", lambda: extract_from_meta(parser.meta)),
        ("json_ld", lambda: extract_from_json_ld(parser.json_ld)),
        ("html_block", lambda: extract_from_abstract_blocks(parser.abstract_blocks)),
    ):
        abstract = extractor()
        if abstract:
            return abstract, source

    return UNKNOWN_ABSTRACT, "not_found"


def doi_to_url(doi):
    doi = str(doi).strip()
    if doi.lower().startswith("http://") or doi.lower().startswith("https://"):
        return doi
    return f"https://doi.org/{quote(doi, safe='/')}"


def fetch_html(url, timeout):
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        html = raw.decode(charset, errors="replace")
        return html, response.geturl()


def load_cache(path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(path, cache):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)


def crawl_doi(doi, timeout):
    if pd.isna(doi) or not str(doi).strip():
        return {
            "abstract": UNKNOWN_ABSTRACT,
            "abstract_source": "missing_doi",
            "resolved_url": "",
            "error": "",
        }

    url = doi_to_url(doi)
    try:
        html, resolved_url = fetch_html(url, timeout=timeout)
        abstract, source = extract_abstract(html)
        return {
            "abstract": abstract,
            "abstract_source": source,
            "resolved_url": resolved_url,
            "error": "",
        }
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "abstract": UNKNOWN_ABSTRACT,
            "abstract_source": "error",
            "resolved_url": url,
            "error": f"{type(exc).__name__}: {exc}",
        }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch abstracts for DOI rows in dataset_stage1/test (2).csv."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.input)
    if "doi" not in df.columns:
        raise ValueError(f"Input CSV has no 'doi' column: {args.input}")

    cache = load_cache(args.cache)
    rows_to_process = df.head(args.limit) if args.limit is not None else df
    results = []

    for index, row in rows_to_process.iterrows():
        doi = str(row["doi"]).strip()
        if doi in cache and not args.force:
            result = cache[doi]
            status = "cached"
        else:
            result = crawl_doi(doi, timeout=args.timeout)
            cache[doi] = result
            save_cache(args.cache, cache)
            status = result["abstract_source"]
            time.sleep(args.sleep)

        results.append(result)
        print(
            f"[{index + 1}/{len(rows_to_process)}] {status} | "
            f"{doi} | {result['abstract'][:90]}"
        )

    output_df = rows_to_process.reset_index(drop=True).copy()
    output_df["abstract"] = [result["abstract"] for result in results]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(args.output, index=False)
    save_cache(args.cache, cache)

    found = output_df["abstract"].fillna("").astype(str).str.strip().ne("").sum()
    print(f"\nSaved: {args.output}")
    print(f"Rows: {len(output_df)} | abstracts found: {found}")
    print(f"Cache: {args.cache}")


if __name__ == "__main__":
    main()
