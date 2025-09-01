# Cloudword Project

This project collects text data from Reddit, processes it with Natural Language Processing (NLP), and generates **WordClouds** based on word frequencies. The results are visualized through a simple web dashboard built with Flask.

---

https://cloudword.onrender.com

---

## How to Run

### 1. Clone Repository
```bash
git clone https://github.com/Hyowon-Cho/cloudword.git
cd cloudword
```

### 2. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install required Python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

Then download the spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

### 4. Reddit API Keys
Create a `.env` file in the project root (`cloudword/`) and fill in your Reddit credentials:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=cloudword:0.1 (by u/your_reddit_username)
```

### 5. Run the Pipeline
```bash
python fetch_reddit.py # Fetch Reddit data
python process_terms.py # Tokenize & aggregate terms
python make_cloud.py # Generate WordCloud images
```

### 6. Run the Server
```bash
python app.py
```

Then, open in your browser:
- http://localhost:5001/ -> Dashboard  
- http://localhost:5001/cloud?category=politics -> WordCloud image  
- http://localhost:5001/top?category=politics -> Term frequency JSON  

## 🧑‍💻 Tech Stack

- **Python 3.13** 
- **Flask** -> lightweight web server & REST API (`/cloud`, `/top`, `/`)
- **PRAW** -> Reddit API data collection
- **python-dotenv** -> environment variable management
- **spaCy (en_core_web_sm)** -> tokenization, stopword removal, lemmatization
- **collections.Counter** -> term frequency aggregation
- **WordCloud (python-wordcloud)** -> frequency-based word cloud generation
- **Pillow (PIL)** -> image processing (used by WordCloud)
- **Git & GitHub** -> version control, README documentation
- **Visual Studio Code** -> macOS development environment (Homebrew, zsh)

---

## 🧩 Architecture Overview

1. **Reddit API** -> `fetch_reddit.py` -> stored as JSON  
2. **spaCy** -> preprocess & tokenize text -> generate term frequency JSON  
3. **WordCloud** -> create PNG images from frequencies  
4. **Flask** -> expose API (`/top`, `/cloud`) + simple web dashboard  

---

## Test Pictures

<img width="1512" height="895" alt="스크린샷 2025-08-31 오후 9 38 46" src="https://github.com/user-attachments/assets/060155e3-7f83-4b38-add6-7efeb31f3832" />