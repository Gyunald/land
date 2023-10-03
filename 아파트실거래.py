import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

st.set_page_config(page_title="🎈아파트 실거래가") # layout='wide'

st.markdown('''
<style>
.stApp [data-testid="stHeader"] {visibility: hidden;}
div[class^='block-container'] { padding-top: 1rem; }
</style>
''', unsafe_allow_html=True)

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

@st.cache_data
def 매매(get_매매):
    temp = pd.DataFrame(
    [i.split(',') for i in get_매매], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = (temp['금액'].astype(float) / 10000)
    index = city[:city.rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
    city_replace = index.replace('광역','').replace('특별','')

    replace_word = '\(.+\)',city_replace,'신도시', '아파트',' ','마을'
    for i in replace_word:
        temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)

    for i in temp['아파트']:
        try:
            if len(i)/2 > i.index('단지'):
                i = i[: i.index('단지')+2]
                temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
        except:
            pass
    for i in temp['아파트']:
        try:                
            if len(i)/2 < i.index('단지'):
                i = i[i.index('단지'):]
                temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
        except:
            pass
    # temp['아파트'] =  temp['아파트'].str[:10]
    return temp
        
db = firestore.client()
address = ['서울특별시 종로구', '서울특별시 중구', '서울특별시 용산구', '서울특별시 성동구', '서울특별시 광진구', '서울특별시 동대문구', '서울특별시 중랑구', '서울특별시 성북구', '서울특별시 강북구', '서울특별시 도봉구', '서울특별시 노원구', '서울특별시 은평구', '서울특별시 서대문구', '서울특별시 마포구', '서울특별시 양천구', '서울특별시 강서구', '서울특별시 구로구', '서울특별시 금천구', '서울특별시 영등포구', '서울특별시 동작구', '서울특별시 관악구', '서울특별시 서초구', '서울특별시 강남구', '서울특별시 송파구', '서울특별시 강동구', '부산광역시 중구', '부산광역시 서구', '부산광역시 동구', '부산광역시 영도구', '부산광역시 부산진구', '부산광역시 동래구', '부산광역시 남구', '부산광역시 북구', '부산광역시 해운대구', '부산광역시 사하구', '부산광역시 금정구', '부산광역시 강서구', '부산광역시 연제구', '부산광역시 수영구', '부산광역시 사상구', '부산광역시 기장군', '대구광역시 중구', '대구광역시 동구', '대구광역시 서구', '대구광역시 남구', '대구광역시 북구', '대구광역시 수성구', '대구광역시 달서구', '대구광역시 달성군', '인천광역시 중구', '인천광역시 동구', '인천광역시 미추홀구', '인천광역시 연수구', '인천광역시 남동구', '인천광역시 부평구', '인천광역시 계양구', '인천광역시 서구', '인천광역시 강화군', '광주광역시 동구', '광주광역시 서구', '광주광역시 남구', '광주광역시 북구', '광주광역시 광산구', '대전광역시 동구', '대전광역시 중구', '대전광역시 서구', '대전광역시 유성구', '대전광역시 대덕구', '울산광역시 중구', '울산광역시 남구', '울산광역시 동구', '울산광역시 북구', '울산광역시 울주군', '세종특별자치시', '수원시 장안구', '수원시 권선구', '수원시 팔달구', '수원시 영통구', '성남시 수정구', '성남시 중원구', '성남시 분당구', '의정부시', '안양시 만안구', '안양시 동안구', '부천시', '광명시', '평택시', '안산시 상록구', '안산시 단원구', '고양시 덕양구', '고양시 일산동구', '고양시 일산서구', '과천시', '구리시', '남양주시', '오산시', '시흥시', '군포시', '의왕시', '하남시', '용인시 처인구', '용인시 기흥구', '용인시 수지구', '파주시', '안성시', '김포시', '화성시', '광주시', '양주시', '청주시 상당구', '청주시 서원구', '청주시 흥덕구', '청주시 청원구', '천안시 동남구', '천안시 서북구', '아산시','익산시', '여수시', '순천시', '포항시 남구', '포항시 북구', '구미시', '창원시 의창구', '창원시 성산구', '창원시 마산합포구', '창원시 마산회원구', '창원시 진해구', '거제시', '제주시', '서귀포시']

city = st.selectbox('🍔 시군구 검색', [i for i in address],index=22,label_visibility='collapsed') # 22 강남 103 파주

date = list(db.collections())
day = (datetime.utcnow() + timedelta(hours=9))
try:    
    get_매매 = db.collection(date[-1].id).document(city).get().to_dict()['매매']
    temp = 매매(get_매매)
    매매_당월 = temp[temp['계약'].str.contains(date[-1].id[5:8])].drop_duplicates()
    
    e = st.empty()
    e1 = st.empty()
    e2 = st.empty()
    
    status = True
    if date[-1].id == day.date().strftime('%Y.%m.%d'):
        get_매매전일 = db.collection(date[-2].id).document(city).get().to_dict()['매매']
        temp3 = 매매(get_매매전일)
        신규 = pd.merge(temp,temp3, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
        신규 = 신규.reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
        
        if len(신규) >= 1:
            status = False
            e.write(f"#### :orange[{city}] 실거래 {len(신규)}건 ({day.strftime('%m.%d')})")
            float_point = dict.fromkeys(신규.select_dtypes('float').columns, "{:.1f}")

            e1.dataframe(신규.sort_values(by=['금액'], ascending=False).style.format(float_point).background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)

    전체 = st.toggle(f':orange[{day.month}월 실거래 전체]',value=status, disabled=status)

    if 전체 :
        매매_당월 = 매매_당월.reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
            
        e.write(f"#### :orange[{city}] 실거래 {len(매매_당월)}건")
        아파트 = e1.multiselect('아파트별',sorted([i for i in 매매_당월["아파트"].drop_duplicates()]),max_selections=3,placeholder= '아파트별',label_visibility='collapsed')
            
        if not 아파트:
            매매_당월 = 매매_당월
        else:
            매매_당월 = 매매_당월[매매_당월["아파트"].isin(아파트)]

        float_point = dict.fromkeys(매매_당월.select_dtypes('float').columns, "{:.1f}")
        
        # 매매_당월["아파트"] = "https://map.naver.com/p/search/"+매매_당월["아파트"]
        
        매매_당월 = 매매_당월.sort_values(by=['금액'], ascending=False)
        e2.dataframe(매매_당월.sort_values(by=['금액'], ascending=False).style.format(float_point).background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True)
        
        # e2.dataframe(매매_당월.style.format(float_point).background_gradient(subset=['금액','층'], cmap="Reds"),use_container_width=True,hide_index=True,
        #                  column_config={
        #                      "아파트": st.column_config.LinkColumn()
        #                     }
        #                  )
except Exception as e:
    st.error('데이터 업데이트 중 😎')
    st.write(e)
