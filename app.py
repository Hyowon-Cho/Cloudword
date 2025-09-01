from flask import Flask, request, send_file, jsonify, render_template_string, url_for
import os, re
from dotenv import load_dotenv
import praw
import spacy
from wordcloud import WordCloud
from collections import Counter

app = Flask(__name__)

# --- Reddit API ---
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# --- spaCy setup ---
nlp = spacy.load("en_core_web_sm")
STOP_EXTRA = set("amp rt http https www com reddit people thing today really get one two".split())

def tokenize(text: str):
    text = re.sub(r"http\\S+|www\\.\\S+", " ", text)
    doc = nlp(text.lower())
    toks = [t.lemma_ for t in doc if t.is_alpha and not t.is_stop and len(t) > 2]
    return [t for t in toks if t not in STOP_EXTRA]

def fetch_terms(sub: str, sort="hot", time_filter="all", limit=150):
    cnt = Counter()
    sr = reddit.subreddit(sub)
    if sort == "new":
        submissions = sr.new(limit=limit)
    elif sort == "top":
        submissions = sr.top(time_filter=time_filter, limit=limit)
    else:
        submissions = sr.hot(limit=limit)

    for s in submissions:
        text = (s.title or "") + " " + (s.selftext or "")
        for t in tokenize(text):
            cnt[t] += 1
    return dict(cnt)

def make_wc(freq: dict, out_path: str, colormap="viridis", bg="white", max_words=300):
    wc = WordCloud(
        width=1100, height=800,
        background_color=bg,
        max_words=max_words,
        colormap=colormap,
        collocations=False,
        prefer_horizontal=0.9,
    )
    wc.generate_from_frequencies(freq).to_file(out_path)

# --- API endpoints ---
@app.get("/cloud")
def cloud():
    sub = request.args.get("sub", "").strip().removeprefix("r/").lower()
    limit = int(request.args.get("limit", 150))
    maxw = int(request.args.get("max_words", 300))
    sort = request.args.get("sort", "hot")
    timef = request.args.get("time_filter", "all")
    cmap = request.args.get("colormap", "viridis")
    bg = request.args.get("bg", "white")

    if not sub:
        return {"error": "subreddit missing"}, 400
    freq = fetch_terms(sub, sort=sort, time_filter=timef, limit=limit)
    if not freq:
        return {"error": f"no posts found in r/{sub}"}, 404
    os.makedirs("outputs", exist_ok=True)
    out = f"outputs/live_{sub}.png"
    make_wc(freq, out, colormap=cmap, bg=bg, max_words=maxw)
    return send_file(out, mimetype="image/png")

@app.get("/top")
def top():
    sub = request.args.get("sub", "").strip().removeprefix("r/").lower()
    limit = int(request.args.get("limit", 150))
    sort = request.args.get("sort", "hot")
    timef = request.args.get("time_filter", "all")
    if not sub:
        return {"error": "subreddit missing"}, 400
    freq = fetch_terms(sub, sort=sort, time_filter=timef, limit=limit)
    items = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]
    return jsonify([{"term": t, "count": int(c)} for t, c in items])

# --- Frontend skeleton ---
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>CloudWord</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header><h1>CloudWord</h1></header>
  <div class="container">
    <div class="card">
      <label>Subreddit
        <input id="sub" placeholder="e.g. technology, AskReddit, nba" />
      </label>
      <label>Number of posts
        <input id="limit" type="number" value="150" min="50" max="500"/>
      </label>
      <label>Max words
        <input id="maxw" type="number" value="300" min="50" max="500"/>
      </label>
      <label>Sort by
        <select id="sort">
          <option value="hot">Hot</option>
          <option value="new">New</option>
          <option value="top">Top</option>
        </select>
      </label>
      <label>Time filter
        <select id="timef">
          <option value="all">All time</option>
          <option value="day">1 day</option>
          <option value="week">1 week</option>
          <option value="month">1 month</option>
          <option value="year">1 year</option>
        </select>
      </label>
      <label>Colormap
        <select id="cmap">
          <option value="viridis">Viridis</option>
          <option value="plasma">Plasma</option>
          <option value="inferno">Inferno</option>
          <option value="magma">Magma</option>
          <option value="Set2">Set2</option>
          <option value="tab10">tab10</option>
        </select>
      </label>
      <label>Background
        <select id="bg">
          <option value="white">White</option>
          <option value="black">Black</option>
        </select>
      </label>
      <button onclick="go()">Generate</button>
      <h2>Top terms</h2>
      <ul id="list"><li class="loading">Enter subreddit and click Generate.</li></ul>
    </div>
    <div class="card" style="align-items:center;justify-content:center;">
      <img id="img" src="" alt="WordCloud result"/>
      <div class="dl" id="dl"></div>
    </div>
  </div>
  <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>
"""

@app.get("/")
def index(): 
    return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
