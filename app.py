import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

# Bitquery API Endpoint & Headers
BITQUERY_API_URL = "https://graphql.bitquery.io"
BITQUERY_API_KEY = "ory_at_DY2ftywKkVB0t5OisZvkZN0PjLZbhjDHzyatDWZsKX0.Xi2BuhFQDeWSRqjRIMoSJNLkspqVUX3Er0tDZoGHZFU"


# Query Bitquery untuk mendapatkan token Pump Fun teratas
def get_pumpfun_tokens():
    query = """
    {
      solana {
        dexTrades(
          options: {desc: "tradeAmount", limit: 10}
          exchangeName: {is: "Pump Fun"}
        ) {
          baseCurrency {
            symbol
            name
          }
          tradeAmount(in: USD)
          buyAmount(in: USD)
          sellAmount(in: USD)
        }
      }
    }
    """
    headers = {"X-API-KEY": BITQUERY_API_KEY, "Content-Type": "application/json"}
    response = requests.post(BITQUERY_API_URL, json={"query": query}, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]["solana"]["dexTrades"]
    else:
        return []

# Streamlit UI
st.set_page_config(page_title="Analisis Pump Fun", layout="wide")
st.title("📈 Analisis Pump Fun Token")
st.write("Lihat data real-time mengenai token Pump Fun dari Bitquery API.")

# Tombol untuk mengambil data
if st.button("🔍 Ambil Data Pump Fun"):
    token_data = get_pumpfun_tokens()
    if not token_data:
        st.warning("⚠ Tidak ada data yang ditemukan. Coba lagi nanti.")
    else:
        df = pd.DataFrame(token_data)
        st.subheader("📊 Token Pump Fun Teratas")
        st.dataframe(df, width=1000, height=300)

# Petunjuk Penggunaan
st.sidebar.header("ℹ️ Petunjuk Penggunaan")
        st.warning("⚠ Tidak ada data yang ditemukan. Coba lagi nanti.")
    else:
        df = pd.DataFrame(token_data)
        st.subheader("📊 Token Pump Fun Teratas")
