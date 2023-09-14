import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

st.set_page_config(page_title="🎈아파트 실거래가 매매/전세/월세 ",layout='wide') # layout='wide'

@st.cache_data
def 매매(get_매매):
    temp = pd.DataFrame(
    [i.split(',') for i in get_매매], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format).astype(int)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = (temp['금액'].astype(float) / 10000).astype('float')
    index = 법정동명[:법정동명.rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
    city_replace = index.replace('광역','').replace('특별','')
    replace_word = '\(.+\)', city_replace, '아파트', '마을', '신도시', '단지', '시범','역'
    for i in replace_word:
        temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
    temp['층']= temp['층'].astype('int64')
    return temp

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
                건축                = str(item.find("건축년도").text)

                거래            = item.find("거래유형").text
                금액            = int(item.find("거래금액").text.replace(',','').strip())
                파기            = item.find("해제사유발생일").text.strip()
                temp = pd.DataFrame([[아파트, 금액, 면적, 층, 건축, 계약 ,동, 거래, 파기]], 
                                columns=["아파트", "금액", "면적", "층", "건축", "계약",  "동", "거래", "파기"])
                aptTrade = pd.concat([aptTrade,temp])

        index = 법정동명[:법정동명.rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
        city_replace = index.replace('광역','').replace('특별','')
        replace_word = '\(.+\)', city_replace, '아파트', '마을', '신도시', '단지', '시범','역'
        for i in replace_word:
            aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)
        aptTrade['금액'] = (aptTrade['금액'].astype(float) / 10000).astype('float')

        aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
        aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.0f}'.format).astype(int)
        aptTrade['동'] = aptTrade['동'].str.split().str[0]
        return aptTrade
        
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
address = {'서울특별시 종로구': '11110', '서울특별시 중구': '11140', '서울특별시 용산구': '11170', '서울특별시 성동구': '11200', '서울특별시 광진구': '11215', '서울특별시 동대문구': '11230',
           '서울특별시 중랑구': '11260', '서울특별시 성북구': '11290', '서울특별시 강북구': '11305', '서울특별시 도봉구': '11320', '서울특별시 노원구': '11350', '서울특별시 은평구': '11380',
           '서울특별시 서대문구': '11410', '서울특별시 마포구': '11440', '서울특별시 양천구': '11470', '서울특별시 강서구': '11500', '서울특별시 구로구': '11530', '서울특별시 금천구': '11545',
           '서울특별시 영등포구': '11560', '서울특별시 동작구': '11590', '서울특별시 관악구': '11620', '서울특별시 서초구': '11650', '서울특별시 강남구': '11680', '서울특별시 송파구': '11710',
           '서울특별시 강동구': '11740', '부산광역시 중구': '26110', '부산광역시 서구': '26140', '부산광역시 동구': '26170', '부산광역시 영도구': '26200', '부산광역시 부산진구': '26230',
           '부산광역시 동래구': '26260', '부산광역시 남구': '26290', '부산광역시 북구': '26320', '부산광역시 해운대구': '26350', '부산광역시 사하구': '26380', '부산광역시 금정구': '26410', 
           '부산광역시 강서구': '26440', '부산광역시 연제구': '26470', '부산광역시 수영구': '26500', '부산광역시 사상구': '26530', '부산광역시 기장군': '26710', '대구광역시 중구': '27110', 
           '대구광역시 동구': '27140', '대구광역시 서구': '27170', '대구광역시 남구': '27200', '대구광역시 북구': '27230', '대구광역시 수성구': '27260', '대구광역시 달서구': '27290', 
           '대구광역시 달성군': '27710', '인천광역시 중구': '28110', '인천광역시 동구': '28140', '인천광역시 미추홀구': '28177', '인천광역시 연수구': '28185', '인천광역시 남동구': '28200', 
           '인천광역시 부평구': '28237', '인천광역시 계양구': '28245', '인천광역시 서구': '28260', '인천광역시 강화군':'28710', '광주광역시 동구': '29110', '광주광역시 서구': '29140', 
           '광주광역시 남구': '29155', '광주광역시 북구': '29170', '광주광역시 광산구': '29200', '대전광역시 동구': '30110', '대전광역시 중구': '30140', '대전광역시 서구': '30170', 
           '대전광역시 유성구': '30200', '대전광역시 대덕구': '30230', '울산광역시 중구': '31110', '울산광역시 남구': '31140', '울산광역시 동구': '31170', '울산광역시 북구': '31200',
           '울산광역시 울주군': '31710', '세종특별자치시': '36110', '수원시 장안구': '41111', '수원시 권선구': '41113', '수원시 팔달구': '41115', '수원시 영통구': '41117', 
           '성남시 수정구': '41131', '성남시 중원구': '41133', '성남시 분당구': '41135', '의정부시': '41150', '안양시 만안구': '41171', '안양시 동안구': '41173', '부천시': '41190', 
           '광명시': '41210', '평택시': '41220', '동두천시': '41250', '안산시 상록구': '41271', '안산시 단원구': '41273', '고양시 덕양구': '41281', '고양시 일산동구': '41285', 
           '고양시 일산서구': '41287', '과천시': '41290', '구리시': '41310', '남양주시': '41360', '오산시': '41370', '시흥시': '41390', '군포시': '41410', '의왕시': '41430', 
           '하남시': '41450', '용인시 처인구': '41461', '용인시 기흥구': '41463', '용인시 수지구': '41465', '파주시': '41480', '안성시': '41550', '김포시': '41570',
           '화성시': '41590', '광주시': '41610', '양주시': '41630','청주시 상당구': '43111', '청주시 서원구': '43112', '청주시 흥덕구': '43113', '청주시 청원구': '43114', 
           '천안시 동남구': '44131','천안시 서북구': '44133', '아산시': '44200', '전주시 완산구': '45111', '전주시 덕진구': '45113', '익산시': '45140','목포시': '46110', 
           '여수시': '46130', '순천시': '46150','광양시': '46230', '포항시 남구': '47111', '포항시 북구': '47113', '구미시': '47190', '경산시': '47290','창원시 의창구': '48121',
           '창원시 성산구': '48123', '창원시 마산합포구': '48125', '창원시 마산회원구': '48127', '창원시 진해구': '48129','김해시': '48250', '거제시': '48310', '제주시': '50110', '서귀포시': '50130'}

