import os, json
from dotenv import load_dotenv
import praw


load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

CATEGORY_SUBS = {
    "politics": ["politics"],
    "cars": ["cars"],
    "gaming": ["gaming"],
}

def fetch_category(cat: str, limit=50):
    items = []
    subs = CATEGORY_SUBS[cat]
    per_sub = max(10, limit // len(subs))
    for sub in subs:
        for s in reddit.subreddit(sub).hot(limit=per_sub):
            items.append({
                "id": s.id,
                "subreddit": sub,
                "title": s.title or "",
                "score": s.score,
                "num_comments": s.num_comments,
                "selftext": s.selftext or "",
            })
    return items

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    for cat in CATEGORY_SUBS:
        data = fetch_category(cat)
        save_json(f"data_raw_{cat}.json", data)
        print(cat, len(data), "posts saved.")
