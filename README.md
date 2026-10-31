# Lab Assignment 4 – Selenium News Summarizer (Roll No. 59)

- **Registration:** FA23-BCT-059
- **News source:** 59 % 20 + 1 = **20 → MIT Technology Review**
- **Selenium language:** Python (Selenium 4 + headless Google Chrome + ChromeDriver)
- **API:** `GET /get?keyword=<keyword>` on port **7000** (starts automatically with the container)

## How it works
1. `scraper.py` opens headless Chrome with Selenium, loads the site's search page
   (`technologyreview.com/search/?s=<keyword>`) and picks the first search result.
2. It opens that article and collects the paragraph text.
3. `summarizer.py` builds an extractive summary (top-scoring sentences by word frequency).
4. `app.py` (Flask, served by gunicorn) returns:
   ```json
   {"registration": "...", "newssource": "...", "keyword": "...", "url": "...", "summary": "..."}
   ```
   The home page `/` shows the registration number.

## Docker Hub image
`zaynop/news-summarizer-59:latest`

```bash
docker pull zaynop/news-summarizer-59:latest
docker run -d -p 7000:7000 zaynop/news-summarizer-59:latest
curl "http://localhost:7000/get?keyword=quantum"
```

## Build and push yourself
```bash
docker build -t zaynop/news-summarizer-59:latest .
docker push zaynop/news-summarizer-59:latest
```
To use a different registration number without rebuilding: `docker run -e REGISTRATION=FA23-BCT-059 ...`
