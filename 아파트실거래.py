import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import datetime
import requests
from streamlit_lottie import st_lottie,st_lottie_spinner
import altair as alt

st.set_page_config(page_title="🎈아파트 실거래가 매매/전세/월세 ",layout='wide')
empty = st.empty()
empty.write('아파트 실거래')
empty.empty()

# @st.experimental_singleton
# @st.experimental_memo   
def 매매(city, date, user_key, rows):
    url = st.secrets.api_path
    url = url + "?&LAWD_CD=" + city
    url = url + "&DEAL_YMD=" + date[:6]
    url = url + "&serviceKey=" + user_key
    url = url + "&numOfRows=" + rows
    
    xml = req.urlopen(url)
    result = xml.read()
    soup = BeautifulSoup(result, 'lxml-xml')    
    
    items = soup.findAll("item")
    aptTrade = pd.DataFrame()
    for item in items:
        계약            = str(item.find('년').text + item.find('월').text + item.find('일').text)
        # 계약            = str(item.find('월').text + item.find('일').text)
        동                  = item.find("법정동").text
        면적            = float(item.find("전용면적").text)
        아파트              = item.find("아파트").text
        층                  = int(item.find("층").text)
        금액            = item.find("거래금액").text
        건축            = int(item.find("건축년도").text)
        거래            = item.find("거래유형").text
        파기      = item.find("해제사유발생일").text
        temp = pd.DataFrame(([[아파트, 금액, 층,면적, 건축, 계약 ,동, 거래, 파기]]), 
                            columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        aptTrade = pd.concat([aptTrade,temp])
    replace_word = '파주','아파트','마을','신도시','단지',r'\(.+\)','중개거래','거래'
    for i in replace_word:
        aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)
        aptTrade['거래'] = aptTrade['거래'].str.replace(i,'',regex=True)
    aptTrade['금액'] = aptTrade['금액'].str.replace(',','').astype(int)
    aptTrade['파기'] = aptTrade['파기'].str.replace('22.','',regex=True)
    aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    # aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.2f}'.format).str.split('.').str[0]
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    return aptTrade.sort_values(by=['아파트'], ascending=True)

# @st.experimental_singleton
# @st.experimental_memo   
def 임대(city, date, user_key, rows):
    url = st.secrets.api_path_2
    url = url + "?&LAWD_CD=" + city
    url = url + "&DEAL_YMD=" + date[:6]
    url = url + "&serviceKey=" + user_key
    url = url + "&numOfRows=" + rows
    
    xml = req.urlopen(url)
    result = xml.read()
    soup = BeautifulSoup(result, 'lxml-xml')    
    
    items = soup.findAll("item")
    aptTrade = pd.DataFrame()
    for item in items:
        계약            = str(item.find('년').text + item.find('월').text + item.find('일').text)
        # 계약            = str(item.find('월').text + item.find('일').text)
        동                  = item.find("법정동").text
        면적            = float(item.find("전용면적").text)
        아파트              = item.find("아파트").text
        층                  = int(item.find("층").text)
        보증금            = item.find("보증금액").text
        건축            = int(item.find("건축년도").text)
        월세            = item.find("월세금액").text
        갱신권            = item.find("갱신요구권사용").text
        기간            = item.find("계약기간").text
        종전보증금        = item.find("종전계약보증금").text
        종전월세        = item.find("종전계약월세").text 
        temp = pd.DataFrame(([[아파트, 보증금, 층, 월세, 면적, 건축, 동, 계약, 기간,  종전보증금,종전월세, 갱신권,]]), 
                            columns=["아파트", "보증금", "층", "월세", "면적", "건축","동", "계약", "기간", "종전보증금", "종전월세", "갱신권"])
        aptTrade = pd.concat([aptTrade,temp])
        
    replace_word = '파주','아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)
    aptTrade['보증금'] = aptTrade['보증금'].str.replace(',','')
    aptTrade['종전보증금'] = aptTrade['종전보증금'].str.replace(',','')
    aptTrade['기간'] = aptTrade['기간'].str[6:]
    aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    # aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['면적'] = aptTrade['면적'].map('{:.2f}'.format).str.split('.').str[0]
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    return aptTrade.sort_values(by=['아파트'], ascending=True)

