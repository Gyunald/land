import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import requests
from streamlit_lottie import st_lottie,st_lottie_spinner
import altair as alt

st.set_page_config(page_title="🎈아파트 실거래가 매매/전세/월세 ",layout='wide')
empty = st.empty()
empty.write('아파트 실거래')
empty.empty()

# st.experimental_singleton.clear()

@st.experimental_singleton(ttl=600)
def 매매(city, date, user_key, rows):
    url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
    url = url + "?&LAWD_CD=" + city
    url = url + "&DEAL_YMD=" + date[:6]
    url = url + "&serviceKey=" + user_key
    url = url + "&numOfRows=" + rows
    
    xml = requests.get(url)
    result = xml.text
    soup = BeautifulSoup(result, 'lxml-xml')
    items = soup.findAll("item")
    aptTrade = pd.DataFrame()
    for item in items:
        계약            =   item.find("년").text + item.find("월").text.zfill(2) + item.find("일").text.zfill(2)
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
    aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.0f}'.format)
    aptTrade['동'] = aptTrade['동'].str.split().str[0]
    return aptTrade.sort_values(by=['아파트'], ascending=True)

@st.experimental_singleton(ttl=600)
def 임대(city, date, user_key, rows):
    url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?'
    url = url + "?&LAWD_CD=" + city
    url = url + "&DEAL_YMD=" + date[:6]
    url = url + "&serviceKey=" + user_key
    url = url + "&numOfRows=" + rows
    
    xml = requests.get(url)
    result = xml.text
    soup = BeautifulSoup(result, 'lxml-xml')    
    
    items = soup.findAll("item")
    aptTrade = pd.DataFrame()
    for item in items:
        계약            = item.find("년").text+item.find("월").text.zfill(2)+item.find("일").text.zfill(2)
        동                  = item.find("법정동").text
        면적            = float(item.find("전용면적").text)
        아파트              = item.find("아파트").text
        층                  = int(item.find("층").text)
        보증금            = item.find("보증금액").text
        건축            = int(item.find("건축년도").text)
        월세            = item.find("월세금액").text
        갱신권            = item.find("갱신요구권사용").text
        종전보증금        = item.find("종전계약보증금").text.replace(' ','0').astype(int)
        종전월세        = item.find("종전계약월세").text.replace(' ','0').astype(int) 
        temp = pd.DataFrame(([[아파트, 보증금, 층, 월세, 면적, 건축, 동, 계약, 종전보증금, 종전월세, 갱신권,]]), 
                            columns=["아파트", "보증금", "층", "월세", "면적", "건축","동", "계약", "종전보증금", "종전월세", "갱신권"])
        aptTrade = pd.concat([aptTrade,temp])
        
    replace_word = '파주','아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)
    aptTrade['보증금'] = aptTrade['보증금'].str.replace(',','').astype(int)
    aptTrade['종전보증금'] = aptTrade['종전보증금'].str.replace(',','')
    aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    aptTrade['면적'] = aptTrade['면적'].map('{:.0f}'.format)
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
            y=alt.Y(y, scale=alt.Scale(zero=False), title=None),
            color=alt.Color('아파트',legend=alt.Legend(orient='bottom', direction='vertical')),
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

