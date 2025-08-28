from flask import Flask, request, send_file, abort
from wordcloud import WordCloud
import tempfile, os

app = Flask(__name__)

@app.get("/")
def home():
    return "OK: /cloud_from_text?text=hello+world"

@app.get("/cloud_from_text")
def cloud_from_text():
    text = request.args.get("text", "").strip()
    if not text:
        abort(400, "text querystring is required")

    wc = WordCloud(
        width=800, height=600,
        background_color="white",
        collocations=False
    ).generate(text)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    wc.to_file(tmp.name)
    path = tmp.name
    tmp.close()

    resp = send_file(path, mimetype="image/png")
    try:
        os.remove(path)
    except Exception:
        pass
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5001)
