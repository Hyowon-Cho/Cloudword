# make_cloud.py
import json, os, glob
from wordcloud import WordCloud

def make_cloud(terms_path: str, out_png: str, width=1100, height=800, max_words=300):
    with open(terms_path, encoding="utf-8") as f:
        weights = json.load(f)  # {"term": count}
    # wordcloud는 dict[term -> weight] 형태를 그대로 받습니다.
    wc = WordCloud(
        width=width,
        height=height,
        background_color="white",
        max_words=max_words,
        collocations=False,
        prefer_horizontal=0.9,
    ).generate_from_frequencies({k: float(v) for k, v in weights.items()})

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    wc.to_file(out_png)

if __name__ == "__main__":
    files = sorted(glob.glob("data_terms_*.json"))
    if not files:
        print("No data_terms_*.json files found. Run process_terms.py first.")
    else:
        for fp in files:
            # 파일명에서 카테고리 추출: data_terms_<cat>.json
            base = os.path.basename(fp)
            cat = base.removeprefix("data_terms_").removesuffix(".json")
            out = f"outputs/{cat}.png"
            make_cloud(fp, out)
            print(f"Saved: {out}")