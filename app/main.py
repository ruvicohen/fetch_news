from time import sleep

from app.service.process_news import process_news_batch

if __name__ == "__main__":
    while True:
        process_news_batch()
        sleep(120)