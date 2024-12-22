import os

from geopy.geocoders import Nominatim
import groq
import json
from typing import List, Dict, Any, Optional
import requests
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(verbose=True)

def compose_news_request() -> Dict[str, Any]:
    return {
        "action": "getArticles",
        "keyword": "terror attack",
        "articlesPage": 1,
        "articlesCount": 5,
        "articlesSortBy": "socialScore",
        "articlesSortByAsc": False,
        "dataType": ["news"],
        "apiKey": os.environ.get("GROQ_API_KEY")
    }


# יצירת חיבורים
groq_client = groq.Client(api_key=os.environ.get("GROQ_API_KEY"))
geolocator = Nominatim(user_agent="terror_analysis")


def fetch_news() -> List[Dict[str, Any]]:
    """משיכת חדשות מ-NewsAPI"""
    url = "https://eventregistry.org/api/v1/article/getArticles"

    body = {
        "action": "getArticles",
        "keyword": "terror attack",
        "articlesPage": 1,
        "articlesCount": 1,
        "articlesSortBy": "socialScore",
        "articlesSortByAsc": False,
        "dataType": ["news"],
        "apiKey": Config.NEWS_API_KEY
    }

    try:
        response = requests.post(url, json=body)
        # נדפיס את קוד התגובה והתוכן
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text[:500]}")  # מדפיס רק 500 תווים ראשונים

        response.raise_for_status()  # מעלה שגיאה אם הסטטוס קוד לא תקין

        data = response.json()
        return data.get('articles', {}).get('results', [])

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

@lru_cache(maxsize=1000)
def get_coordinates(location: str) -> Optional[Coordinates]:
    """המרת שם מיקום לקואורדינטות"""
    try:
        result = geolocator.geocode(location)
        if result:
            return Coordinates(
                latitude=result.latitude,
                longitude=result.longitude
            )
        return None
    except Exception as e:
        print(f"Error getting coordinates for {location}: {e}")
        return None


def classify_news(title: str, content: str) -> Optional[NewsClassification]:
    # ניקוי הטקסט מתווים מיוחדים
    clean_title = title.replace('\\', '')
    clean_content = content.replace('\\', '') if content else ''

    prompt = f"""
    Classify this news article into one category:
    Choose exactly one of: terror_event, historic_terror, general_news

    Title: {clean_title}
    Content: {clean_content}

    Respond in this exact JSON format:
    {{
        "category": "terror_event",
        "location": "city, country",
        "confidence": 0.9
    }}
    """

    try:
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=200
        )

        result = json.loads(completion.choices[0].message.content.strip())

        # וידוא שהקטגוריה חוקית
        if result["category"] not in [cat.value for cat in NewsCategory]:
            print(f"Invalid category received: {result['category']}")
            result["category"] = "general_news"  # ברירת מחדל

        coords = get_coordinates(result["location"])

        return NewsClassification(
            category=NewsCategory(result["category"]),
            location=result["location"],
            confidence=float(result["confidence"]),
            coordinates=coords
        )

    except Exception as e:
        print(f"Classification error: {str(e)}")
        # במקרה של שגיאה, נחזיר None במקום לזרוק שגיאה
        return None


def save_to_elasticsearch(article: Dict[str, Any], classification: NewsClassification):
    """שמירת המידע ב-Elasticsearch"""
    print("Saving article:", article)  # debug print
    print("Classification:", classification)  # debug print

    doc = {
        "title": article.get("title"),
        "content": article.get("body"),  # השינוי מ-content ל-body
        "publication_date": article.get("dateTime"),
        "category": classification.category.value,
        "location": classification.location,
        "confidence": classification.confidence,
        "source_url": article.get("url"),
    }

    if classification.coordinates:
        doc["coordinates"] = {
            "lat": classification.coordinates.latitude,
            "lon": classification.coordinates.longitude
        }

    try:
        elastic_client.index(index=Config.ES_INDEX_FOR_NEWS, document=doc)
        print(f"Successfully saved article: {article.get('title')[:50]}...")
    except Exception as e:
        print(f"Error in save_to_elasticsearch: {str(e)}")
        print(f"Document attempted to save: {doc}")

def process_news():
    """פונקציה ראשית לעיבוד החדשות"""
    articles = fetch_news()

    for article in articles:
        try:
            # בדיקה שיש לנו את כל השדות הנדרשים
            if not article.get("title") or not article.get("body"):
                continue

            classification = classify_news(
                article.get("title", ""),
                article.get("body", "")
            )

            if classification:
                try:
                    save_to_elasticsearch(article, classification)
                    print(f"Saved article: {article.get('title')[:50]}...")
                except Exception as e:
                    print(f"Error saving to elasticsearch: {e}")

        except Exception as e:
            print(f"Error processing article: {e}")
            continue