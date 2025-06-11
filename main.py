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

# 충전기 타입 -> 차량 매핑 함수
def 충전가능차량(타입문자열):
    mapping = {
        "AC완속": "국산차 (현대 코나EV, 기아 니로EV 등)",
        "DC차데모": "일본차 (닛산 리프 등)",
        "DC콤보": "현대 아이오닉5, EV6, 제네시스 GV60, 테슬라 CCS1 어댑터 보유 시",
        "DC차데모+AC3상": "일본차 및 AC3상 호환 국산차",
        "DC차데모+DC콤보": "닛산 리프 + 현대기아차(E-GMP)",
        "DC차데모+AC3상+DC콤보": "모든 주요 충전 규격 지원 차량"
    }
    if not isinstance(타입문자열, str):
        return "정보 없음"

    차량리스트 = []
    for key, value in mapping.items():
        if key in 타입문자열:
            차량리스트.append(value)
    return ', '.join(sorted(set(차량리스트))) if 차량리스트 else "정보 없음"

# 전체 데이터 미리 불러오지 않고, 지역 선택 후 로드
with st.spinner("🔍 데이터 준비 중..."):
    df = load_combined_data(url1, url2)

탭1, 탭2 = st.tabs(["📍 지도 보기", "🚘 차량별 충전기 타입 설명"])

with 탭1:
    st.markdown("### 지역을 먼저 선택해주세요")
    시도목록 = sorted(df['시도'].dropna().unique())
    선택한_시도 = st.selectbox("시/도 선택", 시도목록, index=시도목록.index("서울특별시"))

    선택한_구군 = None
    if 선택한_시도:
        구군목록 = sorted(df[df['시도'] == 선택한_시도]['구군'].dropna().unique())
        선택한_구군 = st.selectbox("구/군 선택", 구군목록, index=구군목록.index("서초구") if "서초구" in 구군목록 else 0)

    if 선택한_시도 and 선택한_구군:
        with st.spinner("🚗 충전소 데이터를 불러오는 중입니다..."):
            df_filtered = df[(df['시도'] == 선택한_시도) & (df['구군'] == 선택한_구군)]

            if not df_filtered.empty:
                map_center = [df_filtered.iloc[0]['위도'], df_filtered.iloc[0]['경도']]
            else:
                map_center = [37.5009, 126.9872]

            # 👉 지도와 표를 나란히 출력할 공간 나누기
            col1, col2 = st.columns([2, 1])

            with col1:
                m = folium.Map(location=map_center, zoom_start=14)
                marker_cluster = MarkerCluster().add_to(m)

                for _, row in df_filtered.iterrows():
                    folium.Marker(
                        location=[row['위도'], row['경도']],
                        tooltip=row['충전소명'],
                        popup=folium.Popup(f"""
                            <b>{row['충전소명']}</b><br>
                            📍 주소: {row['주소']}<br>
                            🏢 시설: {row['시설구분(대)']} - {row['시설구분(소)']}<br>
                            🔋 충전기 타입: {row.get('충전기타입', '정보 없음')}<br>
                            🚘 가능 차량: {충전가능차량(row.get('충전기타입'))}
                        """, max_width=300),
                        icon=folium.Icon(color="green", icon="flash")
                    ).add_to(marker_cluster)

                st_folium(m, width=800, height=600)

            with col2:
                st.markdown("#### 📋 충전소 목록")
                st.dataframe(
                    df_filtered[['충전소명', '주소', '충전기타입', '시설구분(대)']].reset_index(drop=True),
                    use_container_width=True,
                    height=600
                )



with 탭2:
    st.markdown("## 🔍 충전기 타입별 충전 가능 차량 안내")
    설명표 = pd.DataFrame({
        "충전기 타입": [
            "AC완속",
            "DC차데모",
            "DC콤보",
            "DC차데모+AC3상",
            "DC차데모+DC콤보",
            "DC차데모+AC3상+DC콤보"
        ],
        "충전 가능 차량": [
            "국산차 (현대 코나EV, 기아 니로EV 등)",
            "일본차 (닛산 리프 등)",
            "현대 아이오닉5, EV6, 제네시스 GV60, 테슬라 CCS1 어댑터 보유 시",
            "일본차 및 AC3상 호환 국산차",
            "닛산 리프 + 현대기아차(E-GMP)",
            "모든 주요 충전 규격 지원 차량"
        ]
    })
    st.markdown("""아래 표를 통해 충전기 타입별로 어떤 차량이 충전 가능한지 확인해보세요:""")
    st.dataframe(설명표, use_container_width=True)
