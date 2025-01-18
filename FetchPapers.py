import feedparser
from datetime import datetime, timedelta
import urllib.parse


def fetch_arxiv_papers(query, category_filter = ["econ.","cs.","stat."], max_results = 200, days = 2):
    """
    Fetch the latest papers from arXiv matching the query and within the last N days.
    
    Args:
        query (str): The search query (e.g., "causal inference").
        max_results (int): The maximum number of results to fetch.
        days (int): Number of past days to filter papers.
    
    Returns:
        list: A list of dictionaries containing paper metadata.
    """
    # Calculate the date N days ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    query = "+OR".join(query)
    encoded_query = urllib.parse.quote_plus(query)

    # Base URL for arXiv API with date range filter
    base_url = (
        f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}"
        #f"+lastUpdatedDate:[{start_date}T00:00:00Z+TO+{today.strftime('%Y-%m-%dT23:59:59Z')}]"
        f"&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    )

    # Parse the feed
    feed = feedparser.parse(base_url)

    # Extract relevant paper details
    papers = []
    for entry in feed.entries:
        subjects = [info["term"] for info in entry.tags]
        include_sub = 0
        include_date = 0
        # Check if the paper belongs to the specified category
        for subject in subjects:
            for target_subject in category_filter:
                if target_subject in subject:
                    include_sub = 1
                    break

        # check if the paper is within the specified date range
        paper_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
        if start_date <= paper_date <= end_date:
            include_date = 1

        if include_sub == 0 or include_date == 0:
            continue
        papers.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [author.name for author in entry.authors],
            "published": entry.published,
            "link": entry.link,
            "Subject": subjects,
        })

    return papers

# Fetch Data
length = 2
query = ["causal inference"]
papers = fetch_arxiv_papers(query=query, max_results=200, days = length)

today = datetime.now()
end_date = today - timedelta(days=length)

# Save the papers to a file
file_name = f"Digest_{query}_{len(papers)}_{today.strftime('%Y-%m-%d')}to{end_date.strftime('%Y-%m-%d')}.txt"

with open(file_name, "w", encoding="utf-8") as f:
    for paper in papers:
        f.write(f"Title: {paper['title']}\n")
        f.write(f"Published: {paper['published']}\n")
        f.write(f"Link: {paper['link']}\n")
        f.write(f"Authors: {', '.join(paper['authors'])}\n")
        f.write(f"Subjects: {', '.join(paper['Subject'])}\n")
        f.write(f"Summary: {paper['summary']}\n")
        f.write("-"*100 + "\n")
