import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request as req
import datetime
import requests
from streamlit_lottie import st_lottie,st_lottie_spinner
import altair as alt

st.set_page_config(page_title="๐์ํํธ ์ค๊ฑฐ๋๊ฐ ๋งค๋งค/์ ์ธ/์์ธ ",layout='wide')
empty = st.empty()
empty.write('์ํํธ ์ค๊ฑฐ๋')
empty.empty()

@st.experimental_singleton
# @st.experimental_memo   
def ๋งค๋งค(city, date, user_key, rows):
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
        ๊ณ์ฝ            = str(item.find('๋').text + item.find('์').text + item.find('์ผ').text)
        # ๊ณ์ฝ            = str(item.find('์').text + item.find('์ผ').text)
        ๋                  = item.find("๋ฒ์ ๋").text
        ๋ฉด์             = float(item.find("์ ์ฉ๋ฉด์ ").text)
        ์ํํธ              = item.find("์ํํธ").text
        ์ธต                  = int(item.find("์ธต").text)
        ๊ธ์ก            = item.find("๊ฑฐ๋๊ธ์ก").text
        ๊ฑด์ถ            = int(item.find("๊ฑด์ถ๋๋").text)
        ๊ฑฐ๋            = item.find("๊ฑฐ๋์ ํ").text
        ํ๊ธฐ      = item.find("ํด์ ์ฌ์ ๋ฐ์์ผ").text
        temp = pd.DataFrame(([[์ํํธ, ๊ธ์ก, ์ธต,๋ฉด์ , ๊ฑด์ถ, ๊ณ์ฝ ,๋, ๊ฑฐ๋, ํ๊ธฐ]]), 
                            columns=["์ํํธ", "๊ธ์ก", "์ธต", "๋ฉด์ ", "๊ฑด์ถ", "๊ณ์ฝ", "๋", "๊ฑฐ๋", "ํ๊ธฐ"])
        aptTrade = pd.concat([aptTrade,temp])
    replace_word = 'ํ์ฃผ','์ํํธ','๋ง์','์ ๋์','๋จ์ง',r'\(.+\)','์ค๊ฐ๊ฑฐ๋','๊ฑฐ๋'
    for i in replace_word:
        aptTrade['์ํํธ'] = aptTrade['์ํํธ'].str.replace(i,'',regex=True)
        aptTrade['๊ฑฐ๋'] = aptTrade['๊ฑฐ๋'].str.replace(i,'',regex=True)
    aptTrade['๊ธ์ก'] = aptTrade['๊ธ์ก'].str.replace(',','').astype(int)
    aptTrade['ํ๊ธฐ'] = aptTrade['ํ๊ธฐ'].str.replace('22.','',regex=True)
    aptTrade['๊ณ์ฝ'] = pd.to_datetime(aptTrade['๊ณ์ฝ'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    # aptTrade['๊ณ์ฝ'] = pd.to_datetime(aptTrade['๊ณ์ฝ'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['๋ฉด์ '] = aptTrade['๋ฉด์ '].astype(float).map('{:.2f}'.format).str.split('.').str[0]
    aptTrade['๋'] = aptTrade['๋'].str.split().str[0]
    return aptTrade.sort_values(by=['์ํํธ'], ascending=True)

@st.experimental_singleton
# @st.experimental_memo   
def ์๋(city, date, user_key, rows):
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
        ๊ณ์ฝ            = str(item.find('๋').text + item.find('์').text + item.find('์ผ').text)
        # ๊ณ์ฝ            = str(item.find('์').text + item.find('์ผ').text)
        ๋                  = item.find("๋ฒ์ ๋").text
        ๋ฉด์             = float(item.find("์ ์ฉ๋ฉด์ ").text)
        ์ํํธ              = item.find("์ํํธ").text
        ์ธต                  = int(item.find("์ธต").text)
        ๋ณด์ฆ๊ธ            = item.find("๋ณด์ฆ๊ธ์ก").text
        ๊ฑด์ถ            = int(item.find("๊ฑด์ถ๋๋").text)
        ์์ธ            = item.find("์์ธ๊ธ์ก").text
        ๊ฐฑ์ ๊ถ            = item.find("๊ฐฑ์ ์๊ตฌ๊ถ์ฌ์ฉ").text
        ๊ธฐ๊ฐ            = item.find("๊ณ์ฝ๊ธฐ๊ฐ").text
        ์ข์ ๋ณด์ฆ๊ธ        = item.find("์ข์ ๊ณ์ฝ๋ณด์ฆ๊ธ").text
        ์ข์ ์์ธ        = item.find("์ข์ ๊ณ์ฝ์์ธ").text 
        temp = pd.DataFrame(([[์ํํธ, ๋ณด์ฆ๊ธ, ์ธต, ์์ธ, ๋ฉด์ , ๊ฑด์ถ, ๋, ๊ณ์ฝ, ๊ธฐ๊ฐ,  ์ข์ ๋ณด์ฆ๊ธ,์ข์ ์์ธ, ๊ฐฑ์ ๊ถ,]]), 
                            columns=["์ํํธ", "๋ณด์ฆ๊ธ", "์ธต", "์์ธ", "๋ฉด์ ", "๊ฑด์ถ","๋", "๊ณ์ฝ", "๊ธฐ๊ฐ", "์ข์ ๋ณด์ฆ๊ธ", "์ข์ ์์ธ", "๊ฐฑ์ ๊ถ"])
        aptTrade = pd.concat([aptTrade,temp])
        
    replace_word = 'ํ์ฃผ','์ํํธ','๋ง์','์ ๋์','๋จ์ง','\(.+\)'
    for i in replace_word:
        aptTrade['์ํํธ'] = aptTrade['์ํํธ'].str.replace(i,'',regex=True)
    aptTrade['๋ณด์ฆ๊ธ'] = aptTrade['๋ณด์ฆ๊ธ'].str.replace(',','')
    aptTrade['์ข์ ๋ณด์ฆ๊ธ'] = aptTrade['์ข์ ๋ณด์ฆ๊ธ'].str.replace(',','')
    aptTrade['๊ธฐ๊ฐ'] = aptTrade['๊ธฐ๊ฐ'].str[6:]
    aptTrade['๊ณ์ฝ'] = pd.to_datetime(aptTrade['๊ณ์ฝ'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    # aptTrade['๊ณ์ฝ'] = pd.to_datetime(aptTrade['๊ณ์ฝ'],format = "%m%d").dt.strftime('%m.%d')
    aptTrade['๋ฉด์ '] = aptTrade['๋ฉด์ '].map('{:.2f}'.format).str.split('.').str[0]
    aptTrade['๋'] = aptTrade['๋'].str.split().str[0]
    return aptTrade.sort_values(by=['์ํํธ'], ascending=True)

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

def ๋งค๋งค์ฐจํธ๋จ์ผ(data):
    hover = alt.selection_single(
        fields=["๊ธ์ก"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๊ธ์ก",title=None),
            color=alt.Color("๋ฉด์ ",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๊ธ์ก",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(.7)),
            tooltip=[
                alt.Tooltip("๋ฉด์ ", title="๋ฉด์ "),
                alt.Tooltip("๊ธ์ก", title="๊ธ์ก"),
                alt.Tooltip("์ํํธ", title="์ํํธ"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def ๋งค๋งค์ฐจํธ๋ค์ค(data):
    hover = alt.selection_single(
        fields=["๊ธ์ก"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๊ธ์ก",title=None),
            color=alt.Color("์ํํธ",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๊ธ์ก",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("๋ฉด์ ", title="๋ฉด์ "),
                alt.Tooltip("๊ธ์ก", title="๊ธ์ก"),
                alt.Tooltip("์ํํธ", title="์ํํธ"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def ์๋์ฐจํธ๋จ์ผ(data):
    hover = alt.selection_single(
        fields=["๋ณด์ฆ๊ธ"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๋ณด์ฆ๊ธ",title=None),
            color=alt.Color("๋ฉด์ ",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๋ณด์ฆ๊ธ",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(.7)),
            tooltip=[
                alt.Tooltip("๋ฉด์ ", title="๋ฉด์ "),
                alt.Tooltip("๋ณด์ฆ๊ธ", title="๋ณด์ฆ๊ธ"),
                alt.Tooltip("์ํํธ", title="์ํํธ"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def ์๋์ฐจํธ๋ค์ค(data):
    hover = alt.selection_single(
        fields=["๋ณด์ฆ๊ธ"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๋ณด์ฆ๊ธ",title=None),
            color=alt.Color("์ํํธ",legend=alt.Legend(orient='bottom', direction='vertical')),
        )
    )
    points = lines.transform_filter(hover).mark_circle(size=100) #65
    tooltips = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x=alt.X("๊ณ์ฝ",title=None),
            y=alt.Y("๋ณด์ฆ๊ธ",title=None),
            opacity=alt.condition(hover, alt.value(0.1), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("๋ฉด์ ", title="๋ฉด์ "),
                alt.Tooltip("๋ณด์ฆ๊ธ", title="๋ณด์ฆ๊ธ"),
                alt.Tooltip("์ํํธ", title="์ํํธ"),
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
            date = st.date_input('๐ณ ๋ ์ง',value= datetime.date.today()+ datetime.timedelta(hours=14)).strftime('%Y%m')
            date_2 = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=datetime.datetime.now().day).strftime('%m.')

        with c2:
            ์๊ตฐ๊ตฌ = st.selectbox('๐ฐ ์๊ตฐ๊ตฌ ๊ฒ์', sorted([i for i in set(file_1["๋ฒ์ ๋๋ช"])]),index=230) # 93 ๊ฐ๋จ 230 ํ์ฃผ

            file_2 = file_1[file_1['๋ฒ์ ๋๋ช'].str.contains(์๊ตฐ๊ตฌ)].astype(str)
            city = file_2.iloc[0,0][:5]

            # ์ค๋ = datetime.datetime.now().strftime('%Y%m%d')    
        ๋น์ = datetime.datetime(year=int(date[:3 + 1]),month=int(date[4:5 + 1]),day=datetime.datetime.now().day)
        ์ ์ = ๋น์ - datetime.timedelta(days=30)
        # ์ด์  = datetime.datetime.now() - datetime.timedelta(days=1)
        ๊ฐฑ์  = pd.concat([๋งค๋งค(city, ๋น์.strftime('%Y%m%d'), user_key, rows),๋งค๋งค(city, ์ ์.strftime('%Y%m%d'), user_key, rows),]).reset_index(drop=True).drop_duplicates()

        ๋น์_๋งค๋งค_์ ์ฒด = ๊ฐฑ์ [๊ฐฑ์ ['๊ณ์ฝ'].str.contains(date_2)]
        ์ ์๋น์์ ์ธ์์ธ = pd.concat([์๋(city, ๋น์.strftime('%Y%m%d'), user_key, rows),์๋(city, ์ ์.strftime('%Y%m%d'), user_key, rows),]).reset_index(drop=True).drop_duplicates()
#         ์ ์๋น์์ ์ธ์์ธ = ์๋(city, ๋น์.strftime('%Y%m%d'), user_key, rows)

        ๋น์_์ ์ธ_์ ์ฒด = ์ ์๋น์์ ์ธ์์ธ[(์ ์๋น์์ ์ธ์์ธ['๊ณ์ฝ'].str.contains(date_2)) & (์ ์๋น์์ ์ธ์์ธ['์์ธ'] == '0')].drop(columns=['์์ธ']).reset_index(drop=True)
        ๋น์_์์ธ_์ ์ฒด = ์ ์๋น์์ ์ธ์์ธ[(์ ์๋น์์ ์ธ์์ธ['๊ณ์ฝ'].str.contains(date_2)) & (์ ์๋น์์ ์ธ์์ธ['์์ธ'] != '0')].reset_index(drop=True)
    
#     ๊ณ ์  = pd.read_csv(st.secrets.fixed_data, encoding='cp949').drop(columns=['Unnamed: 0'])    
#     ๊ณ ์ ['๋ฉด์ '] = ๊ณ ์ ['๋ฉด์ '].map('{:.2f}'.format)
#     ๊ณ ์ ['๊ณ์ฝ'] = ๊ณ ์ ['๊ณ์ฝ'].map('{:.2f}'.format)
#     ๊ณ ์ ['๊ธ์ก'] = ๊ณ ์ ['๊ธ์ก'].astype(int)
#     ๊ณ ์  = ๊ณ ์ .fillna('')
#     ์ ๊ท = pd.merge(๊ฐฑ์ ,๊ณ ์ , how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)

    with st.expander(f'{์๊ตฐ๊ตฌ} ์ค๊ฑฐ๋ - {date[4:5+1]}์ ๐ฉ ์ ์ฒด',expanded=True):
        if len(๊ฐฑ์ ) == 0 :
            st.info(f'{date[4:5+1]}์ ์ ๊ท ๋ฑ๋ก์ด ์์ต๋๋ค๐')
        tab1, tab2, tab3 = st.tabs([f"๋งค๋งค {len(๋น์_๋งค๋งค_์ ์ฒด)}", f"์ ์ธ {len(๋น์_์ ์ธ_์ ์ฒด)}", f"์์ธ {len(๋น์_์์ธ_์ ์ฒด)}"])

        with tab1 :
            ์ํํธ = st.multiselect('๐ ์ํํธ๋ณ',sorted([i for i in ๋น์_๋งค๋งค_์ ์ฒด["์ํํธ"].drop_duplicates()]),max_selections=5)
            ๋น์์ ์๋งค๋งค์ํํธ๋ณ = ๊ฐฑ์ [๊ฐฑ์ ["์ํํธ"].isin(์ํํธ)].reset_index(drop=True)
            st.warning('๐ฅ ๋จ์ผ์ ํ ๋ฉด์ ๋ณ, ๋ค์ค์ ํ ์ํํธ๋ณ')
            if not ์ํํธ:            
                ์ํํธ๋ณ๋ฉํฐ = ๋น์_๋งค๋งค_์ ์ฒด
            else:
                ์ํํธ๋ณ๋ฉํฐ = ๋น์_๋งค๋งค_์ ์ฒด[๋น์_๋งค๋งค_์ ์ฒด["์ํํธ"].isin(์ํํธ)].reset_index(drop=True)
            st.dataframe(์ํํธ๋ณ๋ฉํฐ.style.background_gradient(subset=['๊ธ์ก','๋ฉด์ '], cmap="Reds"),use_container_width=True)

            if len(์ํํธ) == 1:
                st.error('๐ ์์ธ ๋ํฅ')
                chart = ๋งค๋งค์ฐจํธ๋จ์ผ(๋น์์ ์๋งค๋งค์ํํธ๋ณ)
                st.altair_chart(chart,use_container_width=True)
            elif len(์ํํธ) > 1 :
                st.error('๐ ์์ธ ๋ํฅ')
                chart = ๋งค๋งค์ฐจํธ๋ค์ค(๋น์์ ์๋งค๋งค์ํํธ๋ณ)
                st.altair_chart(chart,use_container_width=True)

        with tab2:
            ์ํํธ = st.multiselect('๐ ์ํํธ๋ณ',sorted([i for i in ๋น์_์ ์ธ_์ ์ฒด["์ํํธ"].drop_duplicates()]),max_selections=5)
            st.warning('๐ฅ ๋จ์ผ์ ํ ๋ฉด์ ๋ณ, ๋ค์ค์ ํ ์ํํธ๋ณ')
            ์ ์๋น์์ ์ธ์ ์ฒด = ์ ์๋น์์ ์ธ์์ธ[(์ ์๋น์์ ์ธ์์ธ['์ํํธ'].isin(์ํํธ)) & (์ ์๋น์์ ์ธ์์ธ['์์ธ'] == '0')].reset_index(drop=True)
            ๋น์_์ ์ธ_์ ์ฒด = ๋น์_์ ์ธ_์ ์ฒด.reindex(columns=["์ํํธ", "๋ณด์ฆ๊ธ", "์ธต", "๋ฉด์ ", "๊ฑด์ถ", "๋", "๊ณ์ฝ", "๊ธฐ๊ฐ", "์ข์ ๋ณด์ฆ๊ธ", "๊ฐฑ์ ๊ถ"])
            if not ์ํํธ:
                ๋น์_์ ์ธ_์ ์ฒด = ๋น์_์ ์ธ_์ ์ฒด
            else:
                ๋น์_์ ์ธ_์ ์ฒด = ๋น์_์ ์ธ_์ ์ฒด[๋น์_์ ์ธ_์ ์ฒด["์ํํธ"].isin(์ํํธ)].reset_index(drop=True)
            st.dataframe(๋น์_์ ์ธ_์ ์ฒด.style.background_gradient(subset=['๋ณด์ฆ๊ธ','๋ฉด์ '], cmap="Reds"),use_container_width=True)

            if len(์ํํธ) == 1:
                st.error('๐ ์์ธ ๋ํฅ')
                chart = ์๋์ฐจํธ๋จ์ผ(์ ์๋น์์ ์ธ์ ์ฒด)
                st.altair_chart(chart,use_container_width=True)
            elif len(์ํํธ) > 1 :
                st.error('๐ ์์ธ ๋ํฅ')
                chart = ์๋์ฐจํธ๋ค์ค(์ ์๋น์์ ์ธ์ ์ฒด)
                st.altair_chart(chart,use_container_width=True)
        with tab3:
            ์ํํธ = st.multiselect('๐ ์ํํธ๋ณ',sorted([i for i in ๋น์_์์ธ_์ ์ฒด["์ํํธ"].drop_duplicates()]),max_selections=5)
            st.warning('๐ฅ ๋จ์ผ์ ํ ๋ฉด์ ๋ณ, ๋ค์ค์ ํ ์ํํธ๋ณ')
            
            if not ์ํํธ:
                ๋น์_์์ธ_์ ์ฒด = ๋น์_์์ธ_์ ์ฒด
            else:
                ๋น์_์์ธ_์ ์ฒด = ๋น์_์์ธ_์ ์ฒด[๋น์_์์ธ_์ ์ฒด["์ํํธ"].isin(์ํํธ)].reset_index(drop=True)


            col_loc = ๋น์_์์ธ_์ ์ฒด.columns.get_loc('๋ณด์ฆ๊ธ') ## ์ํ๋ ์นผ๋ผ์ ์ธ๋ฑ์ค
            st.dataframe(๋น์_์์ธ_์ ์ฒด.style.background_gradient(subset=['๋ณด์ฆ๊ธ','์์ธ'], cmap="Reds"),use_container_width=True)
            # .set_index(['์ํํธ'])
            # .style.background_gradient(subset=['๋ณด์ฆ๊ธ','์์ธ'], cmap="Reds")
except Exception as e:
    st.write(e)
    st.error('No data.๐')
