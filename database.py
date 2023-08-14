import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from threading import Thread

if not firebase_admin._apps :
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
    
choice = st.radio('데이터베이스',['업데이트','삭제'],horizontal=True)
address = {'서울특별시 종로구': '11110', '서울특별시 중구': '11140', '서울특별시 용산구': '11170'}

def 실거래(url, code, user_key, rows, dong, what):
    l = []
    for date in [당월,전월]:
        url = urls[what]
        url = url + "?&LAWD_CD=" + code
        url = url + "&DEAL_YMD=" + date.strftime('%Y%m')
        url = url + "&serviceKey=" + user_key
        url = url + "&numOfRows=" + rows
        
        xml = requests.get(url)
        result = xml.text
        soup = BeautifulSoup(result, 'lxml-xml')
        items = soup.find_all("item")
        
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
                        temp = [','.join((아파트, str(보증금), str(층), str(월세), str(면적), str(건축), 동, 계약, str(종전보증금), str(종전월세), 갱신권))]
                    else:
                        거래            = item.find("거래유형").text
                        금액            = int(item.find("거래금액").text.replace(',','').strip())
                        파기            = item.find("해제사유발생일").text.strip()
                        temp = [','.join((아파트, str(금액), str(층), str(면적), str(건축), 계약 ,동, 거래, 파기))]

                l.extend(temp)
    
    # nyc_ref = db.collection(f"{당월.strftime('%Y.%m.%d')}").document(dong)
    # batch.set(nyc_ref, {what: l},merge=True)
    # batch.commit()
    
    db.collection(f"{당월.strftime('%Y.%m.%d')}").document(dong).set({what:l},merge=True)
    
    # tread_1.join()
    # tread_2.join()

if choice == '업데이트' : 
#     empty = st.empty()
#     login_code = empty.text_input('업데이트 코드', type='password')
    
    # if login_code == st.secrets.login_code :
        # empty.empty()
        # st.success('접속 완료')
    empty2 = st.empty()
    # batch = db.batch()
    db = firestore.client()
    
    urls= {'매매' : 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev','임대' : 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?'}
    
    user_key = st.secrets.user_key
    rows = '9999'
    
    당월 = (datetime.utcnow() + timedelta(hours=9)).date()
    전월 = 당월.replace(day=1) - timedelta(days=1)
    
    c = 0
    d = 0
    with st.spinner('진행중...') :
        if not db.collection(f"{당월.strftime('%Y.%m.%d')}").document('서울특별시 종로구').get().exists:
            for dong,code in address.items():        
                tread_1 = Thread(target=실거래, args=(urls['매매'], code, user_key, rows, dong,'매매'))
                tread_2 = Thread(target=실거래, args=(urls['임대'], code, user_key, rows, dong,'임대'))
                tread_1.start()
                tread_2.start()
                c += (100/len(address))
                empty2.progress(int(c)+1)
                
            empty.empty()
            st.warning('업데이트 완료')

        else:
            st.error('데이터 중복!!!')
                
    # elif login_code != '' and st.secrets.login_code :
    #     st.warning('코드 오류')
        
# def delete_collection(collection_ref):
#     docs = collection_ref.stream()
#     for doc in docs:
#         doc.reference.delete()

if choice == '삭제':
    db = firestore.client()
    empty = st.empty()
    login_code2 = empty.text_input('삭제 코드 ', type='password')

    if login_code2 == st.secrets.login_code :
        empty.success('접속 완료')
        for i in list(db.collections())[:-3]:
            c = 0
            db = firestore.client()
            db = db.collection(i.id).get()
            with st.spinner(f"{i.id} 삭제중...") :
                for doc in db:
                    doc.reference.delete()
                    c += (len(address)/100)
                    st.write(int(c))
                    empty.progress(int(c))
                empty.empty()
        st.warning('삭제 완료')
                
    elif login_code2 != '' and login_code2:
        st.warning('코드 오류')
