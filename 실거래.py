import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import datetime
import requests
from streamlit_lottie import st_lottie

@st.experimental_memo
def trade(city, date, user_key, rows):
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
        계약            = str(item.find('월').text + item.find('일').text)
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
    aptTrade['금액'] = aptTrade['금액'].str.replace(',','').astype(int)
    aptTrade['파기'] = aptTrade['파기'].str.replace('22.','',regex=True)
    aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.2f}'.format)
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    return aptTrade.sort_values(by=['계약'], ascending=False)

@st.experimental_memo
def rent(city, date, user_key, rows):
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
        계약            = str(item.find('월').text + item.find('일').text)
        동                  = item.find("법정동").text
        면적            = float(item.find("전용면적").text)
        아파트              = item.find("아파트").text
        층                  = int(item.find("층").text)
        보증금            = item.find("보증금액").text
        건축            = int(item.find("건축년도").text)
        월세            = item.find("월세금액").text
        temp = pd.DataFrame(([[아파트, 보증금, 월세, 층,면적, 건축, 계약 ,동,]]), 
                            columns=["아파트", "보증금", "월세", "층", "면적", "건축", "계약", "동",])
        aptTrade = pd.concat([aptTrade,temp])
        
    replace_word = '아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)
    aptTrade['보증금'] = aptTrade['보증금'].str.replace(',','').astype(int)
    aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.2f}'.format)
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    return aptTrade.sort_values(by=['계약'], ascending=False).reset_index(drop=(True))

@st.experimental_memo    
def load_lottie(url:str):
    r = requests.get(url)

    if r.status_code != 200:
        return None
    return r.json()
lottie_url = 'https://assets9.lottiefiles.com/packages/lf20_2v2beqrh.json'
lottie_json = load_lottie(lottie_url)

st_lottie(
    lottie_json,
    speed=2,
    # # reverse='Ture',
    loop=True,
    quality='low',
    )

def api(date):
    당월전체 = trade(city, date, user_key, rows)
    return 당월전체

def api2(date):
    당월전체 = rent(city, date, user_key, rows)
    return 당월전체

file_1 = pd.read_csv(st.secrets.user_path,encoding='cp949')
user_key = st.secrets.user_key
c1,c2,c3 = st.columns([1,1,1])
rows = '9999'

