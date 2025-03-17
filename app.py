import os
from dotenv import load_dotenv
import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()


def get_news_api(ticker, api_key):
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

# Fungsi untuk analisis sentimen menggunakan TextBlob
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Fungsi untuk memberikan respons chatbot berdasarkan sentimen
def sentiment_response(sentiment):
    if sentiment > 0.1:
        return "🎉 Sentimen positif! Berita ini menunjukkan bahwa banyak orang merasa optimis tentang perkembangan terbaru. Bisa jadi ini pertanda baik untuk aset tersebut!"
    elif sentiment < -0.1:
        return "⚠️ Sentimen negatif. Banyak orang merasa khawatir atau pesimis tentang perkembangan terbaru. Anda mungkin ingin lebih berhati-hati sebelum membuat keputusan."
    else:
        return "🤔 Sentimen netral. Berita ini cenderung obyektif, tanpa ada pengaruh besar baik dari sisi positif maupun negatif. Tidak ada perubahan signifikan yang dapat diharapkan."


def categorize_sentiment(score):
    if score > 0.1:
        return 'Positif'
    elif score < -0.1:
        return 'Negatif'
    else:
        return 'Netral'


st.set_page_config(page_title="Analisis Sentimen Saham & Crypto", layout="wide")
st.title("📈 Analisis Sentimen Saham & Crypto")
st.write("Masukkan kode aset untuk melihat analisis sentimen berita terbaru dan prediksi harga.")

asset_ticker = st.text_input("Masukkan kode aset (contoh: AAPL, BTC, ETH)", "AAPL").upper()


api_key = "e18b99df0d9c40098f96f149e3cab8b2"

if st.button("🔍 Analisis Berita Saham"):
    yahoo_news = get_news_api(asset_ticker, api_key)
    
    news_list = yahoo_news 
    
    if not news_list:
        st.warning(f"⚠ Tidak ada berita yang ditemukan untuk {asset_ticker}. Coba ticker lain.")
    else:
        sentiments = []
        for news in news_list:
            sentiment_score = analyze_sentiment(news['title'])
            sentiment_explanation = sentiment_response(sentiment_score)
            sentiments.append({
                'title': news['title'],
                'sentiment': sentiment_score,
                'link': news['link'],
                'source': news['source'],
                'sentiment_explanation': sentiment_explanation  # Menambahkan penjelasan dari chatbot
            })
        
        df = pd.DataFrame(sentiments)
        
        
        average_sentiment = df['sentiment'].mean()
        
       
        overall_sentiment = categorize_sentiment(average_sentiment)
        
        
        backend_text = f"Data berita dan analisis sentimen telah diproses. Rata-rata sentimen: {average_sentiment}, Kategori: {overall_sentiment}"
        st.text(backend_text)  
        
        st.subheader(f"📊 Hasil Analisis Sentimen Berita untuk {asset_ticker}")
        st.dataframe(df, width=1000, height=300)
        
        st.subheader("Distribusi Sentimen untuk Semua Berita")
        st.write(f"**Sentimen Keseluruhan**: {overall_sentiment}")
        st.write(sentiment_response(average_sentiment))

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

        
        st.write(f"**Sentimen Keseluruhan**: {overall_sentiment}")
        st.write(f"**Penjelasan Chatbot:** {sentiment_response(average_sentiment)}")

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
