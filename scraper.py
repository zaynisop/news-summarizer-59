"""Selenium + Chrome scraper: searches the assigned news site and reads the first result."""
import re
import time
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from config import ARTICLE_PATTERN, NEWS_DOMAIN, RESULT_SELECTOR, SEARCH_URL

BOILERPLATE = re.compile(r"cookie|subscribe to|newsletter|sign up|all rights reserved|javascript", re.I)


def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1366,900")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    )
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=opts)
    driver.set_page_load_timeout(45)
    return driver


def _first_article_link(driver, timeout=20):
    """Return the first link on the current page that looks like an article on the news site."""
    pattern = re.compile(ARTICLE_PATTERN)
    end = time.time() + timeout
    while time.time() < end:
        anchors = driver.find_elements(By.CSS_SELECTOR, RESULT_SELECTOR) or driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            try:
                href = a.get_attribute("href") or ""
                # skip site navigation / promo links that are not search results
                in_chrome = driver.execute_script(
                    "return !!arguments[0].closest('header, nav, footer, [role=navigation]')", a
                )
            except Exception:
                continue
            if NEWS_DOMAIN in href and pattern.search(href) and not in_chrome:
                return href.split("#")[0]
        time.sleep(1)
    return None


def _search_site(driver, keyword):
    driver.get(SEARCH_URL.format(q=quote_plus(keyword)))
    return _first_article_link(driver)


def _search_fallback(driver, keyword):
    # Used only if the site's own search page returns nothing (e.g. blocked or changed layout).
    driver.get(f"https://html.duckduckgo.com/html/?q={quote_plus(keyword + ' site:' + NEWS_DOMAIN)}")
    for a in driver.find_elements(By.CSS_SELECTOR, "a.result__a"):
        href = a.get_attribute("href") or ""
        if "uddg=" in href:
            href = unquote(parse_qs(urlparse(href).query).get("uddg", [""])[0])
        if NEWS_DOMAIN in href and re.search(ARTICLE_PATTERN, href):
            return href
    return None


def _article_text(driver, url):
    driver.get(url)
    time.sleep(3)
    paragraphs = []
    for selector in ("article p", "main p", "p"):
        paragraphs = [p.text.strip() for p in driver.find_elements(By.CSS_SELECTOR, selector)]
        paragraphs = [p for p in paragraphs if len(p.split()) > 8 and p.count("\n") < 3 and not BOILERPLATE.search(p)]
        if paragraphs:
            break
    title = driver.title or ""
    if not paragraphs:
        # e.g. landing / interactive pages: use the page's own description
        metas = driver.find_elements(By.CSS_SELECTOR, "meta[name='description'], meta[property='og:description']")
        paragraphs = [m.get_attribute("content") or "" for m in metas[:1]]
    return title, " ".join(paragraphs)


def fetch_first_result(keyword):
    """Return (url, title, text) for the first search result of `keyword`."""
    driver = make_driver()
    try:
        url = _search_site(driver, keyword) or _search_fallback(driver, keyword)
        if not url:
            return None, "", ""
        title, text = _article_text(driver, url)
        return url, title, text
    finally:
        driver.quit()
