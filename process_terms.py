# app.py
from flask import Flask, request, send_file, jsonify, render_template_string
import os, json, subprocess, sys

app = Flask(__name__)

CATS = ["politics", "cars", "gaming"]

def terms_path(cat): return f"data_terms_{cat}.json"
def image_path(cat): return f"outputs/{cat}.png"

def load_terms(cat):
    with open(terms_path(cat), encoding="utf-8") as f:
        d = json.load(f)
    # 상위 50개만
    return sorted(d.items(), key=lambda x: x[1], reverse=True)[:50]

@app.get("/top")
def top():
    cat = request.args.get("category", "politics")
    if cat not in CATS or not os.path.exists(terms_path(cat)):
        return jsonify({"error": "unknown category or data missing"}), 404
    items = load_terms(cat)
    return jsonify([{"term": t, "count": int(c)} for t, c in items])

@app.get("/cloud")
def cloud():
    cat = request.args.get("category", "politics")
    if cat not in CATS:
        return {"error": "unknown category"}, 404
    # 이미지 없으면 한번 생성 시도
    if not os.path.exists(image_path(cat)):
        # make_cloud.py는 data_terms_*.json을 읽어 outputs/*.png 생성
        subprocess.run([sys.executable, "make_cloud.py"], check=False)
    if not os.path.exists(image_path(cat)):
        return {"error": "image not found. Run process_terms.py & make_cloud.py"}, 404
    return send_file(image_path(cat), mimetype="image/png")

# 아주 가벼운 UI
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>cloudword</title>
  <style>
    body { font-family: system-ui, -apple-system; margin: 24px; }
    .wrap { display: grid; grid-template-columns: 260px 1fr; gap: 24px; }
    select, button { font-size: 14px; padding: 6px 8px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: 1px solid #ddd; padding: 6px 4px; font-size: 14px; }
    img { max-width: 100%; border: 1px solid #eee; }
  </style>
</head>
<body>
  <h1>cloudword</h1>
  <div class="wrap">
    <div>
      <form id="f">
        <label>Category:
          <select id="cat">
            {% for c in cats %}
              <option value="{{c}}">{{c}}</option>
            {% endfor %}
          </select>
        </label>
        <button type="button" onclick="reload()">Load</button>
      </form>
      <h3>Top terms</h3>
      <table id="tbl"><thead><tr><th>term</th><th>count</th></tr></thead><tbody></tbody></table>
    </div>
    <div>
      <img id="img" src="" alt="wordcloud"/>
    </div>
  </div>
<script>
async function reload(){
  const cat = document.getElementById('cat').value;
  document.getElementById('img').src = '/cloud?category=' + encodeURIComponent(cat) + '&_=' + Date.now();
  const r = await fetch('/top?category=' + encodeURIComponent(cat));
  const data = await r.json();
  const tbody = document.querySelector('#tbl tbody');
  tbody.innerHTML = '';
  (data || []).forEach(row=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.term}</td><td>${row.count}</td>`;
    tbody.appendChild(tr);
  });
}
reload();
</script>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(INDEX_HTML, cats=CATS)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
