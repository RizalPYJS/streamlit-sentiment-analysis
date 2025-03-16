import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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

# Set konfigurasi halaman Streamlit
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
        # Analisis sentimen setiap judul berita
        sentiments = []
        for news in news_list:
            sentiment_score = analyze_sentiment(news['title'])
            sentiments.append({
                'title': news['title'],
                'sentiment': sentiment_score,
                'link': news['link'],
                'source': news['source']
            })
        df = pd.DataFrame(sentiments)
        
        st.subheader(f"📊 Hasil Analisis Sentimen Berita untuk {asset_ticker}")
        st.dataframe(df, width=1000, height=300)
        
        # Klasifikasi sentimen ke dalam kategori
        def categorize_sentiment(score):
            if score > 0.1:
                return 'Positif'
            elif score < -0.1:
                return 'Negatif'
            else:
                return 'Netral'
        df['kategori'] = df['sentiment'].apply(categorize_sentiment)
        
        # Menampilkan grafik distribusi sentimen dengan layout kolom
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Distribusi Sentimen (Pie Chart)")
            pie_fig = px.pie(df, names='kategori', title="Distribusi Sentimen",
                             color='kategori', 
                             color_discrete_map={'Positif':'green','Negatif':'red','Netral':'gray'})
            st.plotly_chart(pie_fig, use_container_width=True)
            
        with col2:
            st.subheader("Distribusi Sentimen (Bar Chart)")
            bar_counts = df['kategori'].value_counts().reset_index()
            bar_counts.columns = ['kategori', 'jumlah']
            bar_fig = px.bar(bar_counts, x='kategori', y='jumlah', text='jumlah', title="Jumlah Berita per Kategori",
                             color='kategori',
                             color_discrete_map={'Positif':'green','Negatif':'red','Netral':'gray'})
            st.plotly_chart(bar_fig, use_container_width=True)
        
        # Histogram sebaran nilai sentimen
        st.subheader("Histogram Sebaran Nilai Sentimen")
        hist_fig = px.histogram(df, x='sentiment', nbins=10, title="Sebaran Nilai Sentimen", color_discrete_sequence=['#636EFA'])
        st.plotly_chart(hist_fig, use_container_width=True)
        
        # Jika aset crypto (mengandung USDT), tampilkan informasi harga
        if "USDT" in asset_ticker:
            price = get_crypto_price(asset_ticker)
            if price:
                st.subheader(f"💰 Harga Saat Ini: {price} USD")
                
                # Simulasi data harga crypto selama 10 jam terakhir
                np.random.seed(42)
                base_price = float(price)
                fluctuations = np.random.uniform(-0.05, 0.05, 10)
                prices = [base_price * (1 + f) for f in fluctuations]
                timestamps = pd.date_range(end=pd.Timestamp.now(), periods=10, freq='H')
                df_prices = pd.DataFrame({'Waktu': timestamps, 'Harga': prices})
                
                st.subheader("📊 Grafik Pergerakan Harga Crypto")
                line_fig = px.line(df_prices, x='Waktu', y='Harga', title=f'Pergerakan Harga {asset_ticker} Selama 10 Jam Terakhir', markers=True)
                line_fig.update_layout(xaxis_title="Waktu", yaxis_title="Harga (USD)")
                st.plotly_chart(line_fig, use_container_width=True)
                
                # Simulasi data OHLC untuk grafik candlestick
                ohlc_data = []
                for i in range(len(df_prices)):
                    open_price = df_prices['Harga'].iloc[i] * np.random.uniform(0.98, 1.02)
                    high_price = open_price * np.random.uniform(1.00, 1.05)
                    low_price = open_price * np.random.uniform(0.95, 1.00)
                    close_price = df_prices['Harga'].iloc[i]
                    ohlc_data.append({
                        'Waktu': df_prices['Waktu'].iloc[i],
                        'Open': open_price,
                        'High': high_price,
                        'Low': low_price,
                        'Close': close_price
                    })
                df_ohlc = pd.DataFrame(ohlc_data)
                candle_fig = go.Figure(data=[go.Candlestick(
                    x=df_ohlc['Waktu'],
                    open=df_ohlc['Open'],
                    high=df_ohlc['High'],
                    low=df_ohlc['Low'],
                    close=df_ohlc['Close']
                )])
                candle_fig.update_layout(title=f'Grafik Candlestick {asset_ticker} (Simulasi)',
                                         xaxis_title="Waktu", yaxis_title="Harga (USD)")
                st.plotly_chart(candle_fig, use_container_width=True)

st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode aset (misal: AAPL, BTCUSDT, ETHUSDT).")
st.sidebar.write("2️⃣ Klik tombol '🔍 Analisis Berita & Prediksi Harga'.")
st.sidebar.write("3️⃣ Lihat tabel berita, grafik sentimen, dan harga crypto.")
