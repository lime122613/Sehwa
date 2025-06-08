import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# GitHub Raw URLs
url1 = "https://raw.githubusercontent.com/ZackWoo05/Sehwa/234c446f6e368583be840f2a93aceea87e112151/chargerinfo_part1.csv"
url2 = "https://raw.githubusercontent.com/ZackWoo05/Sehwa/234c446f6e368583be840f2a93aceea87e112151/chargerinfo_part2.csv"

st.set_page_config(page_title="전기차 충전소 지도", layout="wide")
st.title("🔌 전국 전기차 충전소 클러스터 지도")

@st.cache_data
def load_combined_data(url1, url2):
    df1 = pd.read_csv(url1)
    df2 = pd.read_csv(url2)
    df = pd.concat([df1, df2], ignore_index=True)

    # 위도/경도 분리 및 NaN 제거
    df[['위도', '경도']] = df['위도경도'].str.split(',', expand=True)
    df.dropna(subset=['위도', '경도'], inplace=True)
    df['위도'] = df['위도'].astype(float)
    df['경도'] = df['경도'].astype(float)

    return df

df = load_combined_data(url1, url2)

# 지도 중심
map_center = [37.5665, 126.9780]  # 서울
m = folium.Map(location=map_center, zoom_start=12)

# 클러스터 생성
marker_cluster = MarkerCluster().add_to(m)

# 마커 추가 (모두 클러스터에 추가)
for _, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        tooltip=row['충전소명'],
        popup=folium.Popup(f"""
            <b>{row['충전소명']}</b><br>
            📍 주소: {row['주소']}<br>
            ⚡ 충전기 타입: {row['충전기타입']}<br>
            🏢 시설: {row['시설구분(대)']} - {row['시설구분(소)']}<br>
        """, max_width=300),
        icon=folium.Icon(color="green", icon="flash")
    ).add_to(marker_cluster)

# Streamlit 지도 출력
st_folium(m, width=900, height=600)
