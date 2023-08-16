import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import requests
# from streamlit_lottie import st_lottie,st_lottie_spinner
import altair as alt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

st.set_page_config(page_title="🎈아파트 실거래가 매매/전세/월세 ") # layout='wide'

# @st.cache_data
# def load_lottie(url:str):
#     r = requests.get(url)
#     if r.status_code != 200:
#         return None
#     return r.json()

# @st.cache_data
# def load_lottie2(url:str):
#     r = requests.get(url)
#     if r.status_code != 200:
#         return None
#     return r.json()

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
@st.cache_data
def 매매(get_매매):
    temp = pd.DataFrame(
    [i.split(',') for i in get_매매], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format).astype(int)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = temp['금액'].str.replace(',','').astype('int64')
    replace_word = '아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
    temp['층']= temp['층'].astype('int64')
    temp['면적'] = temp['면적'].astype('int64')
    return temp.sort_values(by=['아파트'], ascending=True)

@st.cache_data
def 매매_전일(get_매매전일):    
    temp3 = pd.DataFrame(
    [i.split(',') for i in get_매매전일], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"]
)
    temp3['계약'] = pd.to_datetime(temp3['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    temp3['면적'] = temp3['면적'].astype(float).map('{:.0f}'.format).astype(int)
    temp3['동'] = temp3['동'].str.split().str[0]
    temp3['금액'] = temp3['금액'].str.replace(',','').astype('int64')
    replace_word = '아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        temp3['아파트'] = temp3['아파트'].str.replace(i,'',regex=True)
    temp3['층']= temp3['층'].astype('int64')
    temp3['면적'] = temp3['면적'].astype('int64')
    return temp3.sort_values(by=['아파트'], ascending=True)

@st.cache_data
def 임대(get_임대):
    temp2 = pd.DataFrame(
    [i.split(',') for i in get_임대], columns=["아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"]
    )        
    temp2['계약'] = pd.to_datetime(temp2['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
    temp2['면적'] = temp2['면적'].astype(float).map('{:.0f}'.format).astype(int)
    temp2['동'] = temp2['동'].str.split().str[0]
    replace_word = '아파트','마을','신도시','단지','\(.+\)'
    for i in replace_word:
        temp2['아파트'] = temp2['아파트'].str.replace(i,'',regex=True)
    temp2['보증금']= temp2['보증금'].str.replace(',','').astype('int64')
    temp2['층']= temp2['층'].astype('int64')
    temp2['월세']= temp2['월세'].str.replace(',','').astype('int64')
    temp2['건축']= temp2['건축'].astype('int64')
    temp2['면적']= temp2['면적'].astype('int64')
    return temp2.sort_values(by=['아파트'], ascending=True)

@st.cache_resource(ttl=6000)
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
                계약               = item.find("년").text + item.find("월").text.zfill(2) + item.find("일").text.zfill(2)
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
                    temp = pd.DataFrame([[아파트, 보증금, 월세, 층, 면적, 건축, 동, 계약, 종전보증금, 종전월세, 갱신권,]], 
                                columns=["아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"])
                else:
                    거래            = item.find("거래유형").text
                    금액            = int(item.find("거래금액").text.replace(',','').strip())
                    파기            = item.find("해제사유발생일").text.strip()
                    temp = pd.DataFrame([[아파트, 금액, 층, 면적, 건축, 계약 ,동, 거래, 파기]], 
                                    columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])            
                aptTrade = pd.concat([aptTrade,temp])

        replace_word = '아파트','마을','신도시','단지','\(.+\)'
        for i in replace_word:
            aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)

        aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
        aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.0f}'.format).astype(int)
        aptTrade['동'] = aptTrade['동'].str.split().str[0]
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
address = {'서울특별시 종로구': '11110', '서울특별시 중구': '11140', '서울특별시 용산구': '11170', '서울특별시 성동구': '11200', '서울특별시 광진구': '11215', '서울특별시 동대문구': '11230', '서울특별시 중랑구': '11260', 
           '서울특별시 성북구': '11290', '서울특별시 강북구': '11305', '서울특별시 도봉구': '11320', '서울특별시 노원구': '11350', '서울특별시 은평구': '11380', '서울특별시 서대문구': '11410', '서울특별시 마포구': '11440',
           '서울특별시 양천구': '11470', '서울특별시 강서구': '11500', '서울특별시 구로구': '11530', '서울특별시 금천구': '11545', '서울특별시 영등포구': '11560', '서울특별시 동작구': '11590', '서울특별시 관악구': '11620',
           '서울특별시 서초구': '11650', '서울특별시 강남구': '11680', '서울특별시 송파구': '11710', '서울특별시 강동구': '11740', '부산광역시 중구': '26110', '부산광역시 서구': '26140', '부산광역시 동구': '26170', 
           '부산광역시 영도구': '26200', '부산광역시 부산진구': '26230', '부산광역시 동래구': '26260', '부산광역시 남구': '26290', '부산광역시 북구': '26320', '부산광역시 해운대구': '26350', '부산광역시 사하구': '26380', 
           '부산광역시 금정구': '26410', '부산광역시 강서구': '26440', '부산광역시 연제구': '26470', '부산광역시 수영구': '26500', '부산광역시 사상구': '26530', '부산광역시 기장군': '26710', '대구광역시 중구': '27110', 
           '대구광역시 동구': '27140', '대구광역시 서구': '27170', '대구광역시 남구': '27200', '대구광역시 북구': '27230', '대구광역시 수성구': '27260', '대구광역시 달서구': '27290', '대구광역시 달성군': '27710', 
           '인천광역시 중구': '28110', '인천광역시 동구': '28140', '인천광역시 미추홀구': '28177', '인천광역시 연수구': '28185', '인천광역시 남동구': '28200', '인천광역시 부평구': '28237', '인천광역시 계양구': '28245',
           '인천광역시 서구': '28260', '인천광역시 강화군':'28710', '광주광역시 동구': '29110', '광주광역시 서구': '29140', '광주광역시 남구': '29155', '광주광역시 북구': '29170', '광주광역시 광산구': '29200',
           '대전광역시 동구': '30110', '대전광역시 중구': '30140', '대전광역시 서구': '30170', '대전광역시 유성구': '30200', '대전광역시 대덕구': '30230', '울산광역시 중구': '31110', '울산광역시 남구': '31140', 
           '울산광역시 동구': '31170', '울산광역시 북구': '31200', '울산광역시 울주군': '31710', '세종특별자치시': '36110', '수원시 장안구': '41111', '수원시 권선구': '41113', '수원시 팔달구': '41115', '수원시 영통구': '41117', 
           '성남시 수정구': '41131', '성남시 중원구': '41133', '성남시 분당구': '41135', '의정부시': '41150', '안양시 만안구': '41171', '안양시 동안구': '41173', '부천시': '41190', '광명시': '41210', '평택시': '41220', 
           '동두천시': '41250', '안산시 상록구': '41271', '안산시 단원구': '41273', '고양시 덕양구': '41281', '고양시 일산동구': '41285', '고양시 일산서구': '41287', '과천시': '41290', '구리시': '41310', '남양주시': '41360', 
           '오산시': '41370', '시흥시': '41390', '군포시': '41410', '의왕시': '41430', '하남시': '41450', '용인시 처인구': '41461', '용인시 기흥구': '41463', '용인시 수지구': '41465', '파주시': '41480', '이천시': '41500', 
           '안성시': '41550', '김포시': '41570', '화성시': '41590', '광주시': '41610', '양주시': '41630', '포천시': '41650', '여주시': '41670', '연천군': '41800', '가평군': '41820', '양평군': '41830', '춘천시': '51110', 
           '원주시': '51130', '강릉시': '51150', '동해시': '51170', '태백시': '51190', '속초시': '51210', '삼척시': '51230', '홍천군': '51720', '횡성군': '51730', '영월군': '51750', '평창군': '51760', '정선군': '51770', 
           '철원군': '51780', '화천군': '51790', '양구군': '51800', '인제군': '51810', '강원 고성군': '51820', '양양군': '51830', '청주시 상당구': '43111', '청주시 서원구': '43112', '청주시 흥덕구': '43113', 
           '청주시 청원구': '43114', '충주시': '43130', '제천시': '43150', '보은군': '43720', '옥천군': '43730', '영동군': '43740', '증평군': '43745', '진천군': '43750', '괴산군': '43760', '음성군': '43770', 
           '단양군': '43800', '천안시 동남구': '44131', '천안시 서북구': '44133', '공주시': '44150', '보령시': '44180', '아산시': '44200', '서산시': '44210', '논산시': '44230', '계룡시': '44250', '당진시': '44270',
           '금산군': '44710', '부여군': '44760', '서천군': '44770', '청양군': '44790', '홍성군': '44800', '예산군': '44810', '태안군': '44825', '전주시 완산구': '45111', '전주시 덕진구': '45113', '군산시': '45130',
           '익산시': '45140', '정읍시': '45180', '남원시': '45190', '김제시': '45210', '완주군': '45710', '진안군': '45720', '무주군': '45730', '장수군': '45740', '임실군': '45750', '순창군': '45770', '고창군': '45790',
           '부안군': '45800', '목포시': '46110', '여수시': '46130', '순천시': '46150', '나주시': '46170', '광양시': '46230', '담양군': '46710', '곡성군': '46720', '구례군': '46730', '고흥군': '46770', '보성군': '46780',
           '화순군': '46790', '장흥군': '46800', '강진군': '46810', '해남군': '46820', '영암군': '46830', '무안군': '46840', '함평군': '46860', '영광군': '46870', '장성군': '46880', '완도군': '46890', '진도군': '46900',
           '신안군': '46910', '포항시 남구': '47111', '포항시 북구': '47113', '경주시': '47130', '김천시': '47150', '안동시': '47170', '구미시': '47190', '영주시': '47210', '영천시': '47230', '상주시': '47250', 
           '문경시': '47280', '경산시': '47290', '군위군': '47720', '의성군': '47730', '청송군': '47750', '영양군': '47760', '영덕군': '47770', '청도군': '47820', '고령군': '47830', '성주군': '47840', '칠곡군': '47850',
           '예천군': '47900', '봉화군': '47920', '울진군': '47930', '울릉군': '47940', '창원시 의창구': '48121', '창원시 성산구': '48123', '창원시 마산합포구': '48125', '창원시 마산회원구': '48127', '창원시 진해구': '48129',
           '진주시': '48170', '통영시': '48220', '사천시': '48240', '김해시': '48250', '밀양시': '48270', '거제시': '48310', '양산시': '48330', '의령군': '48720', '함안군': '48730', '창녕군': '48740', '경남 고성군': '48820',
           '남해군': '48840', '하동군': '48850', '산청군': '48860', '함양군': '48870', '거창군': '48880', '합천군': '48890', '제주시': '50110', '서귀포시': '50130'}

user_key = st.secrets.user_key
rows = '9999'

# lottie_url = 'https://assets9.lottiefiles.com/packages/lf20_2v2beqrh.json'
# lottie_json = load_lottie(lottie_url)
# lottie_url2 = 'https://assets1.lottiefiles.com/packages/lf20_yJ8wNO.json'
# lottie_json2 = load_lottie2(lottie_url2)


with st.expander('실거래 조회 🎈',expanded=False):
    # st_lottie(lottie_json,speed=2,loop=True,quality='low')# reverse='Ture'
    c1,c2 = st.columns([1,1])
    with c1 :
        empty = st.empty()
        standard = empty.date_input('🧁 날짜', datetime.utcnow()+timedelta(hours=9),key='standard_date_1',max_value=datetime.utcnow()+timedelta(hours=9))
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

        standard_str = standard.strftime('%Y.%m.%d')
        standard_previous_str = standard_previous.strftime('%Y.%m.%d')

    with c2:
        시군구 = st.selectbox('🍔 시군구 검색', [i for i in address],index=104) # 22 강남 104 파주
    
city = address[시군구]
address = {y:x for x,y in address.items()}
법정동명 = address[city]

if standard_str[5:] == (datetime.utcnow()+timedelta(hours=9)).date().strftime('%m.%d'):
    get_매매 = db.collection((datetime.utcnow()+timedelta(hours=9)).date().strftime('%Y.%m.%d')).document(시군구).get().to_dict()['매매']
    get_임대 = db.collection((datetime.utcnow()+timedelta(hours=9)).date().strftime('%Y.%m.%d')).document(시군구).get().to_dict()['임대']
    
    temp = 매매(get_매매)
    temp2 = 임대(get_임대)
    
    매매_당월 = temp[temp['계약'].str.contains(standard_str[5:8])].drop_duplicates()
    전세_당월 = temp2[(temp2['계약'].str.contains(standard_str[5:8])) & (temp2['월세'] == 0)].drop_duplicates()
    전세_당월 = 전세_당월.reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "종전보증금", "갱신권"])        
    월세_당월 = temp2[(temp2['계약'].str.contains(standard_str[5:8])) & (temp2['월세'] != 0)].drop_duplicates()
    매매_임대 = pd.concat([매매_당월,전세_당월,월세_당월])

    if standard_str[-2:] == (datetime.utcnow()+timedelta(hours=9)).strftime('%d'):
        get_매매전일 = db.collection(standard_previous_str).document(시군구).get().to_dict()['매매']
        temp3 = 매매_전일(get_매매전일)
        신규 = pd.merge(temp,temp3, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
        신규 = 신규.reindex(columns=["아파트", "금액","면적", "층", "건축", "계약", "동", "거래", "파기"])
        if len(신규) >= 1:
            with st.expander(f'{법정동명.split()[-1]} {(datetime.utcnow()+timedelta(hours=9)).day}일 - 신규 {len(신규)}건',expanded=True):
                # st.success('🍰 신규매매')
                st.dataframe(신규.sort_values(by=['금액'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)

    with st.expander(f'{법정동명.split()[-1]} {(datetime.utcnow()+timedelta(hours=9)).month}월 - 전체',expanded=False):
        아파트 = st.multiselect('🍞 아파트별',sorted([i for i in 매매_임대["아파트"].drop_duplicates()]),max_selections=3,placeholder= '다중 선택 가능')
        # st.warning('🍣 다중선택가능')
        tab1, tab2, tab3 = st.tabs([f"매매 {len(매매_당월)}", f"전세 {len(전세_당월)}", f"월세 {len(월세_당월)}"])

        with tab1:
            if not 아파트:
                아파트별 = 매매_당월
            else:
                아파트별 = 매매_당월[매매_당월["아파트"].isin(아파트)]
            아파트별 = 아파트별.reindex(columns=["아파트", "금액","면적", "층", "건축", "계약", "동", "거래", "파기"])
            st.dataframe(아파트별.sort_values(by=['금액'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)
            if 아파트 :
                매매_전월당월_전체 = temp[temp["아파트"].isin(아파트)]
                if not 매매_전월당월_전체.empty :
                    # st.error('🥯 시세 동향')
                    chart = 차트(매매_전월당월_전체,y='금액',t=매매_전월당월_전체)
                    st.altair_chart(chart,use_container_width=True)
                else:
                    st.error('No data 😎')

        with tab2:
            # 아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 전세_당월["아파트"].drop_duplicates()]),max_selections=3,placeholder= '다중 선택 가능')
            if not 아파트:
                전세_당월 = 전세_당월
            else:
                전세_당월 = 전세_당월[전세_당월["아파트"].isin(아파트)]

            st.dataframe(전세_당월.sort_values(by=['보증금'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['보증금','면적','종전보증금'], cmap="Reds"),use_container_width=True,hide_index=True)

            if 아파트 :
                전세_전월당월_전체 = temp2[(temp2['아파트'].isin(아파트)) & (temp2['월세'] == 0)]
                if not 전세_전월당월_전체.empty :
                    # st.error('🥯 시세 동향')
                    chart = 차트(전세_전월당월_전체,y='보증금',t=전세_전월당월_전체)
                    st.altair_chart(chart,use_container_width=True)
                else:
                    st.error('No data 😎')

        with tab3: 
            # 아파트 = st.multiselect('🚀 아파트별',sorted([i for i in 월세_당월["아파트"].drop_duplicates()]),max_selections=3)
            if not 아파트:
                월세_당월 = 월세_당월
            else:
                월세_당월 = 월세_당월[월세_당월["아파트"].isin(아파트)]
            st.dataframe(월세_당월.sort_values(by=['월세'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['보증금','월세','종전보증금','종전월세'], cmap="Reds"),use_container_width=True,hide_index=True)

# else:
#     # with st.spinner('실거래 목록 구성중'):
#     standard = empty.date_input('🧁 날짜', datetime.utcnow()+timedelta(hours=9),key='standard_date_2',max_value=datetime.utcnow()+timedelta(hours=9))
#     standard_previous = standard.replace(day=1) - timedelta(days=1)

#     if standard.day == 1 :
#         standard = standard-timedelta(days=1)
#         standard_previous = standard.replace(day=1) - timedelta(days=1)

#     standard_str = standard.strftime('%Y.%m')
#     standard_previous_str = standard_previous.strftime('%Y.%m')

#     urls= ['http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev', 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?']

#     api_trade = pd.concat([실거래(urls[0], city, standard.strftime('%Y%m'), user_key, rows),실거래(urls[0], city, standard_previous.strftime('%Y%m'), user_key, rows)]).drop_duplicates()

#     api_rent = pd.concat([실거래(urls[1], city, standard.strftime('%Y%m'), user_key, rows),실거래(urls[1], city, standard_previous.strftime('%Y%m'), user_key, rows)]).reset_index(drop=True).drop_duplicates()
    
#     매매_계약월별 = api_trade[api_trade['계약'].str.contains(standard_str[2:])]
#     전세_계약월별 = api_rent[(api_rent['계약'].str.contains(standard_str[2:])) & (api_rent['월세'] == 0)].reindex(columns=["아파트", "보증금", "층", "면적", "건축", "동", "계약", "종전보증금", "갱신권"])
#     월세_계약월별 = api_rent[(api_rent['계약'].str.contains(standard_str[4:])) & (api_rent['월세'] != 0)]
#     매매_임대_계약월별 = pd.concat([매매_계약월별,전세_계약월별,월세_계약월별])
    
#     with st.expander(f'{시군구} 실거래 - {standard_str[5:]}월 🍩 전체',expanded=True):
#         아파트 = st.multiselect('🍞 아파트별',sorted([i for i in 매매_임대_계약월별["아파트"].drop_duplicates()]),max_selections=3)
#         # st.warning('🍣 다중선택가능')
        
#         tab1, tab2, tab3 = st.tabs([f"매매 {len(매매_계약월별)}", f"전세 {len(전세_계약월별)}", f"월세 {len(월세_계약월별)}"])
        
#         with tab1 :
#             if not 아파트:
#                 매매_데이터프레임 = 매매_계약월별
#             else:
#                 매매_데이터프레임 = 매매_계약월별[매매_계약월별["아파트"].isin(아파트)]
#             매매_데이터프레임 = 매매_데이터프레임.reindex(columns=["아파트", "금액","면적", "층", "건축", "계약", "동", "거래", "파기"])
#             st.dataframe(매매_데이터프레임.sort_values(by=['금액'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)

#             if 아파트 :                
#                 매매_차트 = api_trade[api_trade["아파트"].isin(아파트)]
#                 if not 매매_차트.empty:
#                     # st.error('🥯 시세 동향')
#                     chart = 차트(매매_차트,y='금액',t=매매_차트)
#                     st.altair_chart(chart,use_container_width=True)
#                 else:
#                     st.error('No data 😎')
                
#         with tab2:
#             if not 아파트:
#                 전세_데이터프레임 = 전세_계약월별
#             else:
#                 전세_데이터프레임 = 전세_계약월별[전세_계약월별["아파트"].isin(아파트)]

#             st.dataframe(전세_데이터프레임.sort_values(by=['보증금'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['보증금','면적','종전보증금'], cmap="Reds"),use_container_width=True,hide_index=True)

#             if 아파트 :
#                 전세_차트 = api_rent[(api_rent['아파트'].isin(아파트)) & (api_rent['월세'] == 0)]
#                 if not 전세_차트.empty:
#                     # st.error('🥯 시세 동향')
#                     chart = 차트(전세_차트,y='보증금',t=전세_차트)
#                     st.altair_chart(chart,use_container_width=True)
                
#         with tab3:
#             if not 아파트:
#                 월세_데이터프레임 = 월세_계약월별
#             else:
#                 월세_데이터프레임 = 월세_계약월별[월세_계약월별["아파트"].isin(아파트)]
                
#                 st.dataframe(월세_데이터프레임.sort_values(by=['월세'], ascending=False).reset_index(drop=True).style.background_gradient(subset=['보증금','월세','종전보증금','종전월세'], cmap="Reds"),use_container_width=True,hide_index=True)
# # except Exception as e:
# #     st.write(e)
# #     st.error('No data 😎')
