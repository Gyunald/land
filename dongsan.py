import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time

st.markdown('''
<style>
.stApp [data-testid="stHeader"] {visibility: hidden;}
div[class^='block-container'] { padding-top: 0rem; }
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
def 정규화(get_매매):
    temp = pd.DataFrame(
    [i.split(',') for i in get_매매], columns=["아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])
        
    temp['계약'] = pd.to_datetime(temp['계약'],format = "%Y%m%d").dt.strftime('%m.%d')
    temp['면적'] = temp['면적'].astype(float).map('{:.0f}'.format)
    temp['동'] = temp['동'].str.split().str[0]
    temp['금액'] = (temp['금액'].astype(float) / 10000)
    index = city[0][:city[0].rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
    city_replace = index.replace('광역','').replace('특별','')

    index1 = city[1][:city[1].rfind('시')]  # 마지막 '시'의 위치를 찾습니다.
    city_replace1 = index1.replace('광역','').replace('특별','')
    replace_word = '\(.+\)',city_replace,city_replace1,'신도시', '아파트',' '
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

    temp['아파트'] =  temp['아파트'].str[:10].str.ljust(10,'　')
    return temp
    
cities = [
        '서울특별시 서초구', '서울특별시 강남구',
        '고양시 덕양구', '고양시 일산서구',
        '구리시', '김포시',
        '남양주시', '부천시',
        '성남시 분당구', '성남시 수정구',
        '수원시 영통구', '수원시 팔달구',
        '용인시 기흥구', '용인시 수지구',
        '파주시', '평택시',
        '하남시', '화성시'
    ]

date = list(db.collections())
day = (datetime.utcnow()+timedelta(hours=9))

def get_data(collection_id, city):
    return db.collection(collection_id).document(city).get().to_dict()['매매']

def get_new_entries(data_today, data_yesterday):
    return [i for i in data_today if i not in data_yesterday]

def normalize_and_reindex(new_entries):
    normalized = 정규화(new_entries)
    return normalized.reindex(columns=["아파트", "금액", "면적", "층", "계약", "건축", "동", "거래", "파기"])
    
def df(df,empty):
    try:
        return empty.dataframe(
                df.sort_values(by=['금액'], ascending=False).head(head)
                .style.format(float_point)
                .background_gradient(subset=['금액','층'], cmap='Reds'),
                use_container_width=True,
                hide_index=True
            )
    except:
        pass
    
def title(empty,index,new):
    return empty.write(f"## :orange[{city[index]}] {len(new)}건 ({day.strftime('%m.%d')})")
    
e1 = st.empty()
e2 = st.empty()
e3 = st.empty()
e4 = st.empty()
head = 5

cities = list(reversed(cities))
for city in zip(cities[::2],cities[1::2]):
    if date[-1].id == day.date().strftime('%Y.%m.%d'):
        매매_today = get_data(date[-1].id, city[0])
        매매_yesterday = get_data(date[-2].id, city[0])

        매매1_today = get_data(date[-1].id, city[1])
        매매1_yesterday = get_data(date[-2].id, city[1])

        신규 = normalize_and_reindex(get_new_entries(매매_today , 매매_yesterday))
        신규1 = normalize_and_reindex(get_new_entries(매매1_today , 매매1_yesterday))
        float_point = dict.fromkeys(신규.select_dtypes('float').columns, "{:.1f}")

        title(e1,0,신규)
        title(e3,1,신규1)
        
        df(신규,e2)
        df(신규1,e4)
        
        time.sleep(3)
