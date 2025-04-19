# Keyword checker

**Version:** 1.0  
**Author:** Linus Stoltz

A simple web scraper to identify key words for a given url. Allows various configuration parameters. Exports structured JSON for each scrape event.

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
| `-k, --keywords`   | One or more keywords/phrases to search for (multi‑word phrases in quotes). separate each entry with a space.|
| `-f, --keywords-file` | Path to a text file with one keyword or phrase per line (mutually exclusive with `-k` flag). |
| `-d, --depth`      | Maximum crawl depth (0 = only the start page). Defaults to 1.              |
| `-t, --timeout`    | HTTP request timeout in seconds. Defaults to 10.                           |
| `--json`           | Path to output JSON file. Defaults to `<timestamp>_matches.json`.          |
