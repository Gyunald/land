import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from threading import Thread

# urls= {'매매' : 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev',
#        '임대' : 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?'}

# user_key = st.secrets.user_key
# rows = '9999'

# this_month = (datetime.utcnow() + timedelta(hours=9)).date()
# previous_month = this_month.replace(day=1) - timedelta(days=1)
    
# choice = st.radio('데이터베이스',['업데이트','삭제'],horizontal=True)

# address = {'서울특별시 종로구': '11110', '서울특별시 중구': '11140', '서울특별시 용산구': '11170', '서울특별시 성동구': '11200', '서울특별시 광진구': '11215', '서울특별시 동대문구': '11230',
#            '서울특별시 중랑구': '11260', '서울특별시 성북구': '11290', '서울특별시 강북구': '11305', '서울특별시 도봉구': '11320', '서울특별시 노원구': '11350', '서울특별시 은평구': '11380',
#            '서울특별시 서대문구': '11410', '서울특별시 마포구': '11440', '서울특별시 양천구': '11470', '서울특별시 강서구': '11500', '서울특별시 구로구': '11530', '서울특별시 금천구': '11545',
#            '서울특별시 영등포구': '11560', '서울특별시 동작구': '11590', '서울특별시 관악구': '11620', '서울특별시 서초구': '11650', '서울특별시 강남구': '11680', '서울특별시 송파구': '11710',
#            '서울특별시 강동구': '11740', '부산광역시 중구': '26110', '부산광역시 서구': '26140', '부산광역시 동구': '26170', '부산광역시 영도구': '26200', '부산광역시 부산진구': '26230',
#            '부산광역시 동래구': '26260', '부산광역시 남구': '26290', '부산광역시 북구': '26320', '부산광역시 해운대구': '26350', '부산광역시 사하구': '26380', '부산광역시 금정구': '26410', 
#            '부산광역시 강서구': '26440', '부산광역시 연제구': '26470', '부산광역시 수영구': '26500', '부산광역시 사상구': '26530', '부산광역시 기장군': '26710', '대구광역시 중구': '27110', 
#            '대구광역시 동구': '27140', '대구광역시 서구': '27170', '대구광역시 남구': '27200', '대구광역시 북구': '27230', '대구광역시 수성구': '27260', '대구광역시 달서구': '27290', 
#            '대구광역시 달성군': '27710', '인천광역시 중구': '28110', '인천광역시 동구': '28140', '인천광역시 미추홀구': '28177', '인천광역시 연수구': '28185', '인천광역시 남동구': '28200', 
#            '인천광역시 부평구': '28237', '인천광역시 계양구': '28245', '인천광역시 서구': '28260', '인천광역시 강화군':'28710', '광주광역시 동구': '29110', '광주광역시 서구': '29140', 
#            '광주광역시 남구': '29155', '광주광역시 북구': '29170', '광주광역시 광산구': '29200', '대전광역시 동구': '30110', '대전광역시 중구': '30140', '대전광역시 서구': '30170', 
#            '대전광역시 유성구': '30200', '대전광역시 대덕구': '30230', '울산광역시 중구': '31110', '울산광역시 남구': '31140', '울산광역시 동구': '31170', '울산광역시 북구': '31200',
#            '울산광역시 울주군': '31710', '세종특별자치시': '36110', '수원시 장안구': '41111', '수원시 권선구': '41113', '수원시 팔달구': '41115', '수원시 영통구': '41117', 
#            '성남시 수정구': '41131', '성남시 중원구': '41133', '성남시 분당구': '41135', '의정부시': '41150', '안양시 만안구': '41171', '안양시 동안구': '41173', '부천시': '41190', 
#            '광명시': '41210', '평택시': '41220', '동두천시': '41250', '안산시 상록구': '41271', '안산시 단원구': '41273', '고양시 덕양구': '41281', '고양시 일산동구': '41285', 
#            '고양시 일산서구': '41287', '과천시': '41290', '구리시': '41310', '남양주시': '41360', '오산시': '41370', '시흥시': '41390', '군포시': '41410', '의왕시': '41430', 
#            '하남시': '41450', '용인시 처인구': '41461', '용인시 기흥구': '41463', '용인시 수지구': '41465', '파주시': '41480', '안성시': '41550', '김포시': '41570',
#            '화성시': '41590', '광주시': '41610', '양주시': '41630','청주시 상당구': '43111', '청주시 서원구': '43112', '청주시 흥덕구': '43113', '청주시 청원구': '43114', 
#            '천안시 동남구': '44131','천안시 서북구': '44133', '아산시': '44200', '전주시 완산구': '45111', '전주시 덕진구': '45113', '익산시': '45140','목포시': '46110', 
#            '여수시': '46130', '순천시': '46150','광양시': '46230', '포항시 남구': '47111', '포항시 북구': '47113', '구미시': '47190', '경산시': '47290','창원시 의창구': '48121',
#            '창원시 성산구': '48123', '창원시 마산합포구': '48125', '창원시 마산회원구': '48127', '창원시 진해구': '48129','김해시': '48250', '거제시': '48310', '제주시': '50110', '서귀포시': '50130'}

