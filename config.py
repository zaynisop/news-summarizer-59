import os

# Roll No. 59 -> 59 % 20 + 1 = 20 -> MIT Technology Review
REGISTRATION = os.getenv("REGISTRATION", "FA23-BCT-059")
NEWS_SOURCE = "MIT Technology Review"
NEWS_DOMAIN = "technologyreview.com"
SEARCH_URL = "https://www.technologyreview.com/search/?s={q}"
# Links inside the search-result list (titles of result teasers)
RESULT_SELECTOR = "[class*='teaserItem__title'] a"
# Article URLs look like /2024/05/14/1092407/some-slug/
ARTICLE_PATTERN = r"technologyreview\.com/\d{4}/\d{2}/\d{2}/\d+/"
