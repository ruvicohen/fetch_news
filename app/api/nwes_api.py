import os
import requests
from dotenv import load_dotenv

load_dotenv(verbose=True)

api_key = os.environ["NEWS_API_KEY"]

url = "https://eventregistry.org/api/v1/article/getArticles"
budy = {
    "action": "getArticles",
    "keyword": "terror attack",
    "ignoreSourceGroupUri": "paywall/paywalled_sources",
    "articlesPage": 1,
    "articlesCount": 100,
    "articlesSortBy": "socialScore",
    "articlesSortByAsc": False,
    "dataType": ["news", "pr"],
    "forceMaxDataTimeWindow": 31,
    "resultType": "articles",
    "apiKey": api_key,
}


def fetch_news():
    response = requests.post(url, json=budy)
    json_response = response.json()
    return json_response