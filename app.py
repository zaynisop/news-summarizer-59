"""REST API exposing GET /get?keyword=... on port 7000."""
from flask import Flask, jsonify, request

from config import NEWS_SOURCE, REGISTRATION
from scraper import fetch_first_result
from summarizer import summarize

app = Flask(__name__)


@app.get("/")
def home():
    return (
        f"<html><head><title>{REGISTRATION} - News Summarizer</title></head><body>"
        f"<h1>Registration Number: {REGISTRATION}</h1>"
        f"<p>News source: {NEWS_SOURCE}</p>"
        f"<p>Try: <a href='/get?keyword=AI'>/get?keyword=AI</a></p>"
        f"</body></html>"
    )


@app.get("/get")
def get_news():
    keyword = (request.args.get("keyword") or "").strip()
    result = {
        "registration": REGISTRATION,
        "newssource": NEWS_SOURCE,
        "keyword": keyword,
        "url": "",
        "summary": "",
    }
    if not keyword:
        result["summary"] = "Please provide a keyword, e.g. /get?keyword=AI"
        return jsonify(result), 400
    try:
        url, title, text = fetch_first_result(keyword)
        result["url"] = url or ""
        result["summary"] = summarize(text) if text else (title or "No article found for this keyword.")
    except Exception as exc:
        result["summary"] = f"Error while scraping: {exc}"
        return jsonify(result), 500
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
