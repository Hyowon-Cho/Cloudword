# Cloudword Project

## Tech Stack

### 1. Language & Runtime
- **Python 3.13** (installed via Homebrew, using virtual environment `.venv`)

### 2. Data Collection
- **Python Reddit API Wrapper (PRAW)** -> fetch Reddit posts  
- **python-dotenv** -> manage API keys and secrets through `.env` file

### 3. Data Processing
- **spaCy** (`en_core_web_sm` model) -> English tokenization, stopword removal, lemmatization  
- **collections.Counter** -> count term frequencies

### 4. Visualization
- **WordCloud (python-wordcloud)** -> generate word cloud images from term frequencies  
- **Pillow (PIL)** -> image handling (used internally by WordCloud)

### 5. Server & API
- **Flask** -> lightweight web server and REST API  
- **Flask render_template_string** -> currently serve a simple HTML-based UI

### 6. Execution & Pipeline
- **Python Scripts**:  
  - `fetch_reddit.py` -> fetch raw Reddit data  
  - `process_terms.py` -> tokenize & aggregate word frequencies  
  - `make_cloud.py` -> generate word cloud images  
  - `run_pipeline.py` -> automate the full pipeline  

### 7. Development Environment
- **Visual Studio Code (VS Code)**  
- **macOS** (Zsh shell, Homebrew) -> development environment management

---

## Architecture Overview
1. **Reddit API** -> PRAW -> store as JSON  
2. **spaCy** -> tokenize & preprocess text -> generate term frequency JSON  
3. **WordCloud** -> render PNG images from frequencies  
4. **Flask** -> provide APIs (`/top`, `/cloud`) and a simple web dashboard UI  

---

## Test Pictures

<img width="743" height="775" alt="Image" src="https://github.com/user-attachments/assets/532c5991-4679-4004-936e-4cd88be155a5" />

<img width="743" height="775" alt="Image" src="https://github.com/user-attachments/assets/657b9feb-d783-45ee-a31c-ef9fc12fcb0c" />

<img width="743" height="775" alt="Image" src="https://github.com/user-attachments/assets/b1ee3710-3cbc-4961-8597-844c7d26f49c" />

<img width="743" height="775" alt="Image" src="https://github.com/user-attachments/assets/532c5991-4679-4004-936e-4cd88be155a5" />

<img width="743" height="775" alt="Image" src="https://github.com/user-attachments/assets/657b9feb-d783-45ee-a31c-ef9fc12fcb0c" />

<img width="743" height="775" alt="Image" src="https://github.com/user-attachments/assets/b1ee3710-3cbc-4961-8597-844c7d26f49c" />
