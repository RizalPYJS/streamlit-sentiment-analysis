import os
from dotenv import load_dotenv
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Mengambil API key dari variabel lingkungan
CMC_API_KEY = os.getenv("CMC_API_KEY")

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

# Fungsi untuk mengambil berita dari Finviz
def get_news_finviz(ticker):
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find('table', class_='fullview-news-outer')
        if news_table is None:
            return []
        news_data = []
        rows = news_table.findAll('tr')
        for row in rows[:5]:
            a_tag = row.find('a')
            if a_tag:
                title = a_tag.text.strip()
                link = a_tag['href']
                news_data.append({'title': title, 'link': link, 'source': 'Finviz'})
        return news_data
    except Exception as e:
        return []

# Fungsi untuk mengambil berita dari IHSG (misal dari situs IDX)
def get_news_ihsg():
    url = "https://www.idx.co.id/id/berita-pasar"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
         response = requests.get(url, headers=headers)
         if response.status_code != 200:
              return []
         soup = BeautifulSoup(response.text, 'html.parser')
         news_data = []
         # Asumsi: setiap berita berada di dalam <div class="news-item">
         articles = soup.find_all("div", class_="news-item")
         for item in articles[:5]:
             a_tag = item.find("a")
             if a_tag:
                 title = a_tag.text.strip()
                 link = a_tag.get("href")
                 if link and not link.startswith("http"):
                     link = "https://www.idx.co.id" + link
                 news_data.append({"title": title, "link": link, "source": "IHSG"})
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

# Fungsi untuk mengambil data dari CoinMarketCap
def get_coinmarketcap_data(symbol, api_key):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        return None

# Fungsi analisis sentimen menggunakan TextBlob
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Set konfigurasi halaman Streamlit
st.set_page_config(page_title="Analisis Sentimen Saham & Crypto", layout="wide")
st.title("📈 Analisis Sentimen & Prediksi Saham & Crypto")
st.write("Masukkan kode aset untuk melihat analisis sentimen berita terbaru dan prediksi harga.")

# Input kode aset, termasuk opsi "IHSG" untuk indeks pasar Indonesia
asset_ticker = st.text_input("Masukkan kode aset (contoh: AAPL, BTCUSDT, ETHUSDT, IHSG)", "AAPL").upper()

