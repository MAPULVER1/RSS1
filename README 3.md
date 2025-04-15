
# 🗞️ RSS Newsboard

A live-updating news dashboard built with [Streamlit](https://streamlit.io) that pulls from RSS feeds across the ideological spectrum. Designed for educators, students, and the general public to engage with real-world current events in an organized and transparent way.

## 🌐 Hosted Project
This project can be hosted via [Streamlit Cloud](https://streamlit.io/cloud).

GitHub Repo: [https://github.com/MAPULVER1/RSS](https://github.com/MAPULVER1/RSS)

## ✅ Features
- Pulls live articles from multiple RSS sources
- Displays in sortable table format
- Includes links and publication timestamps
- Streamlit-based UI with expandable article views

## 📦 Setup Instructions

Clone the repository:
```bash
git clone https://github.com/MAPULVER1/RSS.git
cd RSS
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
```bash
streamlit run app.py
```

## 📚 Sources Used (Default)
- NPR (Education)
- Al Jazeera (Top News)
- Reuters (World News)

You can easily add more by editing the `rss_urls` dictionary in `app.py`.

## 🧠 Future Ideas
- GPT-based summaries
- Bias and credibility labeling
- Debate-mode for contrasting perspectives

Enjoy exploring the world of news!
