import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(verbose=True)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def classify_news_message(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Classify the following news message into one of the following categories:
                    1. General News
                    2. Historical Terrorism Event
                    3. Current Terrorism Event

                    News Message:
                    "{message}"

                    Provide only the category number (1, 2, or 3) as the response without text'.
                    """,
                }
            ],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content
        return response

    except Exception as e:
        print(f"Error during classification: {e}")
        return None


def validate_location_details(location_details):
    required_keys = {"city", "country", "region"}
    if not isinstance(location_details, dict):
        return False

    if not required_keys.issubset(location_details.keys()):
        return False

    for key in required_keys:
        value = location_details[key]
        if value not in ["null"] and not isinstance(value, str):
            return False

    return True


def extract_location_details(title, content):
    clean_title = title.replace("\\", "")
    clean_content = content.replace("\\", "") if content else ""
    prompt = f"""
                Extract the location details (City, Country, Region) from the following news article.
                If no specific city, country, or region is mentioned, return None for the missing fields.
                Respond in this exact JSON format:
                {{
                    "city": ["city" or "null"],
                    "country": ["country" or "null"],
                     "region": ["region" or "null"]
                }}
                only one result for each and no additional comments at all
                and please dont use None!!
                

                News Message:
                "{clean_title, clean_content}"
                """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content
        location_details = json.loads(response)

        if validate_location_details(location_details):
            return location_details
        else:
            print(f"Invalid location details: {location_details}")
            return None

    except Exception as e:
        print(f"Error during location extraction: {e}")
        return None
