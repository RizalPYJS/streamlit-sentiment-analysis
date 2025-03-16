import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from io import BytesIO
import textwrap
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import praw

# Fungsi untuk mengambil berita dari Yahoo Finance
def get_news_yahoo(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker}/news?p={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_data = []
        
        articles = soup.find_all('article')
        
        for item in articles:
            headline = item.find('h3')
            link = item.find('a', href=True)
            
            if headline and link:
                title = headline.text.strip()
                news_link = f"https://finance.yahoo.com{link['href']}"
                news_data.append({'title': title, 'link': news_link, 'source': 'Yahoo Finance'})
        
        return news_data[:5] if news_data else []
    
    except Exception as e:
        return []

# Fungsi analisis sentimen
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Fungsi untuk mengambil data saham dari Alpha Vantage
def get_stock_data(ticker):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey=demo'
    response = requests.get(url)
    data = response.json()
    if 'Time Series (5min)' not in data:
        return None
    df = pd.DataFrame.from_dict(data['Time Series (5min)'], orient='index')
    df = df.astype(float)
    df = df.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'})
    return df

# Fungsi untuk mengambil indeks Fear & Greed
def get_fear_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    data = response.json()
    if 'data' in data:
        return data['data'][0]['value'], data['data'][0]['value_classification']
    return None, None

# Fungsi untuk mengambil harga crypto dari Binance
def get_crypto_price_binance(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    data = response.json()
    if 'price' in data:
        return float(data['price'])
    return None

# Fungsi untuk mengambil data dari Reddit
def get_reddit_sentiment(ticker):
    reddit = praw.Reddit(
        client_id='your_client_id',
        client_secret='your_client_secret',
        user_agent='your_user_agent'
    )
    
    subreddit = reddit.subreddit("stocks")
    posts = subreddit.search(ticker, limit=10)
    sentiment_scores = []
    reddit_data = []
    
    for post in posts:
        sentiment = analyze_sentiment(post.title)
        sentiment_scores.append(sentiment)
        reddit_data.append({'title': post.title, 'sentiment': sentiment})
    
    return pd.DataFrame(reddit_data)

st.set_page_config(page_title="Analisis Sentimen Saham & Crypto", layout="wide")
st.title("📈 Analisis Sentimen & Prediksi Saham & Crypto")
st.write("Masukkan kode aset untuk melihat analisis sentimen berita terbaru dan prediksi harga.")

asset_ticker = st.text_input("Masukkan kode aset (contoh: AAPL, BTCUSDT, ETHUSDT)", "AAPL").upper()

if st.button("🔍 Analisis Berita & Prediksi Harga"):
    yahoo_news = get_news_yahoo(asset_ticker)
    stock_data = get_stock_data(asset_ticker)
    crypto_price = get_crypto_price_binance(asset_ticker)
    fear_greed_value, fear_greed_label = get_fear_greed_index()
    reddit_sentiment = get_reddit_sentiment(asset_ticker)
    
    if not yahoo_news:
        st.warning(f"⚠ Tidak ada berita yang ditemukan untuk {asset_ticker}. Coba ticker lain.")
    else:
        sentiments = []
        for news in yahoo_news:
            sentiment_score = analyze_sentiment(news['title'])
            sentiments.append({'title': news['title'], 'sentiment': sentiment_score, 'link': news['link'], 'source': news['source']})
        
        df = pd.DataFrame(sentiments)
        
        st.subheader(f"📊 Hasil Analisis Sentimen Berita untuk {asset_ticker}")
        st.dataframe(df, width=1000, height=300)
        
        st.subheader("📉 Visualisasi Sentimen")
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['red' if s < -0.1 else 'green' if s > 0.1 else 'yellow' for s in df['sentiment']]
        wrapped_titles = [textwrap.fill(title, width=30) for title in df['title']]
        ax.barh(wrapped_titles, df['sentiment'], color=colors)
        ax.set_xlabel('Sentiment Score')
        ax.set_ylabel('News Headlines')
        ax.set_title(f'Sentiment Analysis of {asset_ticker} News')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        st.image(buf)
    
    if fear_greed_value is not None:
        st.subheader("🧠 Fear & Greed Index")
        st.write(f"Indeks saat ini: {fear_greed_value} - {fear_greed_label}")
    
    if stock_data is not None:
        st.subheader("📈 Data Harga Aset")
        st.line_chart(stock_data['close'])
    
    if crypto_price is not None:
        st.subheader("💰 Harga Crypto Saat Ini")
        st.write(f"Harga {asset_ticker}: ${crypto_price}")
    
    if not reddit_sentiment.empty:
        st.subheader("📢 Analisis Sentimen Reddit")
        st.dataframe(reddit_sentiment, width=1000, height=300)

st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode aset (misal: AAPL, BTCUSDT, ETHUSDT).")
st.sidebar.write("2️⃣ Klik tombol '🔍 Analisis Berita & Prediksi Harga'.")
st.sidebar.write("3️⃣ Lihat tabel berita, grafik sentimen, dan indeks Fear & Greed.")