# if not firebase_admin._apps :
#     cred = credentials.Certificate({
#     "type": st.secrets.type,
#     "project_id": st.secrets.project_id,
#     "private_key_id": st.secrets.private_key_id,
#     "private_key": st.secrets.private_key,
#     "client_email": st.secrets.client_email,
#     "client_id": st.secrets.client_id,
#     "auth_uri": st.secrets.auth_uri,
#     "token_uri": st.secrets.token_uri,
#     "auth_provider_x509_cert_url": st.secrets.auth_provider_x509_cert_url,
#     "client_x509_cert_url": st.secrets.client_x509_cert_url
#     })
#     app = firebase_admin.initialize_app(cred)
# db = firestore.client()

# def process_data(url, code, user_key, rows, dong, what):
#     data_list = []    
#     for date in [previous_month, this_month]:
#         query_url = url + f"?&LAWD_CD={code}&DEAL_YMD={date.strftime('%Y%m')}&serviceKey={user_key}&numOfRows={rows}"
#         xml = requests.get(query_url)
#         result = xml.text
#         soup = BeautifulSoup(result, 'lxml-xml')
#         items = soup.find_all("item")
    
#         for item in items:
#             if item.find('건축년도') == None :
#                 continue
#             else:               
#                 계약               =   item.find("년").text + item.find("월").text.zfill(2) + item.find("일").text.zfill(2)
#                 동                = item.find("법정동").text
#                 면적               = float(item.find("전용면적").text)
#                 아파트              = item.find("아파트").text.replace(',','.')
#                 층                 = int(item.find("층").text)
#                 건축                = int(item.find("건축년도").text)
                
#                 if 'getRTMSDataSvcAptRent' in url:
#                     보증금           = int(item.find("보증금액").text.replace(',',''))
#                     월세             = int(item.find("월세금액").text.replace(',','').replace(' ','0'))
#                     갱신권           = item.find("갱신요구권사용").text.strip()
#                     종전보증금        = int(item.find("종전계약보증금").text.replace(',','').replace(' ','0'))
#                     종전월세         = int(item.find("종전계약월세").text.replace(',','').replace(' ','0'))
#                     data_list.append(','.join((아파트, str(보증금), str(층), str(월세), str(면적), str(건축), 동, 계약, str(종전보증금), str(종전월세), 갱신권)))
#                 else:
#                     거래            = item.find("거래유형").text
#                     금액            = int(item.find("거래금액").text.replace(',','').strip())
#                     파기            = item.find("해제사유발생일").text.strip()
#                     data_list.append(','.join((아파트, str(금액), str(층), str(면적), str(건축), 계약 ,동, 거래, 파기)))

#     db.collection(f"{this_month.strftime('%Y.%m.%d')}").document(dong).set({what: data_list}, merge=True)
    
# if choice == '업데이트' : 
# #     empty = st.empty()
# #     login_code = empty.text_input('업데이트 코드', type='password')
    
#     # if login_code == st.secrets.login_code :
#         # empty.empty()
#         # st.success('접속 완료')
#     empty2 = st.empty()        
#     c = 0
    
#     with st.spinner('진행중...'):
#         # if not db.collection(f"{this_month.strftime('%Y.%m.%d')}").document('서울특별시 종로구').get().exists:
#             # threads = []
#         if (datetime.utcnow() + timedelta(hours=9)).date().strftime('%Y.%m.%d') != list(db.collections())[-1].id:
#             for dong, code in address.items():
#                 t = Thread(target=process_data, args=(urls['매매'], code, user_key, rows, dong, '매매'))
#                 # threads.append(t)
#                 t.start()
#                 t = Thread(target=process_data, args=(urls['임대'], code, user_key, rows, dong, '임대'))
#                 # threads.append(t)
#                 t.start()
#                 c += (100/len(address))
#                 empty2.progress(int(c)+1)
                
#             empty2.empty()
#             st.warning('업데이트 완료')

#             # for thread in threads:
#             #     thread.join()

#         else:
#             st.error('데이터 중복!!!')
                
