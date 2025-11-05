import streamlit as st
import pandas as pd
import requests
import time
import altair as alt

# 🔹 Streamlit Page Setup
st.set_page_config(page_title="NSE Option Chain OI Dashboard",
                   layout="wide",
                   page_icon="📊")

st.title("📊 NIFTY Option Chain – CE & PE OI Summary")

# 🔹 Fetch NSE Option Chain data
@st.cache_data(ttl=60)
def get_option_data(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    r = session.get(url, headers=headers)
    return r.json()

try:
    data = get_option_data()
except Exception as e:
    st.error(f"⚠️ Failed to fetch NSE data: {e}")
    st.stop()

# 🔹 Parse CE & PE data
records = []
for item in data["records"]["data"]:
    ce = item.get("CE")
    pe = item.get("PE")
    strike = item.get("strikePrice")
    if ce and pe:
        records.append({
            "Strike Price": strike,
            "CE OI": ce["openInterest"],
            "CE OI Change": ce["changeinOpenInterest"],
            "PE OI": pe["openInterest"],
            "PE OI Change": pe["changeinOpenInterest"]
        })

df = pd.DataFrame(records).sort_values("Strike Price").reset_index(drop=True)

# 🔹 Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total CE OI", f"{df['CE OI'].sum():,}")
col2.metric("Total CE OI Change", f"{df['CE OI Change'].sum():,}")
col3.metric("Total PE OI", f"{df['PE OI'].sum():,}")
col4.metric("Total PE OI Change", f"{df['PE OI Change'].sum():,}")

# 🔹 Chart
st.subheader("📈 Open Interest Comparison by Strike")
chart_df = df.melt(id_vars="Strike Price",
                   value_vars=["CE OI", "PE OI"],
                   var_name="Type",
                   value_name="OI")
chart = (
    alt.Chart(chart_df)
    .mark_bar()
    .encode(
        x=alt.X("Strike Price:O", sort=None),
        y="OI:Q",
        color="Type:N",
        tooltip=["Strike Price", "Type", "OI"]
    )
    .properties(height=400)
)
st.altair_chart(chart, use_container_width=True)

# 🔹 Table
st.subheader("🔹 Detailed Option Data")
st.dataframe(df.style.highlight_max(axis=0, color="lightgreen"))

# 🔹 Auto-refresh every 60 s
st.info("Auto-refreshing every 60 seconds...")
time.sleep(60)
st.experimental_rerun()