if st.button("🔍 Analisis Berita & Prediksi Harga"):
    # Ambil berita dari sumber-sumber yang relevan
    yahoo_news = get_news_yahoo(asset_ticker)
    reuters_news = get_news_reuters(asset_ticker)
    finviz_news = get_news_finviz(asset_ticker)
    
    # Jika aset adalah IHSG, tambahkan scraping berita dari IDX
    if asset_ticker == "IHSG":
        ihsg_news = get_news_ihsg()
    else:
        ihsg_news = []
    
    # Gabungkan semua berita
    news_list = yahoo_news + reuters_news + finviz_news + ihsg_news
    
    if not news_list:
        st.warning(f"⚠ Tidak ada berita yang ditemukan untuk {asset_ticker}. Coba ticker lain.")
    else:
        # Analisis sentimen untuk setiap berita
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
        
        # Fungsi untuk mengkategorikan nilai sentimen
        def categorize_sentiment(score):
            if score > 0.1:
                return 'Positif'
            elif score < -0.1:
                return 'Negatif'
            else:
                return 'Netral'
        df['kategori'] = df['sentiment'].apply(categorize_sentiment)
        
        # Visualisasi distribusi sentimen dengan Pie Chart dan Bar Chart
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Distribusi Sentimen (Pie Chart)")
            pie_fig = px.pie(
                df, 
                names='kategori', 
                title="Distribusi Sentimen",
                color='kategori', 
                color_discrete_map={'Positif': 'green', 'Negatif': 'red', 'Netral': 'gray'}
            )
            st.plotly_chart(pie_fig, use_container_width=True)
            
        with col2:
            st.subheader("Distribusi Sentimen (Bar Chart)")
            bar_counts = df['kategori'].value_counts().reset_index()
            bar_counts.columns = ['kategori', 'jumlah']
            bar_fig = px.bar(
                bar_counts, 
                x='kategori', 
                y='jumlah', 
                text='jumlah', 
                title="Jumlah Berita per Kategori",
                color='kategori',
                color_discrete_map={'Positif': 'green', 'Negatif': 'red', 'Netral': 'gray'}
            )
            st.plotly_chart(bar_fig, use_container_width=True)
        
        # Histogram sebaran nilai sentimen dengan pengaturan ukuran chart
        st.subheader("Histogram Sebaran Nilai Sentimen")
        hist_fig = px.histogram(
            df, 
            x='sentiment', 
            nbins=10, 
            title="Sebaran Nilai Sentimen",
            color_discrete_sequence=['#636EFA']
        )
        hist_fig.update_layout(width=700, height=400)
        st.plotly_chart(hist_fig, use_container_width=False)
        
        # Jika aset adalah crypto (mengandung USDT), tampilkan harga dan grafik pergerakan harga
        if "USDT" in asset_ticker:
            # Data dari Binance
            price = get_crypto_price(asset_ticker)
            if price:
                st.subheader(f"💰 Harga (Binance) Saat Ini: {price} USD")
                
                # Simulasi data harga crypto selama 10 jam terakhir
                np.random.seed(42)
                base_price = float(price)
                fluctuations = np.random.uniform(-0.05, 0.05, 10)
                prices = [base_price * (1 + f) for f in fluctuations]
                timestamps = pd.date_range(end=pd.Timestamp.now(), periods=10, freq='H')
                df_prices = pd.DataFrame({'Waktu': timestamps, 'Harga': prices})
                
                st.subheader("📊 Grafik Pergerakan Harga Crypto (Binance)")
                line_fig = px.line(
                    df_prices, 
                    x='Waktu', 
                    y='Harga', 
                    title=f'Pergerakan Harga {asset_ticker} Selama 10 Jam Terakhir',
                    markers=True
                )
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
                candle_fig.update_layout(
                    title=f'Grafik Candlestick {asset_ticker} (Simulasi)',
                    xaxis_title="Waktu", 
                    yaxis_title="Harga (USD)"
                )
                st.plotly_chart(candle_fig, use_container_width=True)
            
            # Data dari CoinMarketCap
            symbol_cmc = asset_ticker.replace("USDT", "")
            cmc_data = get_coinmarketcap_data(symbol_cmc, CMC_API_KEY)
            if cmc_data and "data" in cmc_data and symbol_cmc in cmc_data["data"]:
                crypto_data = cmc_data["data"][symbol_cmc]
                quote = crypto_data["quote"]["USD"]
                price_cmc = quote["price"]
                market_cap = quote["market_cap"]
                percent_change_24h = quote["percent_change_24h"]
                st.subheader("📊 Data dari CoinMarketCap")
                st.write(f"**Harga:** ${price_cmc:,.2f}")
                st.write(f"**Market Cap:** ${market_cap:,.2f}")
                st.write(f"**Perubahan 24 Jam:** {percent_change_24h:.2f}%")
            else:
                st.warning("Gagal mengambil data dari CoinMarketCap. Pastikan ticker sudah benar.")

# Sidebar untuk petunjuk penggunaan
st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode aset (misal: AAPL, BTCUSDT, ETHUSDT, IHSG).")
st.sidebar.write("2️⃣ Klik tombol '🔍 Analisis Berita & Prediksi Harga'.")
st.sidebar.write("3️⃣ Lihat tabel berita, grafik sentimen, dan data harga (jika berlaku).")

col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.write("🔹 **By Muh Rizal Ardiyansah**")

with col2:
    linkedln_url = "https://www.linkedin.com/in/muh-rizal-ardiyansah-941464248/"
    st.markdown(f'<a href="{linkedln_url}" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="30"></a>', unsafe_allow_html=True)