# if choice == '삭제':
#     empty = st.empty()
#     login_code2 = empty.text_input('삭제 코드 ', type='password')
#     if login_code2 == st.secrets.login_code :
#         empty.empty()
#         if (datetime.utcnow() + timedelta(hours=9)).date().strftime('%Y.%m.%d') == list(db.collections())[-1].id :
#             status = False
#             v = ':rainbow[오늘 데이터만 삭제]'
#         else:
#             status = True
#             v = '오늘 업데이트 필요'

#         toggle = st.toggle(v,value= not status, disabled=status)
        
#         if toggle:
#             list_range = list(db.collections())[-1:]
#             st.write(f"# :rainbow[{list(db.collections())[-1].id}]")

#         else:
#             list_range = list(db.collections())[:-3]
#             st.write(f"# {list(db.collections())[0].id} ~")

#         db = firestore.client()
#         empty2 = st.empty()
#         b = empty2.button('삭제',use_container_width=True)
#         if b :
#             empty2.empty()
#             for i in list_range:
#                 c = 0
#                 db = firestore.client()
#                 db = db.collection(i.id).get()
#                 with st.spinner(f"{i.id} 삭제중...") :
#                     for doc in db:
#                         doc.reference.delete()
#                         c += (100 / len(address))
#                         empty2.progress(int(c))
#                     empty2.empty()
#             st.warning('삭제 완료')
#     elif login_code2 != '' and login_code2:
#         st.warning('코드 오류')


# 수정

import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading


