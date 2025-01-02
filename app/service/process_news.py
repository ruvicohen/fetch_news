import os
from dotenv import load_dotenv
from app.api.groq_api import classify_news_message, extract_location_details
from app.api.nwes_api import fetch_news
from app.kafka_settings.producer import produce
from app.service.location_service import get_coordinates

load_dotenv(verbose=True)

ELASTIC_TOPIC = os.environ["ELASTIC_TOPIC"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_FILE = "../assets/news.json"
FILE_PATH = os.path.join(BASE_DIR, NEWS_FILE)

CLASSIFICATION_MAP = {
    "1": "General News",
    "2": "Historical Terrorism Event",
    "3": "Current Terrorism Event",
}


def classify_news(body):
    classification_type = classify_news_message(body)[0]
    return CLASSIFICATION_MAP.get(classification_type, "General News")

def extract_location(news):
    return extract_location_details(news.get("title"), news.get("body"))

def get_news_coordinates(location_dict):
    if location_dict:
        return get_coordinates(location_dict["country"], location_dict["city"])
    return None

def create_news_dict(news, classification, location_dict, coords):
    return {
        "title": news["title"],
        "body": news["body"],
        "date": news["dateTime"],
        "classification": classification,
        "city": location_dict["city"],
        "country": location_dict["country"],
        "region": location_dict["region"],
        "latitude": coords[0],
        "longitude": coords[1],
    }

def process_single_news(news):
    classification = classify_news(news["body"])
    location_dict = extract_location(news)
    if not location_dict:
        return None

    coords = get_news_coordinates(location_dict)
    if not coords:
        return None

    return create_news_dict(news, classification, location_dict, coords)

def process_news_batch():
    results_news = fetch_news()
    batch = [process_single_news(news) for news in results_news.get("articles", {}).get("results", [])]
    filtered_batch = [news for news in batch if news]

    for i in range(0, len(filtered_batch), 100):
        produce(filtered_batch[i:i+10], "news", ELASTIC_TOPIC)