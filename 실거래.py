import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import datetime
import requests
from streamlit_lottie import st_lottie

@st.experimental_memo
def getRTMSDataSvcAptTrade(city, date, user_key, rows):
    url = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"

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
        계약            = int(item.find('월').text) * 100 + int(item.find('일').text)
        동                  = item.find("법정동").text
        면적            = float(item.find("전용면적").text)
        아파트              = item.find("아파트").text
        층                  = int(item.find("층").text)
        금액            = item.find("거래금액").text
        건축            = int(item.find("건축년도").text)
        거래            = item.find("거래유형").text
        파기      = item.find("해제사유발생일").text
        temp = pd.DataFrame(([[아파트, 금액, 층,면적, 건축, 계약 ,동, 거래, 파기]]), 
                            columns=["아파트", "금액", "층", "면적", "건축", "계약","동", "거래", "파기"])
        aptTrade = pd.concat([aptTrade,temp])
    replace_word = '아파트','마을','신도시','단지','\(.+\)','중개거래','거래'
    for i in replace_word:
        aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)
        aptTrade['거래'] = aptTrade['거래'].str.replace(i,'',regex=True)
    aptTrade['금액'] = aptTrade['금액'].str.replace(',','')
    aptTrade['파기'] = aptTrade['파기'].str.replace('22.','')
    aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.2f}'.format)
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    
    return aptTrade.sort_values(by=['계약'], ascending=False)

def api(date):
    당월전체 = getRTMSDataSvcAptTrade(city, date, user_key, rows)
    return 당월전체

@st.experimental_memo    
def load_lottie(url:str):
    r = requests.get(url)

    if r.status_code != 200:
        return None
    return r.json()

# lottie_url = 'https://assets7.lottiefiles.com/packages/lf20_ghunc0fe.json'
lottie_url = 'https://assets1.lottiefiles.com/packages/lf20_9kfnbeaf.json'
lottie_json = load_lottie(lottie_url)

st_lottie(
    lottie_json,
    speed=2,
    # # reverse='Ture',
    loop=True,
    quality='low',
    )

file_1 = pd.read_csv(st.secrets.user_path, encoding='cp949')
user_key = st.secrets.user_key

c1,c2,c3 = st.columns([1,1,1])
try:
    with c1 :
        date = st.date_input('📆 날짜').strftime('%Y%m%d')
        date_2 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=int(date[6:])).strftime('%m.')
        date,date_2
    with c2:
        with c3:
            empey = st.empty()
            아파트 = empey.selectbox('아파트', ' ')

        시군구 = st.selectbox('🖥️ 검색 또는 선택', sorted([i for i in set(file_1["법정동명"])]),index=230) # 93 강남 230 파주
        file_2 = file_1[file_1['법정동명'].str.contains(시군구)].astype(str)
        city = file_2.iloc[0,0][:5]
        rows = '9999'
        
    당월 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=int(date[6:]))
    전월 = 당월 - datetime.timedelta(days=30)
    어제 = 당월 - datetime.timedelta(days=1)
    갱신 = pd.concat([api(당월.strftime('%Y%m%d')),api(전월.strftime('%Y%m%d'))]).reset_index(drop=True)
    고정 = pd.read_csv(st.secrets.fixed_data, encoding='cp949').drop(columns=['Unnamed: 0'])
    고정['면적'] = 고정['면적'].map('{:.2f}'.format)
    고정['계약'] = 고정['계약'].map('{:.2f}'.format)
    고정['금액'] = 고정['금액'].astype(int)
    갱신['금액'] = 갱신['금액'].astype(int)
    고정 = 고정.fillna('')
    신규 = pd.merge(갱신,고정, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)

    if 시군구:
        당월전체 = 갱신
        당월전체 = 당월전체[당월전체['계약'].str.contains(date_2)].reset_index(drop=True)
        당월전체['계약'] = 당월전체['계약'].str.replace('22.','',regex=True)
        아파트 = empey.selectbox('🏠 아파트', sorted([i for i in 당월전체["아파트"].drop_duplicates()]))
     
    with c3:  
        아파트별 = 당월전체[당월전체['아파트'] == 아파트].sort_values(by=['금액'], ascending=False).reset_index(drop=True)
        
    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 🚀 아파트별 {len(아파트별)}건',expanded=False) :
        if len(당월전체) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')
        else:
            st.dataframe(아파트별.style.background_gradient(subset=['금액','면적','계약'], cmap='Reds')) 

    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 전체 {len(당월전체)}건',expanded=False) :
        if len(당월전체) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')
        else:
            st.dataframe(당월전체.style.background_gradient(subset=['금액', '면적', '계약'], cmap="Reds"))
    
    if len(신규) == 0 :
        st.info(f'{date[6:]}일 신규 등록이 없습니다😎')
    else:
        with st.expander(f'{시군구} 실거래 - {date[6:]}일 신규 {len(신규)}건',expanded=True):
            st.info(f'{date[6:]}일 신규 등록😎')
            st.dataframe(신규.style.background_gradient(subset=['금액', '면적', '계약'], cmap="Reds"))
    # 갱신.to_csv(f'C:/Users/kdkim/Desktop/python/{시군구}_{date}.csv', encoding='cp949')
    
except Exception as e:
    st.write(e)
    st.error('No data.😎')