urls= {'매매' : 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'}
    #    '임대' : 'http://apis.data.go.kr/1613000/RTMSDataSvcAptRent'}

user_key = '3eOnAkVjvK966MbeTAVERd%2Fbmv0OmPtDl0u%2BprDb96wKHePnJWANhz%2B4xUGls%2FKBO0JbDu%2BI8rg%2FzD4WBwLtGg%3D%3D'
rows = '9999'

this_month = (datetime.now() + timedelta(hours=9)).date()
previous_month = this_month.replace(day=1) - timedelta(days=1)

# address = {'파주': '41480'}
    
address = {'서울 종로구': '11110', '서울 중구': '11140', '서울 용산구': '11170', '서울 성동구': '11200', '서울 광진구': '11215', '서울 동대문구': '11230',
           '서울 중랑구': '11260', '서울 성북구': '11290', '서울 강북구': '11305', '서울 도봉구': '11320', '서울 노원구': '11350', '서울 은평구': '11380',
           '서울 서대문구': '11410', '서울 마포구': '11440', '서울 양천구': '11470', '서울 강서구': '11500', '서울 구로구': '11530', '서울 금천구': '11545',
           '서울 영등포구': '11560', '서울 동작구': '11590', '서울 관악구': '11620', '서울 서초구': '11650', '서울 강남구': '11680', '서울 송파구': '11710',
           '서울 강동구': '11740', '부산 중구': '26110', '부산 서구': '26140', '부산 동구': '26170', '부산 영도구': '26200', '부산 부산진구': '26230',
           '부산 동래구': '26260', '부산 남구': '26290', '부산 북구': '26320', '부산 해운대구': '26350', '부산 사하구': '26380', '부산 금정구': '26410', 
           '부산 강서구': '26440', '부산 연제구': '26470', '부산 수영구': '26500', '부산 사상구': '26530', '부산 기장군': '26710', '대구 중구': '27110', 
           '대구 동구': '27140', '대구 서구': '27170', '대구 남구': '27200', '대구 북구': '27230', '대구 수성구': '27260', '대구 달서구': '27290', 
           '대구 달성군': '27710', '인천 중구': '28110', '인천 동구': '28140', '인천 미추홀구': '28177', '인천 연수구': '28185', '인천 남동구': '28200', 
           '인천 부평구': '28237', '인천 계양구': '28245', '인천 서구': '28260', '인천 강화군':'28710', '광주 동구': '29110', '광주 서구': '29140', 
           '광주 남구': '29155', '광주 북구': '29170', '광주 광산구': '29200', '대전 동구': '30110', '대전 중구': '30140', '대전 서구': '30170', 
           '대전 유성구': '30200', '대전 대덕구': '30230', '울산 중구': '31110', '울산 남구': '31140', '울산 동구': '31170', '울산 북구': '31200',
           '울산 울주군': '31710', '세종': '36110', '수원 장안구': '41111', '수원 권선구': '41113', '수원 팔달구': '41115', '수원 영통구': '41117', 
           '성남 수정구': '41131', '성남 중원구': '41133', '성남 분당구': '41135', '의정부': '41150', '안양 만안구': '41171', '안양 동안구': '41173', '부천': '41190', 
           '광명': '41210', '평택': '41220', '동두천': '41250', '안산 상록구': '41271', '안산 단원구': '41273', '고양 덕양구': '41281', '고양 일산동구': '41285', 
           '고양 일산서구': '41287', '과천': '41290', '구리': '41310', '남양주': '41360', '오산': '41370', '시흥': '41390', '군포': '41410', '의왕': '41430', 
           '하남': '41450', '용인 처인구': '41461', '용인 기흥구': '41463', '용인 수지구': '41465', '파주': '41480', '안성': '41550', '김포': '41570',
           '화성': '41590', '광주': '41610', '양주': '41630','청주 상당구': '43111', '청주 서원구': '43112', '청주 흥덕구': '43113', '청주 청원구': '43114', 
           '천안 동남구': '44131','천안 서북구': '44133', '아산': '44200', '전주 완산구': '45111', '전주 덕진구': '45113', '익산': '45140','목포': '46110', 
           '여수': '46130', '순천': '46150','광양': '46230', '포항 남구': '47111', '포항 북구': '47113', '구미': '47190', '경산': '47290','창원 의창구': '48121',
           '창원 성산구': '48123', '창원 마산합포구': '48125', '창원 마산회원구': '48127', '창원 진해구': '48129','김해': '48250', '거제': '48310', '제주': '50110', '서귀포': '50130'}


if not firebase_admin._apps :
    cred = credentials.Certificate({
        'type' : "service_account",

        'project_id' : "kdongsan-8cc40",

        'private_key_id' : "d96491c757022e0548945ec1000ac1c6fa791379",

        'private_key' : "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2xZh1KFh6Zz41\n4U53yxrkNh/OxkRLc9/SFdX1DOgCg1XDtbRd+K5I+2AEemmicDEnyrJxem6SIRme\nMK8C02gpgbUJm7oAzn5AQQlHbChfvddYiVv4ohFsTmo0WdiimiuyMO2RmqvYKez7\nGXUdxz5agjUXQcn9aWHqkWqDlskN7nQnRltN4c3W58e3pAn6ZRouyxEgNHb8pRJV\nAhbjmDNa0oqxUn4sQByak6mdDXSF2nRzGMRglC2WrS208JsZCT7X+57DGUdxtBD9\nUxi9Z2VDWtO/jnnhihE5oDzfNSirR6E3oS5YQDoMwtPFMwUiyHGFcE4o4LwuSVUk\ndESYYSAfAgMBAAECggEAUO+ohz0SDUY55Mc8pczBwEx9gmYHKTiLZW94+1a3SSGa\nsZt931035Ka4itMggyfWhK38nkbevwQ8YXJilchDaJoBLtuQnznR66dBMikhqeAa\nBCFzomM2fvUsj7k3ty25auPC2EcbkRJj2IAZ/lFUeeUOGJnwFjF8BFFXzyTPLMTr\nRKYyx19S98vNhhlUOgZgSRV7UY8Ni7ZP1F0XVLHjan4RpCIU0/C07YLmKKfx0t1J\nuCI0ZrXK3JPeDp3y8t9fvfoAkzdbCgpwGVauUJkCSnduJMZ5ZMHGCMY3FqPmZp3E\nLSUTw/BqlmwFqjQ7xU5ltKsniQlz7KEwCXOZJr0+fQKBgQDjlfctRW4RH7FzrBXG\nXRQLX3V3K/Q8HtDc5Yy5cCs4vGT20IZON/bnza3iwkLwDkl+9nUaZiQyS6kpb3w9\nYY/D9HWUYCPk8sgC6wOwl3M/389vLG3NLVqG36Krd8pP7yD+Q9TEz4Tvmy+m/wp0\njCOmsYbgxzWJDwwRB+pVtYeHtQKBgQDNl0yQpJMsIPul21dXZsMQDvVOqoaV7+Qr\niD8NWU39WrxHIPpCjsFipnc+Pz1mBdyqMg26WdOWlrUCgdoqL4s0dVwb+Uq1XtTR\nsGPCkgI3cz1WwBVDW0E94IXB4HyAZ7/q0pXDIjz+xzRJQDUVA5mMvYHyHnK0pSex\nVjxvWBQFAwKBgE8XtydMkcvxr8H7dDXT8ztgmXopFGAwdXXPcPChQuQc1RnRrltQ\np8Y3fM7ppEm5LWGqVVgvVzUDhm6YCB1s4oG/W32NS+wtU8Vv14BvoeX46iZA0ogT\n0vo8jlP49Z6CBH1ZJYCgfhqnXBA1YnTOnzU3TSChGsHfMNpaXd4bkFZhAoGBAIXb\nUqCCZsg+mVn9m7puT+auto0HfiU1Ucv+I39fe+XPI/Lzx716EPNYCx9eMW2xt2Cg\nwktonNjZOvVs8kyxM+Nt3hDgmQHJwqrcO7e9NPBBedh3q+B1E99jxfLbZHR+GHid\nr6CjNC92J9bhlS4fb+QwpuCrbmereFKAIU0lfbNdAoGARBUJCCdJRkPzYS2QJlt1\noHfvb6LREhJ27pI+oqUrqIwcjfPY7uRsf3tKwv6wbe/XGexBoRcAwk5D5lXu/Cca\nK4rKj1Nhe6x3/stwXQ/bONmyufohSld5mxrCRMdFlzuNNyZPi1WALAMsyGh1FQ3S\ng3DFlMW09F78JEgDb4ZoI0I=\n-----END PRIVATE KEY-----\n",

        'client_email' : "firebase-adminsdk-vr6ws@kdongsan-8cc40.iam.gserviceaccount.com",

        'client_id' : "113863751594410741120",

        'auth_uri' : "https://accounts.google.com/o/oauth2/auth",

        'token_uri' : "https://oauth2.googleapis.com/token",

        'auth_provider_x509_cert_url' : "https://www.googleapis.com/oauth2/v1/certs",

        'client_x509_cert_url' : "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-vr6ws%40kdongsan-8cc40.iam.gserviceaccount.com"})
    app = firebase_admin.initialize_app(cred)
db = firestore.client()

def process_data(url, code, user_key, rows, dong, what):
    data_list = []    
    
    for date in [previous_month, this_month]:
        query_url = url + f"?&serviceKey={user_key}&LAWD_CD={code}&DEAL_YMD={date.strftime('%Y%m')}&pageNo=1&numOfRows={rows}"
        xml = requests.get(query_url)
        result = xml.text
        soup = BeautifulSoup(result,'lxml-xml')
        items = soup.find_all("item")
        
        for item in items:
            if item.find('buildYear') == None :
                continue
            else:
                년 = item.find("dealYear").text if item.find("dealYear") else ""                           # 계약년도
                월 = item.find("dealMonth").text if item.find("dealMonth") else ""                         # 계약월
                일 = item.find("dealDay").text if item.find("dealDay") else ""                             # 계약일
                법정동 = item.find("umdNm").text if item.find("umdNm") else ""                             # 법정동코드
                아파트 = item.find("aptNm").text if item.find("aptNm") else ""                             # 아파트단지명
                건축년도 = item.find("buildYear").text if item.find("buildYear") else ""                   # 건축년도                 
                층 = item.find("floor").text if item.find("floor") else ""                                 # 층
                거래금액 = item.find("dealAmount").text if item.find("dealAmount") else ""                 # 거래금액(만원)
                전용면적 = item.find("excluUseAr").text if item.find("excluUseAr") else ""                  # 전용면적     

                # data_list.append(','.join((아파트, str(거래금액), str(층), str(전용면적), str(건축년도), 법정동, 거래)))  # 리스트에 추가

                data_list.append({
                    '년': 년,
                    '월': 월,
                    '일': 일,
                    '법정동': 법정동,
                    '아파트': 아파트,
                    '건축년도': 건축년도,
                    '층': 층,
                    '거래금액': 거래금액,
                    '전용면적': 전용면적,
                    })
                
    db.collection(f"{this_month.strftime('%Y.%m.%d')}").document(dong).set({what: data_list}, merge=True)

# 병렬처리
def process_data_threaded(dong, code, url, user_key, rows, what):
    process_data(url, code, user_key, rows, dong, what)

# Thread 리스트 생성
# threads = []

with st.spinner('진행중...'):
    if (datetime.now() + timedelta(hours=9)).date().strftime('%Y.%m.%d') != list(db.collections())[-1].id:
        for dong, code in address.items():        
            thread = threading.Thread(target=process_data_threaded, args=(dong, code, urls['매매'], user_key, rows, '매매'))
            # threads.append(thread)
            thread.start()

        # 모든 스레드가 완료될 때까지 대기
        # for thread in threads:
        #     thread.join()
    else:
        st.error('데이터 중복!!!')

list_range = list(db.collections())[:-3]
for i in list_range:
    target = db.collection(i.id).get()
    for doc in target:
        doc.reference.delete()
st.write("모든 데이터 처리가 완료되었습니다.")
