import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie,st_lottie_spinner
import altair as alt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


urls= ['http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev','http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?']

@st.experimental_memo
def load_lottie(url:str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

@st.experimental_singleton
def 차트(data,y,t):
    input_dropdown = alt.binding_select(options=sorted([i for i in t['면적'].drop_duplicates()]), name='면적별 🎈 ')
    hover = alt.selection_single(
        fields=["면적"],
        bind= input_dropdown,
        nearest=True,
        on="mouseover",
        empty="all",
        )

    lines = (
        alt.Chart(data,)
        .mark_line()
        .encode(
            x=alt.X("계약", title=None),
            y=alt.Y(y, scale=alt.Scale(zero=False),sort='y', title=None),
            color=alt.Color('아파트',scale=alt.Scale(scheme='category10'),legend=alt.Legend(orient='bottom', direction='vertical')),
            tooltip=[
                alt.Tooltip("층", title="층"),
                alt.Tooltip(y, title=y),
                alt.Tooltip("아파트", title="아파트"),
            ]
        ).transform_filter(hover)
    )
    points = lines.transform_filter(hover).mark_circle(size=150) #65

    tooltips = (
        alt.Chart(data)
        .mark_circle(size=100)
        .encode(
            x=alt.X("계약", title=None),
            y=alt.Y(y, scale=alt.Scale(zero=False),title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(.1)),
            color=alt.Color('아파트',legend=alt.Legend(orient='bottom', direction='vertical')),
            tooltip=[
                alt.Tooltip('면적', title='면적'),
                alt.Tooltip(y, title=y),
                alt.Tooltip("아파트", title="아파트"),
            ]
        )
        .add_selection(hover)
        .transform_filter(hover)
    )
    return (lines + points + tooltips).interactive()

# cred = credentials.Certificate('kdongsan-8cc40-firebase-adminsdk-vr6ws-d96491c757.json')
# app = firebase_admin.initialize_app(cred)
db = firestore.client()

file_1 = pd.read_csv('/Users/kyu-deokkim/Downloads/address.csv',encoding='cp949')
user_key = 'pRcMh3ZvTSWhUPu4VIMig%2BbD1mnLgAyaxyhB07a86H8XbgJ7ki8JYqk3a6Q6lM%2FN8zhvYZHQsLw0pmbjPBBE%2FA%3D%3D'
rows = '9999'

# lottie_url = 'https://assets1.lottiefiles.com/packages/lf20_yJ8wNO.json'
# lottie_json = load_lottie(lottie_url)
lottie_url2 = 'https://assets9.lottiefiles.com/packages/lf20_2v2beqrh.json'
lottie_json2 = load_lottie(lottie_url2)

st_lottie(
    lottie_json2,
    speed=2,
    # # reverse='Ture',
    loop=True,
    quality='low',
    )
# @st.experimental_singleton
def 매매():
    매매 = db.collection(f'매매 {standard}').document(시군구).get()
    for doc in 매매.to_dict().values():
        temp = pd.DataFrame(
            [doc.split(',') for doc in doc[1:]],
            columns=["시군구", "아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        temp = temp[["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"]]
        temp['금액']= temp['금액'].astype(int)
        temp['층']= temp['층'].astype(int)
        temp['건축']= temp['건축'].astype(int)
    return temp

# @st.experimental_singleton
def 임대():
    임대 = db.collection(f'임대 {standard}').document(시군구).get()
    for doc2 in 임대.to_dict().values():
        temp2 = pd.DataFrame(
            [doc.split(',') for doc in doc2[1:]],
            columns=["시군구", "아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"])
        temp2 = temp2[["아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"]]
        temp2['보증금']= temp2['보증금'].astype(int)
        temp2['층']= temp2['층'].astype(int)
        temp2['월세']= temp2['월세'].astype(int)
        temp2['건축']= temp2['건축'].astype(int)
    return temp2

c1,c2 = st.columns([1,1])
try:
    with c1 :
        standard = st.date_input('🍳 날짜', (datetime.utcnow() + timedelta(hours=9))).strftime('%y.%m.%d')
        date = standard[:5]
    with c2:
        시군구 = st.selectbox('🍰 시군구 검색', sorted([i for i in set(file_1["법정동명"])]),index=228) # 93 강남 230 파주
        
    temp = 매매()
    temp2 = 임대()
        
    전세_당월 = temp2[(temp2['계약'].str.contains(date)) & (temp2['월세'] == 0)].drop_duplicates()
    전세_당월 = 전세_당월.reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "종전보증금", "갱신권"])
    
    월세_당월 = temp2[(temp2['계약'].str.contains(date)) & (temp2['월세'] != 0)].drop_duplicates()
        
    with st.expander(f'{시군구} 실거래 - {date[3:5]}월 🍩 전체',expanded=True):
        매매_당월 = temp[temp['계약'].str.contains(date)].drop_duplicates()
        st.warning('🚥 다중선택가능')
        tab1, tab2, tab3 = st.tabs([f"매매 {len(매매_당월)}", f"전세 {len(전세_당월)}", f"월세 {len(월세_당월)}"])
        
        with tab1:
            아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 매매_당월["아파트"].drop_duplicates()]),max_selections=3)
            if not 아파트:
                아파트별 = 매매_당월
            else:
                아파트별 = 매매_당월[매매_당월["아파트"].isin(아파트)]
            st.dataframe(아파트별.sort_values(by=['아파트'], ascending=True).reset_index(drop=True).style.background_gradient(subset=['금액','면적'], cmap="Reds"),use_container_width=True)
            if 아파트 :
                매매_전월당월_전체 = temp[temp["아파트"].isin(아파트)]
                st.error('📈 시세 동향')
                chart = 차트(매매_전월당월_전체,y='금액',t=매매_전월당월_전체)
                st.altair_chart(chart,use_container_width=True)                

    with tab2:
        아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 전세_당월["아파트"].drop_duplicates()]),max_selections=3)
        if not 아파트:
            전세_당월 = 전세_당월
        else:
            전세_당월 = 전세_당월[전세_당월["아파트"].isin(아파트)]

        st.dataframe(전세_당월.sort_values(by=['아파트'], ascending=True).reset_index(drop=True).style.background_gradient(subset=['보증금','면적','종전보증금'], cmap="Reds"),use_container_width=True)

        if 아파트 :
            전세_전월당월_전체 = temp2[(temp2['아파트'].isin(아파트)) & (temp2['월세'] == 0)]
            st.error('📈 시세 동향')
            chart = 차트(전세_전월당월_전체,y='보증금',t=전세_전월당월_전체)
            st.altair_chart(chart,use_container_width=True)

    with tab3: 
        아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 월세_당월["아파트"].drop_duplicates()]),max_selections=3)
        if not 아파트:
            월세_당월 = 월세_당월
        else:
            월세_당월 = 월세_당월[월세_당월["아파트"].isin(아파트)]
        st.dataframe(월세_당월.sort_values(by=['아파트'], ascending=True).reset_index(drop=True).style.background_gradient(subset=['보증금','월세','종전보증금','종전월세'], cmap="Reds"),use_container_width=True)

except Exception as e:
    st.write(e)
    st.error('No data.😎')