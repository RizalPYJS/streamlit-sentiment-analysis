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

# Fungsi untuk mengambil berita dari Google News
def get_news_google(ticker, api_key):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        
        news_list = response.json().get('articles', [])
        
        news_data = [{'title': news['title'], 'link': news['url'], 'source': 'Google News'} for news in news_list[:5]]
        
        return news_data
    except Exception as e:
        return []

# Fungsi analisis sentimen
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

st.set_page_config(page_title="Analisis Sentimen Saham & Crypto", layout="wide")
st.title("📈 Analisis Sentimen & Prediksi Saham & Crypto")
st.write("Masukkan kode aset untuk melihat analisis sentimen berita terbaru dan prediksi harga.")

asset_ticker = st.text_input("Masukkan kode aset (contoh: AAPL, BTCUSDT, ETHUSDT)", "AAPL").upper()
google_api_key = st.text_input("Masukkan API Key Google News", type="password")

if st.button("🔍 Analisis Berita & Prediksi Harga"):
    yahoo_news = get_news_yahoo(asset_ticker)
    google_news = get_news_google(asset_ticker, google_api_key) if google_api_key else []
    news_list = yahoo_news + google_news
    
    if not news_list:
        st.warning(f"⚠ Tidak ada berita yang ditemukan untuk {asset_ticker}. Coba ticker lain.")
    else:
        sentiments = []
        for news in news_list:
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

st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode aset (misal: AAPL, BTCUSDT, ETHUSDT).")
st.sidebar.write("2️⃣ Masukkan API Key Google News untuk data tambahan.")
st.sidebar.write("3️⃣ Klik tombol '🔍 Analisis Berita & Prediksi Harga'.")
st.sidebar.write("4️⃣ Lihat tabel berita dan grafik sentimen.")
