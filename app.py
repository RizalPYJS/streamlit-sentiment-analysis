import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_yahoo_finance_news():
    url = "https://finance.yahoo.com/topic/stock-market-news/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("h3", class_="Mb(5px)")
    news = [(a.text, "https://finance.yahoo.com" + a.a["href"]) for a in articles]
    return news

def get_cnbc_news():
    url = "https://www.cnbc.com/markets/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", class_="Card-title")
    news = [(a.text.strip(), a["href"]) for a in articles if a.text.strip()]
    return news

def get_marketwatch_news():
    url = "https://www.marketwatch.com/markets"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("h3", class_="article__headline")
    news = [(a.text.strip(), a.a["href"]) for a in articles if a.a]
    return news

def get_investing_news():
    url = "https://www.investing.com/news/stock-market-news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", class_="title")
    news = [(a.text.strip(), "https://www.investing.com" + a["href"]) for a in articles]
    return news

def main():
    yahoo_news = get_yahoo_finance_news()
    cnbc_news = get_cnbc_news()
    marketwatch_news = get_marketwatch_news()
    investing_news = get_investing_news()
    
    all_news = {
        "Yahoo Finance": yahoo_news,
        "CNBC": cnbc_news,
        "MarketWatch": marketwatch_news,
        "Investing.com": investing_news,
    }
    
    for source, news_list in all_news.items():
        print(f"\n{source} News:")
        for title, link in news_list[:5]:  # Print only top 5
            print(f"- {title} ({link})")

if __name__ == "__main__":
    main()
