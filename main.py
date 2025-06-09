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
    df1 = pd.read_csv(url1, low_memory=False)
    df2 = pd.read_csv(url2, low_memory=False)
    df = pd.concat([df1, df2], ignore_index=True)

    # 위도경도 분리
    df[['위도', '경도']] = df['위도경도'].str.split(',', expand=True)

    # 숫자형 변환 (오류는 NaN으로 처리)
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')

    # NaN 제거
    df.dropna(subset=['위도', '경도'], inplace=True)

    # 대한민국 좌표 범위로 제한 (예외 제거)
    df = df[(df['위도'] > 33) & (df['위도'] < 39) & (df['경도'] > 124) & (df['경도'] < 132)]

    # 주소에서 시도, 구군 추출
    df['시도'] = df['주소'].str.split().str[0]
    df['구군'] = df['주소'].str.split().str[1]

    return df

# 전체 데이터 미리 불러오지 않고, 지역 선택 후 로드
st.markdown("### 📍 지역을 먼저 선택해주세요")

with st.spinner("🔍 데이터 준비 중..."):
    df = load_combined_data(url1, url2)
    st.write(df.columns)  # 실제 컬럼명 출력
    시도목록 = sorted(df['시도'].dropna().unique())

선택한_시도 = st.selectbox("시/도 선택", 시도목록, index=시도목록.index("서울특별시"))
선택한_구군 = None
if 선택한_시도:
    구군목록 = sorted(df[df['시도'] == 선택한_시도]['구군'].dropna().unique())
    선택한_구군 = st.selectbox("구/군 선택", 구군목록, index=구군목록.index("서초구") if "서초구" in 구군목록 else 0)

if 선택한_시도 and 선택한_구군:
    with st.spinner("🚗 충전소 데이터를 불러오는 중입니다..."):
        df_filtered = df[(df['시도'] == 선택한_시도) & (df['구군'] == 선택한_구군)]

        map_center = [37.5009, 126.9872]  # 세화고등학교 기준
        m = folium.Map(location=map_center, zoom_start=13)
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df_filtered.iterrows():
            folium.Marker(
                location=[row['위도'], row['경도']],
                tooltip=row['충전소명'],
                popup=folium.Popup(f"""
                    <b>{row['충전소명']}</b><br>
                    📍 주소: {row['주소']}<br>
                    🏢 시설: {row['시설구분(대)']} - {row['시설구분(소)']}<br>
                """, max_width=300),
                icon=folium.Icon(color="green", icon="flash")
            ).add_to(marker_cluster)

        st_folium(m, width=900, height=600)
