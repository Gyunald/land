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

st.set_page_config(page_title="🎈아파트 실거래가 매매/전세/월세 ",layout='wide')
empty = st.empty()
empty.write('아파트 실거래')
empty.empty()

@st.experimental_memo
def load_lottie(url:str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

@st.experimental_memo
def load_lottie2(url:str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

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

def 매매():
#     매매 = db.collection(f"{datetime.now().day}_trade_{standard_str[:-3]}").document(시군구).get()
    for doc in 시군구데이터.to_dict().values():
        temp = pd.DataFrame(
            [doc.split(',') for doc in doc[1:]],
            columns=["시군구", "아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        temp = temp[["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"]]
        replace_word = '단지','\(.+\)'
        for i in replace_word:
            temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
        temp['금액']= temp['금액'].astype('int64')
        temp['층']= temp['층'].astype('int64')
        temp['건축']= temp['건축'].astype('int64')
        temp['면적'] = temp['면적'].astype('int64')
    return temp.sort_values(by=['아파트'], ascending=True)

def 매매_전일():    
    매매_전일 = db.collection(f"{standard_previous.strftime('%d')}_trade_{standard_previous_str[:-3]}").document(시군구).get()
    for doc2 in 매매_전일.to_dict().values():
        temp3 = pd.DataFrame(
            [doc2.split(',') for doc2 in doc2[1:]],
            columns=["시군구", "아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        temp3 = temp3[["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"]]
        replace_word = '단지','\(.+\)'
        for i in replace_word:
            temp3['아파트'] = temp3['아파트'].str.replace(i,'',regex=True)
        temp3['금액']= temp3['금액'].astype('int64')
        temp3['층']= temp3['층'].astype('int64')
        temp3['건축']= temp3['건축'].astype('int64')
        temp3['면적'] = temp3['면적'].astype('int64')
    return temp3.sort_values(by=['아파트'], ascending=True)

def 임대():
    임대 = db.collection(f"{standard.strftime('%d')}_rent_{standard_str[:-3]}").document(시군구).get()  
    for doc2 in 임대.to_dict().values():
        temp2 = pd.DataFrame(
            [doc.split(',') for doc in doc2[1:]],
            columns=["시군구", "아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"])
        temp2 = temp2[["아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"]]
        replace_word = '단지','\(.+\)'
        for i in replace_word:
            temp2['아파트'] = temp2['아파트'].str.replace(i,'',regex=True)
        temp2['보증금']= temp2['보증금'].astype('int64')
        temp2['층']= temp2['층'].astype('int64')
        temp2['월세']= temp2['월세'].astype('int64')
        temp2['건축']= temp2['건축'].astype('int64')
        temp2['면적']= temp2['면적'].astype('int64')
    return temp2.sort_values(by=['아파트'], ascending=True)

@st.experimental_singleton(ttl=6000)
def 실거래(url, city, date, user_key, rows):
    url = url + "?&LAWD_CD=" + city
    url = url + "&DEAL_YMD=" + date[:6]
    url = url + "&serviceKey=" + user_key
    url = url + "&numOfRows=" + rows

    xml = requests.get(url)
    result = xml.text
    soup = BeautifulSoup(result, 'lxml-xml')
    items = soup.find_all("item")
    aptTrade = pd.DataFrame()
    if len(items) >= 1:
        for item in items:
            if item.find('건축년도') == None :
                continue
            else:               
                계약               =   item.find("년").text + item.find("월").text.zfill(2) + item.find("일").text.zfill(2)
                동                = item.find("법정동").text
                면적               = float(item.find("전용면적").text)
                아파트              = item.find("아파트").text.replace(',','.')
                층                 = int(item.find("층").text)
                건축                = int(item.find("건축년도").text)
                
                if 'getRTMSDataSvcAptRent' in url:
                    보증금           = int(item.find("보증금액").text.replace(',',''))
                    월세             = int(item.find("월세금액").text.replace(',','').replace(' ','0'))
                    갱신권           = item.find("갱신요구권사용").text.strip()
                    종전보증금        = int(item.find("종전계약보증금").text.replace(',','').replace(' ','0'))
                    종전월세         = int(item.find("종전계약월세").text.replace(',','').replace(' ','0'))
                    temp = pd.DataFrame([[아파트, 보증금, 층, 월세, 면적, 건축, 동, 계약, 종전보증금, 종전월세, 갱신권,]], 
                                columns=["아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"])
                else:
                    거래            = item.find("거래유형").text
                    금액            = int(item.find("거래금액").text.replace(',','').strip())
                    파기            = item.find("해제사유발생일").text.strip()
                    temp = pd.DataFrame([[아파트, 금액, 층,면적, 건축, 계약 ,동, 거래, 파기]], 
                                    columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])            
                aptTrade = pd.concat([aptTrade,temp])

        replace_word = '아파트','마을','신도시'
        for i in replace_word:
            aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)

        aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
        aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.0f}'.format).astype(int)
        aptTrade['동'] = aptTrade['동'].str.split().str[0]

    else:
        return Exception

    return aptTrade.sort_values(by=['아파트'], ascending=True)

if not firebase_admin._apps:
    cred = credentials.Certificate({
    "type": st.secrets.type,
    "project_id": st.secrets.project_id,
    "private_key_id": st.secrets.private_key_id,
    "private_key": st.secrets.private_key,
    "client_email": st.secrets.client_email,
    "client_id": st.secrets.client_id,
    "auth_uri": st.secrets.auth_uri,
    "token_uri": st.secrets.token_uri,
    "auth_provider_x509_cert_url": st.secrets.auth_provider_x509_cert_url,
    "client_x509_cert_url": st.secrets.client_x509_cert_url
    })
    app = firebase_admin.initialize_app(cred)
    
db = firestore.client()

file_1 = pd.read_csv('https://raw.githubusercontent.com/Gyunald/land/main/address.csv',encoding='cp949')
user_key = 'pRcMh3ZvTSWhUPu4VIMig%2BbD1mnLgAyaxyhB07a86H8XbgJ7ki8JYqk3a6Q6lM%2FN8zhvYZHQsLw0pmbjPBBE%2FA%3D%3D'
rows = '9999'

lottie_url = 'https://assets9.lottiefiles.com/packages/lf20_2v2beqrh.json'
lottie_json = load_lottie(lottie_url)
lottie_url2 = 'https://assets1.lottiefiles.com/packages/lf20_yJ8wNO.json'
lottie_json2 = load_lottie2(lottie_url2)


st_lottie(
    lottie_json,
    speed=2,
    # reverse='Ture',
    loop=True,
    quality='low',
    )

c1,c2 = st.columns([1,1])

try:
    with c1 :
        empty = st.empty()
        standard = empty.date_input('🧁 날짜', datetime.utcnow()+timedelta(hours=9),key='standard_date_1')
        standard_previous = standard - timedelta(days=1)
        day_num = datetime.isoweekday(standard)

        if day_num == 1 :
            standard = standard-timedelta(days=2)
            standard_previous = standard_previous-timedelta(days=2)
        elif day_num == 2:
            standard_previous = standard_previous-timedelta(days=2)
        elif day_num == 7:            
            standard = standard-timedelta(days=1)
            standard_previous = standard_previous-timedelta(days=1)
            
        if standard.day == 1 :
            standard = standard-timedelta(days=1)
            standard_previous = standard.replace(day=1) - timedelta(days=1)
        
        standard_str = standard.strftime('%y.%m.%d')
        standard_previous_str = standard_previous.strftime('%y.%m.%d')

    with c2:
        시군구 = st.selectbox('🍔 시군구 검색', [i for i in file_1["법정동명"]],index=105) # 22 강남 105 파주
        
    시군구데이터 = db.collection(f"{standard.strftime('%d')}_trade_{standard_str[:-3]}").document(시군구).get()
    file_2 = file_1[file_1['법정동명'].str.contains(시군구)].astype(str)

    if 시군구데이터.exists:
        temp = 매매()
        temp2 = 임대()
        if standard == datetime.utcnow().date():
            temp3 = 매매_전일()
            신규 = pd.merge(temp,temp3, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
            
        매매_당월 = temp[temp['계약'].str.contains(standard_str[:5])].drop_duplicates()
        전세_당월 = temp2[(temp2['계약'].str.contains(standard_str[:5])) & (temp2['월세'] == 0)].drop_duplicates()
        전세_당월 = 전세_당월.reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "종전보증금", "갱신권"])        
        월세_당월 = temp2[(temp2['계약'].str.contains(standard_str[:5])) & (temp2['월세'] != 0)].drop_duplicates()
        매매_임대 = pd.concat([매매_당월,전세_당월,월세_당월])

        if standard_str[-2:] == str(datetime.utcnow().strftime('%d')):
            if len(신규) >= 1:
                with st.expander(f'{시군구.split()[-1]} {datetime.utcnow().day}일 - 신규 {len(신규)}건',expanded=True):
                    st.success('🍰 신규매매')
                    st.dataframe(신규.reset_index(drop=True).style.background_gradient(subset=['금액','면적'], cmap="Reds"),use_container_width=True)
        
        with st.expander(f'{시군구.split()[-1]} {datetime.utcnow().month}월 - 전체',expanded=True):
            아파트 = st.multiselect('🍞 아파트별',sorted([i for i in 매매_임대["아파트"].drop_duplicates()]),max_selections=3)
            st.warning('🍣 다중선택가능')
            tab1, tab2, tab3 = st.tabs([f"매매 {len(매매_당월)}", f"전세 {len(전세_당월)}", f"월세 {len(월세_당월)}"])
            
            with tab1:
                if not 아파트:
                    아파트별 = 매매_당월
                else:
                    아파트별 = 매매_당월[매매_당월["아파트"].isin(아파트)]
                    
                st.dataframe(아파트별.sort_values(by=['아파트'], ascending=True).reset_index(drop=True).style.background_gradient(subset=['금액','면적'], cmap="Reds"),use_container_width=True)
                
                if 아파트 :
                    매매_전월당월_전체 = temp[temp["아파트"].isin(아파트)]
                    st.error('🥯 시세 동향')
                    chart = 차트(매매_전월당월_전체,y='금액',t=매매_전월당월_전체)
                    st.altair_chart(chart,use_container_width=True)
                    
            with tab2:
                # 아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 전세_당월["아파트"].drop_duplicates()]),max_selections=3)
                if not 아파트:
                    전세_당월 = 전세_당월
                else:
                    전세_당월 = 전세_당월[전세_당월["아파트"].isin(아파트)]

                st.dataframe(전세_당월.sort_values(by=['아파트'], ascending=True).reset_index(drop=True).style.background_gradient(subset=['보증금','면적','종전보증금'], cmap="Reds"),use_container_width=True)

                if 아파트 :
                    전세_전월당월_전체 = temp2[(temp2['아파트'].isin(아파트)) & (temp2['월세'] == 0)]
                    st.error('🥯 시세 동향')
                    chart = 차트(전세_전월당월_전체,y='보증금',t=전세_전월당월_전체)
                    st.altair_chart(chart,use_container_width=True)
                    
            with tab3: 
                # 아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 월세_당월["아파트"].drop_duplicates()]),max_selections=3)
                if not 아파트:
                    월세_당월 = 월세_당월
                else:
                    월세_당월 = 월세_당월[월세_당월["아파트"].isin(아파트)]
                st.dataframe(월세_당월.sort_values(by=['아파트'], ascending=True).reset_index(drop=True).style.background_gradient(subset=['보증금','월세','종전보증금','종전월세'], cmap="Reds"),use_container_width=True)
    else:
        with st_lottie_spinner(lottie_json2):
            # empty.empty()
            standard = empty.date_input('🍳 날짜', datetime.utcnow(),key='standard_date_2')
            standard_previous = standard.replace(day=1) - timedelta(days=1)

            if standard.day == 1 :
                standard = standard-timedelta(days=1)
                standard_previous = standard.replace(day=1) - timedelta(days=1)

            standard_str = standard.strftime('%Y.%m')
            standard_previous_str = standard_previous.strftime('%Y.%m')

            urls= ['http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev', 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?']
            city = file_2.iloc[0,0][:5]

            api_trade = pd.concat([실거래(urls[0], city, standard.strftime('%Y%m'), user_key, rows),실거래(urls[0], city, standard_previous.strftime('%Y%m'), user_key, rows)]).drop_duplicates()

            api_rent = pd.concat([실거래(urls[1], city, standard.strftime('%Y%m'), user_key, rows),실거래(urls[1], city, standard_previous.strftime('%Y%m'), user_key, rows)]).reset_index(drop=True).drop_duplicates()
        
        매매_계약월별 = api_trade[api_trade['계약'].str.contains(standard_str[2:])]
        전세_계약월별 = api_rent[(api_rent['계약'].str.contains(standard_str[2:])) & (api_rent['월세'] == 0)].reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "종전보증금", "갱신권"])
        월세_계약월별 = api_rent[(api_rent['계약'].str.contains(standard_str[4:])) & (api_rent['월세'] != 0)]
        매매_임대_계약월별 = pd.concat([매매_계약월별,전세_계약월별,월세_계약월별])
        
        with st.expander(f'{시군구} 실거래 - {standard_str[5:]}월 🍩 전체',expanded=True):
            아파트 = st.multiselect('🍞 아파트별',sorted([i for i in 매매_임대_계약월별["아파트"].drop_duplicates()]),max_selections=3)
            st.warning('🚥 다중선택가능')
            
            tab1, tab2, tab3 = st.tabs([f"매매 {len(매매_계약월별)}", f"전세 {len(전세_계약월별)}", f"월세 {len(월세_계약월별)}"])
            
            with tab1 :
                if not 아파트:
                    매매_데이터프레임 = 매매_계약월별
                else:
                    매매_데이터프레임 = 매매_계약월별[매매_계약월별["아파트"].isin(아파트)]
                    
                st.dataframe(매매_데이터프레임.reset_index(drop=True).style.background_gradient(subset=['금액','면적'], cmap="Reds"),use_container_width=True)

                if 아파트 :                
                    매매_차트 = api_trade[api_trade["아파트"].isin(아파트)]
                    st.error('🥯 시세 동향')
                    chart = 차트(매매_차트,y='금액',t=매매_차트)
                    st.altair_chart(chart,use_container_width=True)
                    
            with tab2:
                if not 아파트:
                    전세_데이터프레임 = 전세_계약월별
                else:
                    전세_데이터프레임 = 전세_계약월별[전세_계약월별["아파트"].isin(아파트)]

                st.dataframe(전세_데이터프레임.reset_index(drop=True).style.background_gradient(subset=['보증금','면적','종전보증금'], cmap="Reds"),use_container_width=True)

                if 아파트 :
                    전세_차트 = api_rent[(api_rent['아파트'].isin(아파트)) & (api_rent['월세'] == '0')]
                    st.error('🥯 시세 동향')
                    chart = 차트(전세_차트,y='보증금',t=전세_차트)
                    st.altair_chart(chart,use_container_width=True)
                    
            with tab3:
                if not 아파트:
                    월세_데이터프레임 = 월세_계약월별
                else:
                    월세_데이터프레임 = 월세_계약월별[월세_계약월별["아파트"].isin(아파트)]
                    
                st.dataframe(월세_데이터프레임.reset_index(drop=True).style.background_gradient(subset=['보증금','월세','종전보증금','종전월세'], cmap="Reds"),use_container_width=True)
except Exception as e:
    st.write(e)
    st.error('No data 😎')
