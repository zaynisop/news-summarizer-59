"""Selenium + Chrome scraper: searches the assigned news site and reads the first result."""
import re
import time
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from config import ARTICLE_PATTERN, NEWS_DOMAIN, RESULT_SELECTOR, SEARCH_URL

BOILERPLATE = re.compile(
    r"cookie|consent|partner|subscribe to|newsletter|sign up|all rights reserved|javascript|advertisement",
    re.I,
)


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
    # Don't wait for ads/trackers to finish loading; the HTML content is ready much earlier.
    opts.page_load_strategy = "eager"
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=opts)
    driver.set_page_load_timeout(25)
    return driver


def _open(driver, url):
    """Load a page; if it is still loading after the timeout, stop it and use what is there."""
    try:
        driver.get(url)
    except TimeoutException:
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass


def _is_article(href):
    return urlparse(href).netloc in (NEWS_DOMAIN, "www." + NEWS_DOMAIN) and re.search(ARTICLE_PATTERN, href)


def _first_article_link(driver, timeout=15):
    """Return the first link in the site's search-result list that is an article."""
    end = time.time() + timeout
    while time.time() < end:
        for a in driver.find_elements(By.CSS_SELECTOR, RESULT_SELECTOR):
            try:
                href = a.get_attribute("href") or ""
            except Exception:
                continue
            if _is_article(href):
                return href.split("#")[0]
        time.sleep(1)
    return None


def _search_site(driver, keyword):
    _open(driver, SEARCH_URL.format(q=quote_plus(keyword)))
    return _first_article_link(driver)


def _search_fallback(driver, keyword):
    # Used only if the site's own search page returns nothing (e.g. blocked or changed layout).
    _open(driver, f"https://html.duckduckgo.com/html/?q={quote_plus(keyword + ' site:' + NEWS_DOMAIN)}")
    for a in driver.find_elements(By.CSS_SELECTOR, "a.result__a"):
        href = a.get_attribute("href") or ""
        if "uddg=" in href:
            href = unquote(parse_qs(urlparse(href).query).get("uddg", [""])[0])
        if _is_article(href):
            return href
    return None


def _article_text(driver, url):
    _open(driver, url)
    time.sleep(3)
    paragraphs = []
    for selector in ("article p", "main p", "p"):
        # textContent also covers paragraphs the site hides with CSS (e.g. metered articles)
        paragraphs = [" ".join((p.get_attribute("textContent") or "").split())
                      for p in driver.find_elements(By.CSS_SELECTOR, selector)]
        paragraphs = [p for p in paragraphs if len(p.split()) > 8 and not BOILERPLATE.search(p)]
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
