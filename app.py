from flask import Flask, request, send_file
from wordcloud import WordCloud
import os
import tempfile

app = Flask(__name__)

@app.post("/text")
def text_api():
    
    # 화면상 검색창에 입력한 text(JSON: {keyword: ...})를 받아 워드클라우드 이미지로 반환하는 API

    data = request.get_json()
    if not data or "keyword" not in data:
        return {"error": "JSON body with 'keyword' required"}, 400

    text = data["keyword"].strip()
    if not text:
        return {"error": "keyword cannot be empty"}, 400

    # 워드클라우드 생성
    wc = WordCloud(
        width=1000, height=700,
        background_color="white",
        max_words=300,
        collocations=False
    ).generate(text)

    # 임시 파일에 저장
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    wc.to_file(tmp.name)
    path = tmp.name
    tmp.close()

    # 이미지 응답 후 임시 파일 삭제
    resp = send_file(path, mimetype="image/png")
    try:
        os.remove(path)
    except Exception:
        pass
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5001)
