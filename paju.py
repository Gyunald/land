import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time

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
st.set_page_config(page_title="🎈아파트 실거래가 매매/전세/월세 ") # layout='wide'

@st.cache_data
def 정규화(get_매매):
    temp = pd.DataFrame(
    [i.split(',') for i in get_매매], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = (temp['금액'].astype(float) / 10000)
    index = city[:city.rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
    city_replace = index.replace('광역','').replace('특별','')
    
    replace_word = '\(.+\)',city_replace,'신도시', '아파트','역','시범','마을',
    for i in replace_word:
        temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
        
    if city == '파주시':
        temp['아파트'] = temp['아파트'].apply(lambda j: j[j.index('단지')+2 :] if '단지' in j else j)
        temp['아파트'] = temp['아파트'].str.replace('세상','',regex=True)
        
    elif city == '평택시':
        temp['아파트'] = temp['아파트'].str.replace('국제','',regex=True)

    elif city == '화성시':
        temp['아파트'] = temp['아파트'].str.replace('반도유보라','',regex=True).replace('산척동.동탄호수공원','',regex=True)

    elif city == '인천광역시 서구':
        temp['아파트'] = temp['아파트'].str.replace('에듀앤파크','',regex=True).str.replace('국제금융단지','',regex=True).str.replace('지구','',regex=True).str.replace('블루','',regex=True)

    elif city == '인천광역시 연수구':
        temp['아파트'] = temp['아파트'].str.replace('더샵','',regex=True).str.replace('송도1차','1차',regex=True).str.replace('송도2차','2차',regex=True).str.replace('송도3차','3차',regex=True).str.replace('송도4차','4차',regex=True)

    elif city == '고양시 일산동구':
        temp['아파트'] = temp['아파트'].str.replace('일산','',regex=True)

    elif city == '고양시 일산서구':
        temp['아파트'] = temp['아파트'].str.replace('일산','',regex=True)             
    
    temp['아파트'] = temp['아파트'].apply(lambda j: j[:j.index('단지')] if '단지' in j else j)
    return temp

db = firestore.client()
cities =  ['파주시', '김포시', '고양시 일산서구', '고양시 일산동구', '인천광역시 연수구', '인천광역시 서구', '성남시 분당구', '수원시 영통구', '용인시 수지구', '화성시', '평택시']

date = list(db.collections())
day = (datetime.utcnow()+timedelta(hours=9))
for city in cities[::-1]:
    if date[-1].id == day.date().strftime('%Y.%m.%d') :        
        매매 = db.collection(date[-1].id).document(city).get().to_dict()['매매']
        매매전일 = db.collection(date[-2].id).document(city).get().to_dict()['매매']
        index = city[:city.rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
        city_replace = index.replace('광역','').replace('특별','')
        신규 = [i for i in 매매 if i not in 매매전일]
        신규 = 정규화(신규).reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
        e1 = st.empty()
        e = st.empty()
        if len(신규) >= 1:          
            e1.write(f"#### :orange[{city}] 실거래 {len(신규)}건 ({day.strftime('%m.%d')})")                    
            float_point = dict.fromkeys(신규.select_dtypes('float').columns, "{:.1f}")
            e.dataframe(신규.sort_values(by=['금액'], ascending=False).style.format(float_point).background_gradient(subset=['금액','층'], cmap='Reds'),use_container_width=True,hide_index=True)
            time.sleep(3.3)
        e.empty()
        e1.empty()
