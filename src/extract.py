import os
from dotenv import load_dotenv
import requests
import json
from pathlib import Path
import time

BASE_URL = "https://api.nytimes.com/svc/books/v3/lists/overview.json"
RAW_DIR = Path("data/raw")

def get_api_key():
    """Load the NYT API key from the .env file."""
    load_dotenv()
    key = os.getenv("NYT_API_KEY")
    if not key:
        raise EnvironmentError("No API Key found. Add NYT_API_KEY in the .env file.")
    return key

def fetch_week(published_date=None):
    """Fetch the bestseller lists from the API for a given date. 
    If no date is given, it fetches the latest bestsellers lists.
    Args: the published date of the wanted bestseller lists, in YYYY-MM-DD format
    Returns: the data gotten from the API
    Raises: HTTPError if the request failed
    """
    key = get_api_key()
    resp = requests.get(BASE_URL, params={"api-key": key, "published_date": published_date}, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data

def raw_path(published_date):
    """Build the raw path for saving the data.
    Args: the published date of the data
    Returns: the path
    """
    return RAW_DIR / f"lists_{published_date}.json"

def save_raw(payload):
    """Saves the data to local files.
    Args: the data as payload
    Returns: the path where the data was saved
    """
    published_date = payload["results"]["published_date"]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = raw_path(published_date)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path

def main():
    data = fetch_week()
    published_date = data['results']['published_date']
    print(f"fetched latest bestsellers lists (published date: {published_date})")

    path = save_raw(data)
    print(f"saved {path} to disk")

    current_week = data["results"]["previous_published_date"]

    for _ in range(4):

        path = raw_path(current_week)

        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
                print(f"loaded {path} from disk")
        else:
            time.sleep(12)

            data = fetch_week(current_week)
            print(f"fetched bestsellers lists from {current_week}")

            path = save_raw(data)
            print(f"saved {path} to disk")

        current_week = data["results"]["previous_published_date"]


if __name__ == "__main__":
    main()