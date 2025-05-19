# RSS1 Extemp Topic Generator – Refactor & Enhancement Guide

> **NOTE:** Refactor in progress. Subject/category logic and UI have been removed from all main scripts as per this spec. See app.py, refresh_rss.py, and rss_archive_script.py for current implementation.

## Overview

Transform the RSS1 repo into a high-performance, streamlined Streamlit app for extemporaneous speaking topic generation.  
The app should use **spaCy** for advanced headline parsing and question generation, leverage existing hourly RSS/CSV logic, and provide a clean, low-latency interface that presents 3 nuanced topic questions and up to 10 full-text related articles per selection.  
Logging is strictly for administrative tracking: only log which topic was chosen and what articles were shown.

---

## 1. Remove Unneeded Features

- **Delete or disable:**
  - Any code or files for user authentication, scholar/admin dashboards, bonus points, peer question logs, or subject/category/tagging logic.
  - All subject filtering (no domestic/international or topic tags).

---

## 2. RSS Handling

- **Preserve the existing RSS pull and archive system:**  
  - Keep `refresh_rss.py` and `rss_archive_script.py` logic that pulls hourly from non-paywalled feeds, deduplicates, and saves headlines to `rss_archive.csv`.
  - Limit each feed to max 10 new headlines per pull.
  - Remove all subject/category logic—store “Subject”: “General” or drop the column entirely.

- **Deduplication:**  
  - Maintain the deduplication on `Date`, `Title`, and `Link` before saving to archive.
  - Example:
    ```python
    df_all = pd.concat([df_archive, new_df]).drop_duplicates(subset=["Date", "Title", "Link"])
    df_all.to_csv(archive_file, index=False)
    ```

---

## 3. Advanced Topic Generation with spaCy

- **Integrate/expand spaCy headline parsing in `app.py`:**
  - Load spaCy English model (`en_core_web_sm`).
  - Use subject-verb-object (SVO) and named entity recognition (NER) to rephrase headlines as extemp questions.
  - Use varied templates for *informative* and *persuasive* framing.

  ```python
  import spacy
  import random
  nlp = spacy.load("en_core_web_sm")

  def to_question(headline):
      doc = nlp(headline)
      subj = next((tok.text for tok in doc if tok.dep_ == "nsubj"), None)
      verb = next((tok.lemma_ for tok in doc if tok.dep_ == "ROOT"), None)
      obj  = next((tok.text for tok in doc if tok.dep_ == "dobj"), None)
      if subj and verb and obj:
          templates = [
              f"What is the significance of {subj} {verb} {obj}?",
              f"How has {subj} {verb} {obj} affected society?",
              f"Should {subj} {verb} {obj}? Why or why not?"
          ]
          return random.choice(templates)
      return None
  ```

- **Generate three questions:**
  ```python
  def generate_topics(headlines):
      questions = [q for h in headlines if (q := to_question(h))]
      return random.sample(questions, min(3, len(questions)))
  ```

---

## 4. UI Refactor in `app.py`

- **Streamlit UI:**
  - Main page displays “Generate Topics” button.
  - After click, show 3 question options as a radio select.
  - On selecting a topic and clicking “Show Related Articles,” display up to 10 related articles, each in a collapsible container (`st.expander`), with full text (no links, no summarization).
  - Remove all references to “Subject” in UI or dataframes.

  ```python
  if st.button("Generate Topics"):
      st.session_state["topics"] = generate_topics(df_today["Title"])

  if st.session_state.get("topics"):
      choice = st.radio("Choose a topic:", st.session_state["topics"])
      if choice and st.button("Show Related Articles"):
          related = find_related_articles(choice, df_archive)
          for art in related:
              with st.expander(art["Title"]):
                  st.write(art["text"])
          log_selection(choice, related)
          st.success("Session logged.")
  ```

---

## 5. Article Retrieval (Full Text)

- **Limit related articles to 10 per topic.**
- **Cache article downloads for speed:**
  ```python
  @st.cache_data(max_entries=100)
  def fetch_article_text(url):
      try:
          article = Article(url)
          article.download()
          article.parse()
          return article.text
      except:
          return "[Content not available]"
  ```

- **Find related articles by keyword match in headline:**
  ```python
  def find_related_articles(topic, df):
      doc = nlp(topic)
      keywords = [tok.lemma_.lower() for tok in doc if tok.is_alpha and not tok.is_stop]
      mask = df["Title"].str.lower().apply(lambda t: any(k in t for k in keywords))
      articles = df[mask][["Title", "Link"]].drop_duplicates().head(10)
      articles = articles.to_dict(orient="records")
      for art in articles:
          art["text"] = fetch_article_text(art["Link"])
      return articles
  ```

---

## 6. Logging

- **Log the selected topic and article titles to `topic_logs.csv`:**
  ```python
  import pandas as pd
  from datetime import datetime

  def log_selection(topic, articles):
      log_file = "topic_logs.csv"
      entry = {
          "timestamp": datetime.now().isoformat(),
          "topic": topic,
          "articles": "; ".join(a["Title"] for a in articles)
      }
      if os.path.exists(log_file):
          df = pd.read_csv(log_file)
      else:
          df = pd.DataFrame(columns=["timestamp","topic","articles"])
      df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
      df.to_csv(log_file, index=False)
  ```

---

## 7. Scheduling (Optional but recommended)

- **To keep the archive fresh, run `refresh_rss.py` with a scheduler:**
  - Use the Python `schedule` library or a system cron job.
  - Example for a standalone loop at the end of `refresh_rss.py`:
    ```python
    import schedule, time
    schedule.every().hour.do(refresh_rss)
    while True:
        schedule.run_pending()
        time.sleep(60)
    ```

---

## 8. Requirements

- `spacy`
- `en_core_web_sm`
- `feedparser`
- `pandas`
- `streamlit`
- `newspaper3k`
- `schedule` (for hourly pulls)

---

## 9. General Notes

- **No topic categorization, no external API keys, no summarization, no login.**
- **Everything else (structure, RSS list, CSV logic) should remain as in the current repo, unless refactoring for performance.**

---

## 10. Migration & Review

- Remove deprecated code/files.
- Double-check all dataframes, logs, and UI widgets for references to now-removed fields.
- Test performance with >1000 headlines in `rss_archive.csv` to ensure UI doesn’t lag.
- Ensure only 10 articles per topic are displayed (per session, per user click).
- Optionally, run `python -m spacy download en_core_web_sm` to ensure spaCy model is present.

---

## Setup Instructions

To set up the environment and install all dependencies (including the spaCy English model), run:

```bash
chmod +x setup.sh
./setup.sh
```

This will install all required Python packages and download the spaCy model needed for topic generation.

---

**This markdown file is the spec for your refactor. Paste it into your repo root or give it directly to Copilot/Visual Studio Code Agent Mode for maximum clarity.**

