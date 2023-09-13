import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time

def 정규화(신규):
    temp = pd.DataFrame(
    [i.split(',') for i in 신규], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = (temp['금액'].astype(float) / 10000).astype('float')
    replace_word = '\(.+\)',city_replace,'아파트','마을','신도시','단지','국제금융'
    for i in replace_word:
        temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)

    return temp.sort_values(by=['아파트'], ascending=True)

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
cities = ['서울특별시 강남구', '파주시', '고양시 일산서구', '인천광역시 서구', '인천광역시 연수구','김포시','화성시', '성남시 분당구',]

for city in cities:
    if list(db.collections())[-1].id == (datetime.utcnow()+timedelta(hours=9)).date().strftime('%Y.%m.%d') :        
        매매 = db.collection(list(db.collections())[-1].id).document(city).get().to_dict()['매매']
        매매전일 = db.collection(list(db.collections())[-2].id).document(city).get().to_dict()['매매']
        index = city[:city.rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
        city_replace = index.replace('광역','').replace('특별','')
        신규 = [i for i in 매매 if i not in 매매전일]
        신규 = 정규화(신규).reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
        if len(신규) >= 1:
            e1 = st.empty()
            e = st.empty()
            e1.write(f'{city} {(datetime.utcnow()+timedelta(hours=9)).day}일 - 신규 {len(신규)}건')
            float_point = dict.fromkeys(신규.select_dtypes('float').columns, "{:.1f}")
            e.dataframe(신규.sort_values(by=['금액'], ascending=False).style.format(float_point).background_gradient(subset=['금액','층'], cmap='Reds'),use_container_width=True,hide_index=True)
            time.sleep(2.8)
        e.empty()
        e1.empty()