@st.experimental_memo     
def load_lottie(url:str):
    r = requests.get(url)

    if r.status_code != 200:
        return None
    return r.json()
lottie_url = 'https://assets1.lottiefiles.com/packages/lf20_yJ8wNO.json'
lottie_json = load_lottie(lottie_url)
lottie_url2 = 'https://assets9.lottiefiles.com/packages/lf20_2v2beqrh.json'
lottie_json2 = load_lottie(lottie_url2)

# st_lottie(
#     lottie_json,
#     speed=2,
#     # # reverse='Ture',
#     loop=True,
#     quality='low',
#     )

def 매매차트단일(data):
    hover = alt.selection_single(
        fields=["금액"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("금액",title=None),
            color=alt.Color("면적",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("금액",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(.7)),
            tooltip=[
                alt.Tooltip("면적", title="면적"),
                alt.Tooltip("금액", title="금액"),
                alt.Tooltip("아파트", title="아파트"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def 매매차트다중(data):
    hover = alt.selection_single(
        fields=["금액"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("금액",title=None),
            color=alt.Color("아파트",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("금액",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("면적", title="면적"),
                alt.Tooltip("금액", title="금액"),
                alt.Tooltip("아파트", title="아파트"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def 임대차트단일(data):
    hover = alt.selection_single(
        fields=["보증금"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("보증금",title=None),
            color=alt.Color("면적",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("보증금",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(.7)),
            tooltip=[
                alt.Tooltip("면적", title="면적"),
                alt.Tooltip("보증금", title="보증금"),
                alt.Tooltip("아파트", title="아파트"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def 임대차트다중(data):
    hover = alt.selection_single(
        fields=["보증금"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("보증금",title=None),
            color=alt.Color("아파트",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("계약",title=None),
            y=alt.Y("보증금",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("면적", title="면적"),
                alt.Tooltip("보증금", title="보증금"),
                alt.Tooltip("아파트", title="아파트"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

file_1 = pd.read_csv(st.secrets.user_path,encoding='cp949')
user_key = st.secrets.user_key
rows = '9999'

st_lottie(
    lottie_json2,
    speed=2,
    # # reverse='Ture',
    loop=True,
    quality='low',
    )

c1,c2 = st.columns([1,1])
try:
    with st_lottie_spinner(lottie_json):
        with c1 :
            date = st.date_input('🍳 날짜',value= datetime.date.today()+ datetime.timedelta(hours=22)).strftime('%Y%m%d')
            date_2 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=datetime.datetime.now().day).strftime('%m.')

        with c2:
            시군구 = st.selectbox('🍰 시군구 검색', sorted([i for i in set(file_1["법정동명"])]),index=230) # 93 강남 230 파주

            file_2 = file_1[file_1['법정동명'].str.contains(시군구)].astype(str)
            city = file_2.iloc[0,0][:5]

            # 오늘 = datetime.datetime.now().strftime('%Y%m%d')    
        당월 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=datetime.datetime.now().day)
        전월 = 당월 - datetime.timedelta(days=30)
        # 어제 = datetime.datetime.now() - datetime.timedelta(days=1)
        갱신 = pd.concat([매매(city, 당월.strftime('%Y%m%d'), user_key, rows),매매(city, 전월.strftime('%Y%m%d'), user_key, rows),]).reset_index(drop=True).drop_duplicates()

        당월_매매_전체 = 갱신[갱신['계약'].str.contains(date_2)]
        전월당월전세월세 = pd.concat([임대(city, 당월.strftime('%Y%m%d'), user_key, rows),임대(city, 전월.strftime('%Y%m%d'), user_key, rows),]).reset_index(drop=True).drop_duplicates()
#         전월당월전세월세 = 임대(city, 당월.strftime('%Y%m%d'), user_key, rows)

        당월_전세_전체 = 전월당월전세월세[(전월당월전세월세['계약'].str.contains(date_2)) & (전월당월전세월세['월세'] == '0')].drop(columns=['월세']).reset_index(drop=True)
        당월_월세_전체 = 전월당월전세월세[(전월당월전세월세['계약'].str.contains(date_2)) & (전월당월전세월세['월세'] != '0')].reset_index(drop=True)
    
#     고정 = pd.read_csv(st.secrets.fixed_data, encoding='cp949').drop(columns=['Unnamed: 0'])    
#     고정['면적'] = 고정['면적'].map('{:.2f}'.format)
#     고정['계약'] = 고정['계약'].map('{:.2f}'.format)
#     고정['금액'] = 고정['금액'].astype(int)
#     고정 = 고정.fillna('')
#     신규 = pd.merge(갱신,고정, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)

    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 🍩 전체',expanded=True):
        if len(갱신) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')
        tab1, tab2, tab3 = st.tabs([f"매매 {len(당월_매매_전체)}", f"전세 {len(당월_전세_전체)}", f"월세 {len(당월_월세_전체)}"])

        with tab1 :
            아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 당월_매매_전체["아파트"].drop_duplicates()]),max_selections=5)
            당월전월매매아파트별 = 갱신[갱신["아파트"].isin(아파트)].reset_index(drop=True)
            st.warning('🚥 단일선택 면적별, 다중선택 아파트별')
            if not 아파트:            
                아파트별멀티 = 당월_매매_전체
            else:
                아파트별멀티 = 당월_매매_전체[당월_매매_전체["아파트"].isin(아파트)].reset_index(drop=True)
            st.dataframe(아파트별멀티.style.background_gradient(subset=['금액','면적'], cmap="Reds"),use_container_width=True)

            if len(아파트) == 1:
                st.error('📈 시세 동향')
                chart = 매매차트단일(당월전월매매아파트별)
                st.altair_chart(chart,use_container_width=True)
            elif len(아파트) > 1 :
                st.error('📈 시세 동향')
                chart = 매매차트다중(당월전월매매아파트별)
                st.altair_chart(chart,use_container_width=True)

        with tab2:
            아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 당월_전세_전체["아파트"].drop_duplicates()]),max_selections=5)
            st.warning('🚥 단일선택 면적별, 다중선택 아파트별')
            전월당월전세전체 = 전월당월전세월세[(전월당월전세월세['아파트'].isin(아파트)) & (전월당월전세월세['월세'] == '0')].reset_index(drop=True)
            당월_전세_전체 = 당월_전세_전체.reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "기간", "종전보증금", "갱신권"])
            if not 아파트:
                당월_전세_전체 = 당월_전세_전체
            else:
                당월_전세_전체 = 당월_전세_전체[당월_전세_전체["아파트"].isin(아파트)].reset_index(drop=True)
            st.dataframe(당월_전세_전체.style.background_gradient(subset=['보증금','면적'], cmap="Reds"),use_container_width=True)

            if len(아파트) == 1:
                st.error('📈 시세 동향')
                chart = 임대차트단일(전월당월전세전체)
                st.altair_chart(chart,use_container_width=True)
            elif len(아파트) > 1 :
                st.error('📈 시세 동향')
                chart = 임대차트다중(전월당월전세전체)
                st.altair_chart(chart,use_container_width=True)
        with tab3:
            아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 당월_월세_전체["아파트"].drop_duplicates()]),max_selections=5)
            st.warning('🚥 단일선택 면적별, 다중선택 아파트별')
            
            if not 아파트:
                당월_월세_전체 = 당월_월세_전체
            else:
                당월_월세_전체 = 당월_월세_전체[당월_월세_전체["아파트"].isin(아파트)].reset_index(drop=True)


            col_loc = 당월_월세_전체.columns.get_loc('보증금') ## 원하는 칼럼의 인덱스
            st.dataframe(당월_월세_전체.style.background_gradient(subset=['보증금','월세'], cmap="Reds"),use_container_width=True)
            # .set_index(['아파트'])
            # .style.background_gradient(subset=['보증금','월세'], cmap="Reds")
except Exception as e:
    st.write(e)
    st.error('No data.😎')
