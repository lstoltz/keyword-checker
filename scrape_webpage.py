__author__ = "Linus Stoltz"
__version__ = "1.0"

import argparse
import json
import re
import sys
import time
from collections import deque
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup, Comment
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


REQUEST_DELAY  = 1.0    # seconds between requests for spammin' protection
MAX_RETRIES    = 3
BACKOFF_FACTOR = 0.5
USER_AGENT     = f"NightlyCrawler/{__version__}" # keep the sites happy
# (and avoid being blocked for scraping too fast)


def make_session():
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def fetch_html(session, url, timeout):
    """Download the HTML content of the given URL, with retries/backoff."""
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def make_pattern(kw: str) -> re.Pattern:
    """
    Turn a keyword (possibly multi‑word) into a regex that:
      - matches whole‑word boundaries at start/end
      - allows any whitespace sequence between words
      - is case‑insensitive
    """
    parts = kw.split()  # splits on any whitespace
    inner = r'\s+'.join(map(re.escape, parts))
    return re.compile(rf'\b{inner}\b', re.IGNORECASE)


def is_snippet_valid(snippet: str) -> bool:
    """
    Return False if snippet contains non‑printable or replacement chars,
    to filter out gibberish.
    """
    if not snippet.isprintable():
        return False
    if '\ufffd' in snippet:
        return False
    return True


def locate_keywords(soup, keywords):
    """
    Return a list of occurrences of each keyword in the soup.
    Each occurrence is a dict: {keyword, tag, snippet}.
    Filters out snippets with non‑printable/gibberish characters.
    """
    occs = []
    for txt in soup.find_all(string=True):
        if txt.parent.name in ('script', 'style') or isinstance(txt, Comment):
            continue
        text = str(txt)
        for kw in keywords:
            pat = make_pattern(kw)
            for m in pat.finditer(text):
                start, end = m.span()
                snippet = text[max(0, start - 30): end + 30].replace("\n", " ").strip()
                if not is_snippet_valid(snippet):
                    continue
                occs.append({
                    "keyword": kw,
                    "tag":     txt.parent.name,
                    "snippet": snippet
                })
    return occs


def crawl_and_collect(start_url, keywords, max_depth, timeout):
    session = make_session()
    domain  = urlparse(start_url).netloc
    visited = {start_url}
    queue   = deque([(start_url, 0)])
    grouped = {}

    while queue:
        url, depth = queue.popleft()
        try:
            html = fetch_html(session, url, timeout)
        except Exception as e:
            print(f"[!] Failed to fetch {url}: {e}", file=sys.stderr)
            continue

        soup = BeautifulSoup(html, 'lxml')
        occs = locate_keywords(soup, keywords)

        if occs:
            if url not in grouped:
                grouped[url] = {
                    "url":     url,
                    "depth":   depth,
                    "matches": []
                }
            grouped[url]["matches"].extend(occs)

        if depth < max_depth:
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                if link.startswith("http") and urlparse(link).netloc == domain:
                    if link not in visited:
                        visited.add(link)
                        queue.append((link, depth + 1))

        time.sleep(REQUEST_DELAY)

    return list(grouped.values())


def export_json(results, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Crawl "
    )
    parser.add_argument('url', help="Starting URL")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-k', '--keywords', nargs='+',
        help="List of keywords to search for (enclose multi‑word ones in quotes) separate by spaces"
    )
    group.add_argument(
        '-f', '--keywords-file',
        help="Path to a file containing one keyword (or phrase) per line saved as .txt"
    )
    parser.add_argument(
        '-d', '--depth', type=int, default=1,
        help="Max crawl depth (0 = only the start page) changes the number of sublinks links to follow"
    )
    parser.add_argument(
        '-t', '--timeout', type=int, default=10,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        '--json', default=f'{start_time}_matches.json',
        help="Output JSON file (default: curtime_matches.json)"
    )
    args = parser.parse_args()

    if args.keywords:
        keywords = args.keywords
    else:
        with open(args.keywords_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]

    start_time = time.time()
    results = crawl_and_collect(args.url, keywords, args.depth, args.timeout)
    end_time = time.time()

    if not results:
        print("No matches found.", file=sys.stderr)
        sys.exit(1)

    for entry in results:
        url = entry["url"]
        depth = entry["depth"]
        for m in entry["matches"]:
            print(
                f"[depth {depth}] {url}  –  "
                f"'{m['keyword']}' in <{m['tag']}> …{m['snippet']}…"
            )

    export_json(results, args.json)
    elapsed = end_time - start_time
    print(f"\nExported {len(results)} URLs with matches to '{args.json}'")
    print(f"Total execution time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
