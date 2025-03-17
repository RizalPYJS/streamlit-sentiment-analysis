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


load_dotenv()

def get_news_google(ticker):
    url = f'https://news.google.com/rss/search?q={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'xml')  # Parsing XML untuk RSS feed
        news_data = []
        items = soup.find_all('item')
        
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            news_data.append({'title': title, 'link': link, 'source': 'Google News'})
        
        return news_data[:20] if news_data else []  # Ambil 20 berita terbaru
    
    except Exception:
        return []


def get_news_api(ticker):
    
    api_key = os.getenv('NEWSAPI_KEY')
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        data = response.json()
        articles = data['articles']
        news_data = []
        
        for article in articles:
            title = article['title']
            link = article['url']
            news_data.append({'title': title, 'link': link, 'source': article['source']['name']})
        
        return news_data[:20] if news_data else []  # Ambil 20 berita terbaru
    except Exception as e:
        return []


def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity


st.set_page_config(page_title="Analisis Sentimen Saham & Crypto", layout="wide")
st.title("📈 Analisis Sentimen Saham & Crypto")
st.write("Masukkan kode aset untuk melihat analisis sentimen berita terbaru dan prediksi harga.")

asset_ticker = st.text_input("Masukkan kode aset (contoh: AAPL, BTC, ETH)", "AAPL").upper()


news_source = st.selectbox("Pilih sumber berita", ("Google News", "NewsAPI"))

if st.button("🔍 Analisis Berita Saham"):
    if news_source == "Google News":
        yahoo_news = get_news_google(asset_ticker)
    elif news_source == "NewsAPI":
        yahoo_news = get_news_api(asset_ticker)
    else:
        yahoo_news = []

    news_list = yahoo_news 
    
    if not news_list:
        st.warning(f"⚠ Tidak ada berita yang ditemukan untuk {asset_ticker}. Coba ticker lain.")
    else:
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
        
        def categorize_sentiment(score):
            if score > 0.1:
                return 'Positif'
            elif score < -0.1:
                return 'Negatif'
            else:
                return 'Netral'
        
        df['kategori'] = df['sentiment'].apply(categorize_sentiment)
        
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


st.sidebar.header("ℹ️ Petunjuk Penggunaan")
st.sidebar.write("1️⃣ Masukkan kode aset (misal: AAPL, TSLA, BTC).")
st.sidebar.write("2️⃣ Klik tombol '🔍 Analisis Berita Saham'.")
st.sidebar.write("3️⃣ Lihat tabel berita, grafik sentimen, dan data harga (jika berlaku).")
st.sidebar.write("Data Dari IHSG & Crypto masih sangat terbatas dikarenakan terbatas API")
col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.write("🔹 **By Muh Rizal Ardiyansah**")

with col2:
    linkedln_url = "https://www.linkedin.com/in/muh-rizal-ardiyansah-941464248/"
    st.markdown(
        f'<a href="{linkedln_url}" target="_blank">'
        f'<img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="30"></a>',
        unsafe_allow_html=True
    )
