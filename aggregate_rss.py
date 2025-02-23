import feedparser
import xmltodict
import time
import json
import os
from datetime import datetime


# List of RSS feeds to poll
RSS_FEEDS = {
    "HN": "https://hnrss.org/frontpage?points=100",  # Hacker News, front page, 100+ points
    "Stratechery": "https://stratechery.passport.online/feed/rss/CLUsu28XgnV1NzU3ZQjxw",  # free Stratechery,
}


OUTPUT_FILE = "custom_feed.xml"
HISTORY_FILE = "history.json"


def load_history():
    """Load previously saved articles."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(entries):
    """Save articles to history.json."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4)


def fetch_feeds():
    """Fetch and deduplicate RSS entries."""

    history = load_history()
    seen_links = set([history_item["link"] for history_item in history])

    # Start with saved history
    entries = history.copy()

    count_new = 0

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link not in seen_links:
                count_new += 1
                seen_links.add(entry.link)
                entries.append(
                    {
                        "title": entry.title,
                        "link": entry.link,
                        "description": entry.get("summary", ""),
                        "source": source,
                        "pubDate": entry.get("published", ""),
                        "retrievedDate": datetime.now().strftime(
                            "%m/%d/%Y, %I:%M:%S %p"
                        ),
                    }
                )

    print(f"Added {count_new} new entries to history.")
    # Sort by date (newest first)
    entries.sort(key=lambda x: x.get("pubDate", ""), reverse=True)

    return entries


# def generate_rss(entries):
#     """Generate an RSS feed from entries."""
#     rss_structure = {
#         "rss": {
#             "@version": "2.0",
#             "channel": {
#                 "title": "My Custom RSS Feed",
#                 "link": "https://yourgithubusername.github.io/custom_feed.xml",
#                 "description": "Aggregated RSS Feed",
#                 "item": entries,
#             },
#         }
#     }
#     return xmltodict.unparse(rss_structure, pretty=True)


if __name__ == "__main__":
    feed_entries = fetch_feeds()
    save_history(feed_entries)  # Persist history

    # rss_content = generate_rss(feed_entries)

    # with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    #     f.write(rss_content)

    print(f"RSS feed with {len(feed_entries)} total entries.")