with st_lottie_spinner(lottie_json):
    with c1 :
        date = st.date_input('🍳 날짜',value= datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y%m.')
        date_2 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=datetime.datetime.now().day)

    with c2:
        시군구 = st.selectbox('🍰 시군구 검색', sorted([i for i in set(file_1["법정동명"])]),index=230) # 93 강남 230 파주
        
        file_2 = file_1[file_1['법정동명'].str.contains(시군구)].astype(str)
        city = file_2.iloc[0,0][:5]
        
        # 오늘 = datetime.datetime.now().strftime('%Y%m%d')    
    당월 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=datetime.datetime.now().day)

    전월 = 당월 - datetime.timedelta(days=30)
    # 어제 = datetime.datetime.now() - datetime.timedelta(days=1)
    갱신 = pd.concat([매매(city, date, user_key, rows),매매(city, 전월.strftime('%Y%m'), user_key, rows),]).drop_duplicates()

    #전월당월전세월세 = pd.concat([임대(city, date, user_key, rows),임대(city, 전월.strftime('%Y%m'), user_key, rows),]).reset_index(drop=True).drop_duplicates()
    전월당월전세월세 = 임대(city, date, user_key, rows)
    당월_전세_전체 = 전월당월전세월세[(전월당월전세월세['계약'].str.contains(date[4:])) & (전월당월전세월세['월세'] == '0')].drop_duplicates()
    당월_월세_전체 = 전월당월전세월세[(전월당월전세월세['계약'].str.contains(date[4:])) & (전월당월전세월세['월세'] != '0')].drop_duplicates()
#     고정 = pd.read_csv(st.secrets.fixed_data, encoding='cp949').drop(columns=['Unnamed: 0'])    
#     고정['면적'] = 고정['면적'].map('{:.2f}'.format)
#     고정['계약'] = 고정['계약'].map('{:.2f}'.format)
#     고정['금액'] = 고정['금액'].astype(int)
#     고정 = 고정.fillna('')
#     신규 = pd.merge(갱신,고정, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
try:
    with st.expander(f'{시군구} 실거래 - {date[4:5+1]}월 🍩 전체',expanded=True):
        당월_매매_전체 = 갱신[갱신['계약'].str.contains(date[4:])].drop_duplicates()
        아파트 = st.multiselect('🍉 아파트별',sorted([i for i in 당월_매매_전체["아파트"].drop_duplicates()]),max_selections=3)
        st.warning('🚥 다중선택가능')
        tab1, tab2, tab3 = st.tabs([f"매매 {len(당월_매매_전체)}", f"전세 {len(당월_전세_전체)}", f"월세 {len(당월_월세_전체)}"])
        with tab1 :
            if not 아파트:
                아파트별멀티 = 당월_매매_전체
            else:
                아파트별멀티 = 당월_매매_전체[당월_매매_전체["아파트"].isin(아파트)]
                
            st.dataframe(아파트별멀티.reset_index(drop=True).style.background_gradient(subset=['금액','면적'], cmap="Reds"),use_container_width=True)

            if 아파트 :                
                전월당월매매전체 = 갱신[갱신["아파트"].isin(아파트)]
                st.error('📈 시세 동향')
                chart = 차트(전월당월매매전체,y='금액',t=전월당월매매전체)
                st.altair_chart(chart,use_container_width=True)

        with tab2:            
            전월당월전세전체 = 전월당월전세월세[(전월당월전세월세['아파트'].isin(아파트)) & (전월당월전세월세['월세'] == '0')]
            당월_전세_전체 = 당월_전세_전체.reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "종전보증금", "갱신권"])
            if not 아파트:
                당월_전세_전체 = 당월_전세_전체
            else:
                당월_전세_전체 = 당월_전세_전체[당월_전세_전체["아파트"].isin(아파트)]

            st.dataframe(당월_전세_전체.reset_index(drop=True).style.background_gradient(subset=['보증금','면적','종전보증금'], cmap="Reds"),use_container_width=True)

            if 아파트 :
                st.error('📈 시세 동향')
                chart = 차트(전월당월전세전체,y='보증금',t=전월당월전세전체)
                st.altair_chart(chart,use_container_width=True)

        with tab3:
            if not 아파트:
                당월_월세_전체 = 당월_월세_전체
            else:
                당월_월세_전체 = 당월_월세_전체[당월_월세_전체["아파트"].isin(아파트)]
            st.dataframe(당월_월세_전체.reset_index(drop=True).style.background_gradient(subset=['보증금','월세','종전보증금','종전월세'], cmap="Reds"),use_container_width=True)

except Exception as e:
    st.write(e)
    st.error('No data.😎')
