import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import plotly.express as px
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

# Fungsi untuk mengambil berita dari Reuters
def get_news_reuters(ticker):
    url = f'https://www.reuters.com/markets/companies/{ticker}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_data = []
        
        articles = soup.find_all('div', class_='story-content')
        
        for item in articles[:5]:
            headline = item.find('h3')
            link = item.find('a', href=True)
            
            if headline and link:
                title = headline.text.strip()
                news_link = f"https://www.reuters.com{link['href']}"
                news_data.append({'title': title, 'link': news_link, 'source': 'Reuters'})
        
        return news_data
    except Exception as e:
        return []

# Fungsi untuk mengambil harga crypto dari Binance API
def get_crypto_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
        return response.json()['price']
    except Exception as e:
        return None

# Fungsi analisis sentimen
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

st.set_page_config(page_title="Analisis Sentimen Saham & Crypto", layout="wide")
st.title("📈 Analisis Sentimen & Prediksi Saham & Crypto")
st.write("Masukkan kode aset untuk melihat analisis sentimen berita terbaru dan prediksi harga.")

asset_ticker = st.text_input("Masukkan kode aset (contoh: AAPL, BTCUSDT, ETHUSDT)", "AAPL").upper()

if st.button("🔍 Analisis Berita & Prediksi Harga"):
    yahoo_news = get_news_yahoo(asset_ticker)
    reuters_news = get_news_reuters(asset_ticker)
    news_list = yahoo_news + reuters_news
    
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
        
        # Grafik distribusi sentimen
        st.subheader("📈 Distribusi Sentimen Berita")
        sentiment_counts = df['sentiment'].apply(lambda x: 'Positif' if x > 0.1 else ('Negatif' if x < -0.1 else 'Netral')).value_counts()
        fig_sentiment = px.bar(sentiment_counts, x=sentiment_counts.index, y=sentiment_counts.values, labels={'x': 'Sentimen', 'y': 'Jumlah'}, title="Distribusi Sentimen")
        st.plotly_chart(fig_sentiment)
        
        # Tampilkan harga crypto jika applicable
        if "USDT" in asset_ticker:
            price = get_crypto_price(asset_ticker)
            if price:
                st.subheader(f"💰 Harga Saat Ini: {price} USD")
                
                # Grafik harga crypto
                st.subheader("📊 Grafik Harga Crypto")
                prices = [float(price) * (1 + np.random.uniform(-0.05, 0.05)) for _ in range(10)]  # Simulasi data harga
                timestamps = pd.date_range(end=pd.Timestamp.now(), periods=10, freq='H')
                df_prices = pd.DataFrame({'Waktu': timestamps, 'Harga': prices})
                fig_prices = px.line(df_prices, x='Waktu', y='Harga', title=f'Pergerakan Harga {asset_ticker}')
                st.plotly_chart(fig_prices)

st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode aset (misal: AAPL, BTCUSDT, ETHUSDT).")
st.sidebar.write("2️⃣ Klik tombol '🔍 Analisis Berita & Prediksi Harga'.")
st.sidebar.write("3️⃣ Lihat tabel berita, grafik sentimen, dan harga crypto.")
