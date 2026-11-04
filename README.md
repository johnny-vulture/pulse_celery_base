# Pulse Celery Base

A Flask + Celery backend that scrapes live soccer match commentary and scores (Goal.com / ESPN), stores match data in MongoDB, rewrites high-signal events with OpenAI for Twitter-style posts, and generates match-moment images via Hugging Face Stable Diffusion.

## Features

- Flask API to enqueue scrape jobs and poll Celery task status
- Celery workers for commentary/score scraping and match pipelines
- Selenium scrapers for Goal.com scores and ESPN commentary
- MongoDB storage for matches, comments, tweetable events, and tweeted posts
- NLP event ranking with spaCy (goals, cards, penalties, etc.)
- OpenAI rewrite of commentary into lively social posts
- Hugging Face image generation for tweetable moments
- Optional Google Sheets integration for fixture scheduling (`sheet.py`)

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | Flask |
| Task queue | Celery + RabbitMQ (`amqp://guest@localhost//`) |
| Database | MongoDB (`celery` DB) |
| Scraping | Selenium + ChromeDriver |
| NLP | spaCy (`en_core_web_md`) |
| LLM | OpenAI (`gpt-4o`) |
| Images | Hugging Face Inference API (SDXL) |
| Sheets (optional) | Google Sheets API |

## Project Structure

```text
app.py              # Flask API + Celery config
tasks.py            # Celery tasks (scrape, match pipeline)
scrapers.py         # Selenium scrapers (ESPN commentary, Goal scores)
utils.py            # NLP ranking, OpenAI rewrite, HF image gen, Mongo helpers
sheet.py            # Google Sheets fixture lookup + Goal.com link matching
DB_dash.py          # Mongo helpers / sample inserts
constants.py        # MongoDB connection settings
Test/               # Experimental Celery/scraper scripts
images/             # Generated match images
credentials.json    # Google OAuth client secrets (local; do not commit real values)
token.json          # Google OAuth user token (local; do not commit real values)
