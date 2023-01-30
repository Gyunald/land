import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime,timedelta
import requests
from streamlit_lottie import st_lottie,st_lottie_spinner
import altair as alt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def 실거래(url, city, date, user_key, rows, dong):
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
                시군구              = dong
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
                    temp = pd.DataFrame([[시군구, 아파트, 보증금, 층, 월세, 면적, 건축, 동, 계약, 종전보증금, 종전월세, 갱신권,]], 
                                columns=["시군구","아파트", "보증금", "층", "월세", "면적", "건축", "동", "계약", "종전보증금", "종전월세", "갱신권"])
                else:
                    거래            = item.find("거래유형").text
                    금액            = int(item.find("거래금액").text.replace(',','').strip())
                    파기            = item.find("해제사유발생일").text.strip()
                    temp = pd.DataFrame([[시군구, 아파트, 금액, 층,면적, 건축, 계약 ,동, 거래, 파기]], 
                                    columns=["시군구", "아파트", "금액", "층", "면적", "건축", "계약", "동", "거래", "파기"])            
                aptTrade = pd.concat([aptTrade,temp])

        replace_word = '아파트','마을','신도시'
        for i in replace_word:
            aptTrade['아파트'] = aptTrade['아파트'].str.replace(i,'',regex=True)

        aptTrade['계약'] = pd.to_datetime(aptTrade['계약'],format = "%Y%m%d").dt.strftime('%y.%m.%d')
        aptTrade['면적'] = aptTrade['면적'].astype(float).map('{:.0f}'.format).astype(int)
        aptTrade['동'] = aptTrade['동'].str.split().str[0]
    return aptTrade

cred = credentials.Certificate('kdongsan-8cc40-firebase-adminsdk-vr6ws-d96491c757.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

urls= {'매매' : 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev','임대' : 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?'}

file_1 = pd.read_csv('/Users/kyu-deokkim/Downloads/address.csv',encoding='cp949')
user_key = 'pRcMh3ZvTSWhUPu4VIMig%2BbD1mnLgAyaxyhB07a86H8XbgJ7ki8JYqk3a6Q6lM%2FN8zhvYZHQsLw0pmbjPBBE%2FA%3D%3D'
rows = '9999'

당월 = datetime.now().date()
전월 = 당월 - timedelta(days=30)

c = 0
for i,j in urls.items():
    당월합= pd.DataFrame()
    전월합= pd.DataFrame()
    start = datetime.now()
    for city,dong in zip(file_1['법정동코드'].astype(str).str[:5],file_1['법정동명']):
        합_당월매매 = {}
        print(f"{c:.1f}% {dong} complete...")
        당월매매 = 실거래(j, city, 당월.strftime('%Y%m'), user_key, rows, dong)
        전월매매 = 실거래(j, city, 전월.strftime('%Y%m'), user_key, rows, dong)
        당월합 = pd.concat([당월합,당월매매])
        전월합 = pd.concat([전월합,전월매매])
        당월전월합 = pd.concat([당월합,전월합]).reset_index(drop=True)
        합_당월매매[dong] = 당월전월합[당월전월합['시군구'].str.contains(dong)].set_index('시군구').to_csv().strip().split('\n')
        db.collection(f"{당월.strftime('%d')}_{i}_{당월.strftime('%Y.%m')}").document(dong).set(합_당월매매)        
        c += (50/len(file_1['법정동코드']))
end = datetime.now()
print(f"100% complete! >>> {end-start} seconds")

del_list = ['trade', 'rent']
a = datetime.utcnow()- timedelta(days=1)
b = a.date().strftime('%y.%m')

for i in del_list:
    db = db.collection(f"{a.day}_{i}_{b}").stream()
    for j in db:
        j.reference.delete()
