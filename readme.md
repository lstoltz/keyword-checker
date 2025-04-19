# Keyword checker

**Version:** 1.0  
**Author:** Linus Stoltz

A simple, polite web crawler that scans pages under a single domain for one or more keywords, prints matches to the console, and exports structured JSON output.

---

## Features

- **Domain‑restricted breadth‑first crawl** up to a configurable depth  
- **Keyword matching** (supports multi‑word phrases, whole‑word boundaries, and case‑insensitive)  
- **Spam‑protection** via fixed delay between requests  
- **Robust retries/backoff** on HTTP errors or rate‑limits (429, 5xx)  
- **Clean JSON export** of all pages with keyword occurrences, including URL, depth, HTML tag, and text snippet  

---

## Requirements

- Python 3.7+  
- [requests](https://pypi.org/project/requests/)  
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)  
- [lxml](https://pypi.org/project/lxml/)  

You can install all dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scrape_webpage.py https://example.com [OPTIONS]
```

| Options             | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `-k, --keywords`   | One or more keywords/phrases to search for (multi‑word phrases in quotes). |
| `-f, --keywords-file` | Path to a text file with one keyword or phrase per line (mutually exclusive with `-k`). |
| `-d, --depth`      | Maximum crawl depth (0 = only the start page). Defaults to 1.              |
| `-t, --timeout`    | HTTP request timeout in seconds. Defaults to 10.                           |
| `--json`           | Path to output JSON file. Defaults to `<timestamp>_matches.json`.          |
