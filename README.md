
# PulverLogic RSS Dashboard

A powerful, modular Streamlit app designed to track news headlines across multiple sources for academic, debate, and classroom purposes.

## 🚀 Features

### 📰 Top Headlines
- Live RSS feed pulls from NPR, Reuters, and Al Jazeera
- Each article is displayed in a clean, focused layout
- Click to view full article, metadata, and generate GPT-powered claim + warrant

### 📊 Visual Dashboard
- Interactive Plotly line chart showing subject frequency trends over time
- Dropdown filters allow drill-down into specific subjects and dates
- Credibility and subject breakdowns displayed with clean visualizations

### 📂 Archive Dashboard
- Daily archiving of all RSS data to `rss_archive.csv`
- Filter by subject or date range
- Export to CSV for classroom or research use

## 🧠 Built For
- Extemp, PF, Congress, and classroom research
- Educators, students, and debate teams
- Ongoing archive building and news-trend visualization

## 📦 Installation

1. Upload all project files (including this README and requirements.txt)
2. Install dependencies using:

```
pip install -r requirements.txt
```

3. Run locally with:

```
streamlit run app.py
```

Or deploy via [Streamlit Cloud](https://streamlit.io/cloud)

## 🔐 Setup
You’ll need to add your OpenAI key as a secret in Streamlit Cloud:

```
OPENAI_API_KEY = "your-api-key"
```

## 📈 Data
- Archive auto-saves into `rss_archive.csv`
- Can be linked to Google Sheets or exported manually
