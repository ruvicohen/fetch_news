import json
import os
from app.api.groq_api import classify_news_message, extract_location_details
from app.kafka_settings.producer import produce
from app.service.location_service import get_coordinates
from dotenv import load_dotenv

load_dotenv(verbose=True)

elastic_topic = os.environ["ELASTIC_TOPIC"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file = "../assets/news.json"
file_path = os.path.join(BASE_DIR, file)
classify_news_message_dict = {"1": "General News", "2": "Historical Terrorism Event", "3": "Current Terrorism Event"}

def read_json(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data


def process_news():
    results_news = read_json(file_path)
    a = 0
    for news in results_news["articles"]["results"]:
        type = classify_news_message(news["body"])
        if type[0] == "1":
            classification = classify_news_message_dict["1"]
        elif type[0] == "2":
            classification = classify_news_message_dict["2"]
        elif type[0] == "3":
            classification = classify_news_message_dict["3"]
        else:
            classification = classify_news_message_dict["1"]
        location_dict = extract_location_details(news["title"], news["body"])
        if location_dict is None:
            continue
        city = location_dict["city"]
        country = location_dict["country"]
        region = location_dict["region"]
        coords = get_coordinates(country, city)
        print(coords)
        if coords is None or classification is None or city is None or country is None or region is None:
            continue
        news_dict = {
            "title": news["title"],
            "body": news["body"],
            "date": news["dateTime"],
            "classification": classification,
            "city": city,
            "country": country,
            "region": region,
            "latitude": coords[0],
            "longitude": coords[1]
        }
        batch = []
        batch.append(news_dict)
        if batch:
            produce(batch,"news", elastic_topic)
            batch = []

        a += 1
        print(a)

process_news()