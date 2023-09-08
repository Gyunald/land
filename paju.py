import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import requests
import altair as alt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

st.set_page_config(page_title="파주시 실거래가") # layout='wide'

@st.cache_data
def 매매(get_매매):
    temp = pd.DataFrame(
    [i.split(',') for i in get_매매], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = (temp['금액'].astype(int) / 10000).astype(str)
    replace_word = '아파트','마을','신도시','단지','\(.+\)','운정','파주','더퍼스트'
    for i in replace_word:
        temp['아파트'] = temp['아파트'].str.replace(i,'',regex=True)
    temp['층']= temp['층']

    return temp.sort_values(by=['아파트'], ascending=True)

@st.cache_data
def 매매_전일(get_매매전일):    
    temp3 = pd.DataFrame(
    [i.split(',') for i in get_매매전일], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"]
)
    temp3['계약'] = pd.to_datetime(temp3['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp3['면적'] = temp3['면적'].astype(float).map('{:.0f}'.format)
    temp3['동'] = temp3['동'].str.split().str[0]
    temp3['금액'] = (temp3['금액'].astype(int) / 10000).astype(str)
    replace_word = '아파트','마을','신도시','단지','\(.+\)','운정','파주','더퍼스트'
    for i in replace_word:
        temp3['아파트'] = temp3['아파트'].str.replace(i,'',regex=True)
    temp3['층']= temp3['층']
    return temp3.sort_values(by=['아파트'], ascending=True)

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
address = {'파주시' : '41480'}

user_key = st.secrets.user_key
rows = '9999'

city = address['파주시']
address = {y:x for x,y in address.items()}
법정동명 = address[city]
try:
    if list(db.collections())[-1].id == (datetime.utcnow()+timedelta(hours=9)).date().strftime('%Y.%m.%d') :        
        get_매매 = db.collection(list(db.collections())[-1].id).document('파주시').get().to_dict()['매매']
        temp = 매매(get_매매)            

        get_매매전일 = db.collection(list(db.collections())[-2].id).document('파주시').get().to_dict()['매매']
        temp3 = 매매_전일(get_매매전일)        
        신규 = pd.merge(temp,temp3, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']).reset_index(drop=True)
        신규 = 신규.reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
        if len(신규) >= 1:
            f'{법정동명.split()[-1]} {(datetime.utcnow()+timedelta(hours=9)).day}일 - 신규 {len(신규)}건'
            st.dataframe(신규.sort_values(by=['금액'], ascending=False).style.background_gradient(subset=['금액','층'], cmap='Reds'),use_container_width=True,hide_index=True)

except Exception as e:
    # st.write(e)
    st.error('데이터 업데이트 중 😎')
