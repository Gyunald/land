import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import datetime
import requests
from streamlit_lottie import st_lottie

@st.experimental_memo
def getRTMSDataSvcAptTrade(city, date, user_key, rows): 
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
        거래일자            = int(item.find("년").text) * 10000 + int(item.find('월').text) * 100 + int(item.find('일').text)
        동                  = item.find("법정동").text
        면적            = float(item.find("전용면적").text)
        아파트              = item.find("아파트").text
        층                  = int(item.find("층").text)
        거래금액            = item.find("거래금액").text
        건축            = int(item.find("건축년도").text)
        거래유형            = item.find("거래유형").text
        해제            = item.find("해제여부").text
        발생일      = item.find("해제사유발생일").text
        temp = pd.DataFrame(([[아파트, 거래금액, 층, 면적, 건축, 동, 거래일자, 거래유형, 해제, 발생일]]), 
                            columns=["아파트                    ", "거래금액", "층", "면적",  "건축", "동", "거래일", "거래유형", "해제","발생일"]) 
        aptTrade = pd.concat([aptTrade,temp])

    aptTrade = aptTrade.reset_index(drop=True)    
    aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.2f}'.format)
    aptTrade['거래금액'] = aptTrade['거래금액'].str.replace(',','').astype(int)
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    replace_word = '아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        aptTrade['아파트                    '] = aptTrade['아파트                    '].str.replace(i,'',regex=True)
    return aptTrade

def api(date):
    당월전체 = getRTMSDataSvcAptTrade(city, date, user_key, rows)
    return 당월전체

@st.experimental_memo    
def load_lottie(url:str):
    r = requests.get(url)

    if r.status_code != 200:
        return None
    return r.json()

lottie_url = 'https://assets7.lottiefiles.com/packages/lf20_ghunc0fe.json'
lottie_json = load_lottie(lottie_url)

st_lottie(
    lottie_json,
    speed=3,
    # # reverse='Ture',
    loop=True,
    quality='low',
    )

file_1 = pd.read_csv(st.secrets.user_path,encoding='cp949')
user_key = st.secrets.user_key

c1,c2,c3 = st.columns([1,1,1])
try:
    with c1 :
        date = st.date_input('📆 날짜').strftime('%Y%m%d')
        date_2 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=int(date[6:])).strftime('%y.%m')
    with c2:
        with c3:
            empey = st.empty()
            아파트 = empey.selectbox('아파트', ' ')

        시군구 = st.selectbox('🖥️ 검색 또는 선택', sorted([i for i in set(file_1["법정동명"])]),index=230) # 93 강남 230 파주
        file_2 = file_1[file_1['법정동명'].str.contains(시군구)].astype(str)
        city = file_2.iloc[0,0][:5]
        rows = '9999'
        
    당월 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=int(date[6:]))
    어제 = 당월 - datetime.timedelta(days=1)
    전월 = 당월 - datetime.timedelta(days=30)
    오늘합 = pd.concat([api(당월.strftime('%Y%m')),api(전월.strftime('%Y%m'))]).reset_index(drop=True)
    오늘합['계약일'] = pd.to_datetime(오늘합['거래일'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    오늘합['거래금액'] = 오늘합['거래금액'].astype('int64')
    오늘합['면적'] = 오늘합['면적'].astype(float).map('{:.2f}'.format)
    오늘합 = 오늘합[["아파트                    ", "거래금액", "층", "면적", "계약일","건축", "동", "거래유형", "해제", "발생일"]].sort_values(by=['거래금액'], ascending=False).reset_index(drop=True)
    
    if 시군구:
        당월전체 = 오늘합
        당월전체 = 당월전체[당월전체['계약일'].str.contains(date_2)]
        당월전체['계약일'] = 당월전체['계약일'].str.replace('22.','',regex=True)
        아파트 = empey.selectbox('🏠 아파트', sorted([i for i in 당월전체["아파트                    "].drop_duplicates()]))
        
    with c3:  
        아파트별 = 당월전체[당월전체['아파트                    '] == 아파트]
        
    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 🚀 아파트별',expanded=True) :
        if len(당월전체) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')
        else:
            st.dataframe(아파트별.style.background_gradient(subset=['거래금액','면적','건축'], cmap='Reds')) 
            
    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 전체',expanded=True) :
        if len(당월전체) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')
        else:
            st.dataframe(당월전체.style.background_gradient(subset=['거래금액', '면적', '건축'], cmap="Reds"))      

    st.success('GTX 운정신도시 오픈챗 🚅 https://open.kakao.com/o/gICcjcDb')
    st.warning('참여코드 🍩 2023gtxa')
    
except Exception as e:
    st.error('No data.😎')
