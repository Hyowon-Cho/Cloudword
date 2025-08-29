import json, re, os, datetime as dt
from collections import Counter
import spacy
nlp = spacy.load("en_core_web_sm")

STOP_EXTRA = set("""
amp rt http https www com reddit people thing things today really good
great bad new make use work time think want look need year like get got
say said more one two three etc
""".split())

def tokenize_en(text: str):
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    doc = nlp(text.lower())
    toks = [t.lemma_ for t in doc if t.is_alpha and not t.is_stop and len(t) > 2]
    return [t for t in toks if t not in STOP_EXTRA]

def aggregate(file_in:str, file_out:str):
    now = dt.datetime.utcnow()
    with open(file_in, encoding="utf-8") as f:
        posts = json.load(f)

    counter = Counter()
    for p in posts:
        text = (p["title"] + " " + (p.get("selftext") or "")).strip()
        toks = tokenize_en(text)
        for t in toks:
            counter[t] += 1 
            
    with open(file_out, "w", encoding="utf-8") as f:
        json.dump(counter, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    for cat in ["politics","cars","gaming"]:
        infile = f"data_raw_{cat}.json"
        outfile = f"data_terms_{cat}.json"
        if os.path.exists(infile):
            aggregate(infile, outfile)
            print("aggregated:", cat)
