from flask import Flask, request, send_file, jsonify, render_template_string
import os, re, time
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

# --- Endpoints ---
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
    try:
        freq = fetch_terms(sub, sort=sort, time_filter=timef, limit=limit)
        if not freq:
            return {"error": f"no posts found in r/{sub}"}, 404
        os.makedirs("outputs", exist_ok=True)
        out = f"outputs/live_{sub}.png"
        make_wc(freq, out, colormap=cmap, bg=bg, max_words=maxw)
        return send_file(out, mimetype="image/png")
    except Exception as e:
        return {"error": str(e)}, 400

@app.get("/top")
def top():
    sub = request.args.get("sub", "").strip().removeprefix("r/").lower()
    limit = int(request.args.get("limit", 150))
    sort = request.args.get("sort", "hot")
    timef = request.args.get("time_filter", "all")
    if not sub:
        return {"error": "subreddit missing"}, 400
    try:
        freq = fetch_terms(sub, sort=sort, time_filter=timef, limit=limit)
        items = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]
        return jsonify([{"term": t, "count": int(c)} for t, c in items])
    except Exception as e:
        return {"error": str(e)}, 400

# --- Frontend UI ---
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>CloudWord Live</title>
  <style>
    body {
      font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
      margin:0;padding:0;background:#f9fafb;color:#111827;
    }
    header {
      background:#2563eb;color:white;padding:16px 24px;text-align:center;
    }
    header h1 {margin:0;font-size:22px;}
    .container {
      max-width:1200px;margin:24px auto;padding:0 16px;
      display:grid;grid-template-columns:1fr 2fr;gap:24px;
    }
    @media(max-width:800px){.container{grid-template-columns:1fr;}}
    .card {
      background:white;padding:20px;border-radius:8px;
      box-shadow:0 1px 3px rgba(0,0,0,0.1);
      display:flex;flex-direction:column;
    }
    label {display:block;margin-bottom:12px;font-weight:500;font-size:14px;}
    input,select {
      width:100%;padding:8px 10px;font-size:14px;
      border:1px solid #d1d5db;border-radius:6px;margin-top:4px;
    }
    button {
      margin-top:8px;padding:10px 14px;background:#2563eb;color:white;
      border:none;border-radius:6px;cursor:pointer;font-size:15px;font-weight:500;
    }
    button:hover{background:#1e40af;}
    h2{font-size:16px;margin:16px 0 8px;}
    ul{list-style:none;padding:0;margin:0;flex:1;overflow-y:auto;}
    li{padding:6px 0;border-bottom:1px solid #f3f4f6;font-size:14px;}
    img{max-width:100%;border-radius:8px;margin-top:8px;align-self:center;}
    .loading{text-align:center;padding:20px;color:#6b7280;}
    .dl{margin-top:12px;text-align:center;}
    .dl a{
      display:inline-block;padding:8px 12px;background:#10b981;color:white;
      border-radius:6px;text-decoration:none;font-size:14px;
    }
    .dl a:hover{background:#059669;}
  </style>
</head>
<body>
  <header><h1> CloudWord </h1></header>
  <div class="container">
    <!-- Left panel -->
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
      <label>Background color
        <select id="bg">
          <option value="white">White</option>
          <option value="black">Black</option>
        </select>
      </label>
      <button onclick="go()">Generate </button>

      <h2>Top terms</h2>
      <ul id="list"><li class="loading">Enter subreddit and click Generate.</li></ul>
    </div>
    <!-- Right panel -->
    <div class="card" style="align-items:center;justify-content:center;">
      <img id="img" src="" alt="WordCloud result"/>
      <div class="dl" id="dl"></div>
    </div>
  </div>
<script>
async function go(){
  const sub=document.getElementById('sub').value.trim().replace(/^r\\//,'');
  const limit=document.getElementById('limit').value||150;
  const maxw=document.getElementById('maxw').value||300;
  const sort=document.getElementById('sort').value;
  const timef=document.getElementById('timef').value;
  const cmap=document.getElementById('cmap').value;
  const bg=document.getElementById('bg').value;

  const list=document.getElementById('list');
  const img=document.getElementById('img');
  const dl=document.getElementById('dl');

  if(!sub){alert('Please enter a subreddit');return;}

  list.innerHTML='<li class="loading">Loading...</li>';
  img.src=''; dl.innerHTML='';

  try{
    img.src='/cloud?sub='+encodeURIComponent(sub)
           +'&limit='+limit+'&max_words='+maxw
           +'&sort='+sort+'&time_filter='+timef
           +'&colormap='+cmap+'&bg='+bg
           +'&_='+Date.now();

    dl.innerHTML='<a href="'+img.src+'" download="cloud_'+sub+'.png">⬇ Download PNG</a>';

    const r=await fetch('/top?sub='+encodeURIComponent(sub)
                        +'&limit='+limit
                        +'&sort='+sort
                        +'&time_filter='+timef);
    const data=await r.json();
    if(data.error){list.innerHTML='<li class="loading">'+data.error+'</li>';return;}
    list.innerHTML='';
    (data||[]).forEach(x=>{
      const li=document.createElement('li');
      li.textContent=x.term+" ("+x.count+")";
      list.appendChild(li);
    });
  }catch(err){
    list.innerHTML='<li class="loading">Failed to load.</li>';
  }
}
</script>
</body>
</html>
"""
@app.get("/")
def index(): return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