try:
    with c1 :
        date = st.date_input('📆 날짜',).strftime('%Y%m%d')
        date_2 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=int(date[6:])).strftime('%m.')
        
    with c2:
        with c3:
            empty = st.empty()
            아파트 = empty.selectbox('아파트', ' ')

        시군구 = st.selectbox('🖥️ 검색 또는 선택', sorted([i for i in set(file_1["법정동명"])]),index=230) # 93 강남 230 파주
        file_2 = file_1[file_1['법정동명'].str.contains(시군구)].astype(str)
        city = file_2.iloc[0,0][:5]
        
    오늘 = datetime.date.today().strftime('%Y%m%d')
    당월 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=int(date[6:]))
    전월 = 당월 - datetime.timedelta(days=30)
    어제 = 당월 - datetime.timedelta(days=1)
    갱신 = pd.concat([api(당월.strftime('%Y%m%d')),api(전월.strftime('%Y%m%d'))]).reset_index(drop=True)
    갱신['금액'] = 갱신['금액'].astype(int)
    갱신 = 갱신.reindex(columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
    
#     고정 = pd.read_csv(st.secrets.fixed_data, encoding='cp949').drop(columns=['Unnamed: 0'])    
#     고정['면적'] = 고정['면적'].map('{:.2f}'.format)
#     고정['계약'] = 고정['계약'].map('{:.2f}'.format)
#     고정['금액'] = 고정['금액'].astype(int)
#     고정 = 고정.fillna('')
#     신규 = pd.merge(갱신,고정, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
    
    아파트 = empty.selectbox('🏠 아파트',sorted([i for i in 갱신["아파트"].drop_duplicates()]))
    갱신2 = 갱신[갱신['아파트'].str.contains(아파트)]
    아파트별 = 갱신2[(갱신2['아파트'] == 아파트) & (갱신2['계약'].str.contains(date_2))].sort_values(by=['금액'], ascending=False)
    전월당월전세월세 = pd.concat([api2(당월.strftime('%Y%m%d')),api2(전월.strftime('%Y%m%d'))])
    당월_전세_전체 = 전월당월전세월세[(전월당월전세월세['계약'].str.contains(date_2)) & (전월당월전세월세['월세'] == '0')].drop(columns=['월세']).reset_index(drop=True)
    당월_월세_전체 = 전월당월전세월세[(전월당월전세월세['계약'].str.contains(date_2)) & (전월당월전세월세['월세'] != '0')].reset_index(drop=True)
    전월당월_전세_전체 = 전월당월전세월세[(전월당월전세월세['아파트'] == 아파트) & (전월당월전세월세['월세'] == '0')].drop(columns=['월세'])
    당월_전세_아파트별  = 당월_전세_전체[당월_전세_전체['아파트'] == 아파트]
    당월_월세_아파트별 = 당월_월세_전체[당월_월세_전체['아파트'] == 아파트]
    
    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 🍩 전체',expanded=False) :
        if len(갱신) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')
        tab1, tab2, tab3 = st.tabs([f"매매 {len(갱신)}", f"전세 {len(당월_전세_전체)}", f"월세 {len(당월_월세_전체)}"])
        with tab1 :
            st.dataframe(갱신.style.background_gradient(subset=['금액','면적','계약'], cmap="Reds"),use_container_width=True)
        with tab2:
            st.dataframe(당월_전세_전체.style.background_gradient(subset=['보증금','면적','계약'], cmap="Reds"),use_container_width=True)
        with tab3:
            st.dataframe(당월_월세_전체.style.background_gradient(subset=['보증금','층','건축'], cmap="Reds"),use_container_width=True)
    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 🍰 아파트별',expanded=False) :
        tab4, tab5, tab6 = st.tabs(["매매", "전세", "월세"])

        if len(갱신) == 0 :
            st.info(f'{date[4:5+1]}월 신규 등록이 없습니다😎')

        with tab4:
            면적_라디오 = st.radio('🔎 면적',[i for i in 아파트별['면적'].drop_duplicates()],key='매매면적',horizontal=True)
            면적별 = 갱신2[갱신2['면적'] == 면적_라디오].reset_index(drop=True)
            
            if len(면적별) > 0 :
                st.dataframe(면적별.style.background_gradient(subset=['금액','면적','계약'], cmap='Reds'),use_container_width=True)
                st.error('📈 시세 동향')
                st.line_chart(면적별,x='계약',y='금액')
            else:
                st.error('No data.😎')
                
        with tab5:
            if len(당월_전세_아파트별) > 1:
                면적_라디오_전세 = st.radio('🔎 면적',[i for i in 당월_전세_아파트별['면적'].drop_duplicates()],key='전세면적',horizontal=True)                
                전월당월_전세면적별 =  전월당월_전세_전체[(전월당월_전세_전체['면적'] == 면적_라디오_전세)].reset_index(drop=True)
                당월_전세면적별 =  당월_전세_아파트별[당월_전세_아파트별['면적'] == 면적_라디오_전세].reset_index(drop=True)
                전세면적별 = 전월당월_전세_전체[(전월당월_전세_전체['면적'] == 면적_라디오_전세)].reset_index(drop=True)

                st.dataframe(당월_전세면적별.style.background_gradient(subset=['보증금','면적','계약'], cmap="Blues"),use_container_width=True)
                st.error('📈 시세 동향')
                st.line_chart(전월당월_전세면적별,x='계약',y='보증금')
            else:
                st.error('No data.😎')

        with tab6:
            if len(당월_월세_아파트별) > 1:
                면적_라디오_월세 = st.radio('🔎 면적',[i for i in 당월_월세_아파트별['면적'].drop_duplicates()],key='월세면적',horizontal=True)
                월세면적별 = 당월_월세_아파트별[(당월_월세_아파트별['면적'] == 면적_라디오_월세)].reset_index(drop=True)
                st.dataframe(월세면적별.style.background_gradient(subset=['보증금','층','건축'], cmap="Blues"),use_container_width=True)
            else:
                st.error('No data.😎')
except Exception as e:
#     st.write(e)
    st.error('No data.😎')