user_key = st.secrets.user_key
rows = '9999'

# st.write('실거래 조회 🎈')
c1,c2 = st.columns([1,1])
with c1 :
    empty = st.empty()
    standard = empty.date_input('🧁 날짜', datetime.utcnow()+timedelta(hours=9),key='standard_date_1',max_value=datetime.utcnow()+timedelta(hours=9),label_visibility='collapsed',format='YYYY.MM.DD')
    empty.empty()

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
    시군구 = st.selectbox('🍔 시군구 검색', [i for i in address],index=104,label_visibility='collapsed') # 22 강남 104 파주

    city = address[시군구]
    address = {y:x for x,y in address.items()}
    법정동명 = address[city]

try:
    if standard_str[5:8] == (datetime.utcnow()+timedelta(hours=9)).date().strftime('%m.%d')[:3] :

        get_매매 = db.collection(list(db.collections())[-1].id).document(시군구).get().to_dict()['매매']

        temp = 매매(get_매매)
        매매_당월 = temp[temp['계약'].str.contains(standard_str[5:8])].drop_duplicates()

        if standard_str[-2:] == (datetime.utcnow()+timedelta(hours=9)).strftime('%d'):
            get_매매전일 = db.collection(list(db.collections())[-2].id).document(시군구).get().to_dict()['매매']
            temp3 = 매매(get_매매전일)
            신규 = pd.merge(temp,temp3, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
            신규 = 신규.reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
            
            if len(신규) >= 1:
                e = st.empty()
                e1 = st.empty()
                e2 = st.empty()

                e.write(f"#### :orange[{법정동명}] 실거래 {len(신규)}건 ({(datetime.utcnow() + timedelta(hours=9)).strftime('%m.%d')})")
                float_point = dict.fromkeys(신규.select_dtypes('float').columns, "{:.1f}")

                e1.dataframe(신규.sort_values(by=['금액'], ascending=False).style.format(float_point).background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)

            전체 = st.toggle(f':orange[{standard.month}월 실거래 전체]')

            if 전체 :
                매매_당월 = 매매_당월.reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
                
                e.write(f"#### :orange[{법정동명}] 실거래 {len(매매_당월)}건")
                아파트 = e1.multiselect('🍞 아파트별1',sorted([i for i in 매매_당월["아파트"].drop_duplicates()]),max_selections=3,placeholder= '아파트별',label_visibility='collapsed')
                
                if not 아파트:
                    매매_데이터프레임 = 매매_당월
                else:
                    매매_데이터프레임 = 매매_당월[매매_당월["아파트"].isin(아파트)]

                float_point = dict.fromkeys(매매_당월.select_dtypes('float').columns, "{:.1f}")
                e2.dataframe(매매_데이터프레임.sort_values(by=['금액'], ascending=False).style.format(float_point).background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)

except Exception as e:
    st.write(e)
    st.error('데이터 업데이트 중 😎')
