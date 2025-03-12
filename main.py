import argparse
import sys
from fetch_papers import fetch_paper_ids, fetch_paper_details, save_to_csv
from tabulate import tabulate

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed.")
    parser.add_argument("-f", "--file", type=str, help="Save results to a file.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")

    args = parser.parse_args()

    if args.debug:
        print(f"Fetching papers for query: {args.query}")
    try:
        paper_ids = fetch_paper_ids(args.query)
        if args.debug:
            print(f"Found PubMed IDs: {paper_ids}")

        papers = fetch_paper_details(paper_ids)
        if not papers:
            print("No papers found matching the criteria.")
            return

        if args.file:
            save_to_csv(papers, args.file)
            print(f"Results saved to {args.file}")
        else:
            print(tabulate(papers, headers="keys", tablefmt="grid"))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
