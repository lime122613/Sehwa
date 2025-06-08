
# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# GitHub Raw CSV URL
GITHUB_CSV_URL = "https://raw.githubusercontent.com/ZackWoo05/Sehwa/bd11b2729ca1334f903808f24e6fd4b13886a3e9/chargerinfo_sample_small.csv"

st.set_page_config(page_title="전기차 충전소 지도", layout="wide")
st.title("🔌 전기차 충전소 지도 확인")

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df[['위도', '경도']] = df['위도경도'].str.split(',', expand=True).astype(float)
    return df

df = load_data(GITHUB_CSV_URL)

# 지도 중심 (서울 기본값)
default_lat, default_lng = 37.5665, 126.9780
m = folium.Map(location=[default_lat, default_lng], zoom_start=13)

# 마커 추가
for _, row in df.iterrows():
    folium.Marker(
        [row['위도'], row['경도']],
        tooltip=row['충전소명'],
        popup=folium.Popup(f"""
            <b>{row['충전소명']}</b><br>
            📍 주소: {row['주소']}<br>
            ⚡ 충전기 타입: {row['충전기타입']}<br>
            🏢 시설: {row['시설구분(대)']} - {row['시설구분(소)']}<br>
        """, max_width=300),
        icon=folium.Icon(color="green", icon="flash")
    ).add_to(m)

st_folium(m, width=900, height=600)
