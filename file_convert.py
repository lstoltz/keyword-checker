import argparse
import json
import csv
import sys

def json_to_csv(json_path: str, csv_path: str):
    # Load JSON data
    try:
        with open(json_path, 'r', encoding='utf-8') as jf:
            data = json.load(jf)
    except Exception as e:
        print(f"Error reading JSON file '{json_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Open CSV and write rows
    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
            writer = csv.writer(cf)
            # Write header
            writer.writerow(['url', 'depth', 'keyword', 'tag', 'snippet'])

            # Iterate through JSON objects
            for entry in data:
                url = entry.get('url', '')
                depth = entry.get('depth', '')
                matches = entry.get('matches', [])
                for m in matches:
                    keyword = m.get('keyword', '')
                    tag = m.get('tag', '')
                    snippet = m.get('snippet', '')
                    writer.writerow([url, depth, keyword, tag, snippet])
    except Exception as e:
        print(f"Error writing CSV file '{csv_path}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON keyword match results to CSV.'
    )
    parser.add_argument(
        'json_file',
        help='Path to the input JSON file (grouped keyword matches)'
    )
    parser.add_argument(
        'csv_file',
        help='Path to the output CSV file'
    )
    args = parser.parse_args()

    json_to_csv(args.json_file, args.csv_file)
    print(f"Converted '{args.json_file}' to '{args.csv_file}' successfully.")

if __name__ == '__main__':
    main()
