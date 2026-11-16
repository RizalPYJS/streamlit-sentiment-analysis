# Streamlit Sentiment Analysis

Saya membuat aplikasi Streamlit untuk menganalisis sentimen berita saham dan kripto berdasarkan kode aset. Berita diambil dari NewsAPI, lalu judulnya dianalisis dengan TextBlob dan ditampilkan dalam tabel serta grafik interaktif.

## Fitur
- Cari berita berdasarkan ticker, seperti `AAPL`, `BTC`, atau `ETH`.
- Kelompokkan sentimen menjadi positif, netral, dan negatif.
- Lihat distribusi sentimen melalui grafik Plotly.

## Menjalankan
```bash
pip install -r requirements.txt
streamlit run app.py
