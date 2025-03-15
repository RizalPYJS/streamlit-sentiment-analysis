# Analisis Sentimen Berita Saham - GitHub Codespaces Version

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from io import BytesIO
import textwrap

# Fungsi untuk mengambil berita dari Yahoo Finance
def get_news(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker}/news?p={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_data = []
        
        articles = soup.find_all('article')  # Mencari elemen berita
        
        for item in articles:
            headline = item.find('h3')  # Judul berita ada dalam elemen <h3>
            link = item.find('a', href=True)  # Ambil link berita
            
            if headline and link:
                title = headline.text.strip()
                news_link = f"https://finance.yahoo.com{link['href']}"
                news_data.append({'title': title, 'link': news_link})
        
        return news_data[:5] if news_data else []
    
    except Exception as e:
        return []

# Fungsi analisis sentimen
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity  # Skor antara -1 (negatif) dan 1 (positif)

# Streamlit UI
st.set_page_config(page_title="Analisis Sentimen Saham", layout="wide")
st.title("📈 Analisis Sentimen Berita Saham")
st.write("Masukkan kode saham untuk melihat analisis sentimen berita terbaru.")

stock_ticker = st.text_input("Masukkan kode saham (contoh: AAPL, TSLA, GOTO.JK)", "AAPL").upper()

if st.button("🔍 Analisis Berita"):
    news_list = get_news(stock_ticker)
    
    if not news_list:
        st.warning(f"⚠ Tidak ada berita yang ditemukan untuk {stock_ticker}. Coba ticker lain.")
    else:
        sentiments = []
        for news in news_list:
            sentiment_score = analyze_sentiment(news['title'])
            sentiments.append({'title': news['title'], 'sentiment': sentiment_score, 'link': news['link']})
        
        df = pd.DataFrame(sentiments)
        
        # Tampilkan hasil dalam tabel interaktif
        st.subheader(f"📊 Hasil Analisis Sentimen Berita untuk {stock_ticker}")
        st.dataframe(df, width=1000, height=300)
        
        # Plot hasil analisis sentimen dengan perbaikan tampilan teks
        st.subheader("📉 Visualisasi Sentimen")
        fig, ax = plt.subplots(figsize=(12, 6))  # Lebarkan ukuran gambar
        colors = ['red' if s < -0.1 else 'green' if s > 0.1 else 'yellow' for s in df['sentiment']]
        
        # Membungkus teks agar lebih rapi
        wrapped_titles = [textwrap.fill(title, width=30) for title in df['title']]
        ax.barh(wrapped_titles, df['sentiment'], color=colors)
        ax.set_xlabel('Sentiment Score')
        ax.set_ylabel('News Headlines')
        ax.set_title(f'Sentiment Analysis of {stock_ticker} News')

        plt.tight_layout()  # Supaya layout lebih rapi
        
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        st.image(buf)

# Petunjuk Penggunaan
st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode saham (misal: AAPL, TSLA, GOTO.JK).")
st.sidebar.write("2️⃣ Klik tombol '🔍 Analisis Berita'.")
st.sidebar.write("3️⃣ Lihat tabel berita dan grafik sentimen.")
st.sidebar.write("4️⃣ Klik tautan berita untuk membaca lebih lanjut.")

# Menampilkan Kredit dan LinkedIn
st.markdown("---")  # Garis pemisah
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.write("🔹 **By Muh Rizal Ardiyansah**")

with col2:
    linkedln_url = "https://www.linkedin.com/in/muh-rizal-ardiyansah-941464248/"
    st.markdown(f'<a href="{linkedln_url}" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="30"></a>', unsafe_allow_html=True)
