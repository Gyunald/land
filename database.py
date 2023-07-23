import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from threading import Thread
# from streamlit_autorefresh import st_autorefresh

# st_autorefresh(interval=40800000, limit=2)

choice = st.radio('데이터베이스',['업데이트','삭제'],horizontal=True)
address = {'서울특별시 종로구': '11110', '서울특별시 중구': '11140', '서울특별시 용산구': '11170', '서울특별시 성동구': '11200', '서울특별시 광진구': '11215', '서울특별시 동대문구': '11230', '서울특별시 중랑구': '11260', '서울특별시 성북구': '11290', '서울특별시 강북구': '11305', '서울특별시 도봉구': '11320', '서울특별시 노원구': '11350', '서울특별시 은평구': '11380', '서울특별시 서대문구': '11410', '서울특별시 마포구': '11440', '서울특별시 양천구': '11470', '서울특별시 강서구': '11500', '서울특별시 구로구': '11530', '서울특별시 금천구': '11545', '서울특별시 영등포구': '11560', '서울특별시 동작구': '11590', '서울특별시 관악구': '11620', '서울특별시 서초구': '11650', '서울특별시 강남구': '11680', '서울특별시 송파구': '11710', '서울특별시 강동구': '11740', '부산광역시 중구': '26110', '부산광역시 서구': '26140', '부산광역시 동구': '26170', '부산광역시 영도구': '26200', '부산광역시 부산진구': '26230', '부산광역시 동래구': '26260', '부산광역시 남구': '26290', '부산광역시 북구': '26320', '부산광역시 해운대구': '26350', '부산광역시 사하구': '26380', '부산광역시 금정구': '26410', '부산광역시 강서구': '26440', '부산광역시 연제구': '26470', '부산광역시 수영구': '26500', '부산광역시 사상구': '26530', '부산광역시 기장군': '26710', '대구광역시 중구': '27110', '대구광역시 동구': '27140', '대구광역시 서구': '27170', '대구광역시 남구': '27200', '대구광역시 북구': '27230', '대구광역시 수성구': '27260', '대구광역시 달서구': '27290', '대구광역시 달성군': '27710', '인천광역시 중구': '28110', '인천광역시 동구': '28140', '인천광역시 미추홀구': '28177', '인천광역시 연수구': '28185', '인천광역시 남동구': '28200', '인천광역시 부평구': '28237', '인천광역시 계양구': '28245', '인천광역시 서구': '28260', '인천광역시 강화군':'28710', '광주광역시 동구': '29110', '광주광역시 서구': '29140', '광주광역시 남구': '29155', '광주광역시 북구': '29170', '광주광역시 광산구': '29200', '대전광역시 동구': '30110', '대전광역시 중구': '30140', '대전광역시 서구': '30170', '대전광역시 유성구': '30200', '대전광역시 대덕구': '30230', '울산광역시 중구': '31110', '울산광역시 남구': '31140', '울산광역시 동구': '31170', '울산광역시 북구': '31200', '울산광역시 울주군': '31710', '세종특별자치시': '36110', '수원시 장안구': '41111', '수원시 권선구': '41113', '수원시 팔달구': '41115', '수원시 영통구': '41117', '성남시 수정구': '41131', '성남시 중원구': '41133', '성남시 분당구': '41135', '의정부시': '41150', '안양시 만안구': '41171', '안양시 동안구': '41173', '부천시': '41190', '광명시': '41210', '평택시': '41220', '동두천시': '41250', '안산시 상록구': '41271', '안산시 단원구': '41273', '고양시 덕양구': '41281', '고양시 일산동구': '41285', '고양시 일산서구': '41287', '과천시': '41290', '구리시': '41310', '남양주시': '41360', '오산시': '41370', '시흥시': '41390', '군포시': '41410', '의왕시': '41430', '하남시': '41450', '용인시 처인구': '41461', '용인시 기흥구': '41463', '용인시 수지구': '41465', '파주시': '41480', '이천시': '41500', '안성시': '41550', '김포시': '41570', '화성시': '41590', '광주시': '41610', '양주시': '41630', '포천시': '41650', '여주시': '41670', '연천군': '41800', '가평군': '41820', '양평군': '41830', '춘천시': '42110', '원주시': '42130', '강릉시': '42150', '동해시': '42170', '태백시': '42190', '속초시': '42210', '삼척시': '42230', '홍천군': '42720', '횡성군': '42730', '영월군': '42750', '평창군': '42760', '정선군': '42770', '철원군': '42780', '화천군': '42790', '양구군': '42800', '인제군': '42810', '강원 고성군': '42820', '양양군': '42830', '청주시 상당구': '43111', '청주시 서원구': '43112', '청주시 흥덕구': '43113', '청주시 청원구': '43114', '충주시': '43130', '제천시': '43150', '보은군': '43720', '옥천군': '43730', '영동군': '43740', '증평군': '43745', '진천군': '43750', '괴산군': '43760', '음성군': '43770', '단양군': '43800', '천안시 동남구': '44131', '천안시 서북구': '44133', '공주시': '44150', '보령시': '44180', '아산시': '44200', '서산시': '44210', '논산시': '44230', '계룡시': '44250', '당진시': '44270', '금산군': '44710', '부여군': '44760', '서천군': '44770', '청양군': '44790', '홍성군': '44800', '예산군': '44810', '태안군': '44825', '전주시 완산구': '45111', '전주시 덕진구': '45113', '군산시': '45130', '익산시': '45140', '정읍시': '45180', '남원시': '45190', '김제시': '45210', '완주군': '45710', '진안군': '45720', '무주군': '45730', '장수군': '45740', '임실군': '45750', '순창군': '45770', '고창군': '45790', '부안군': '45800', '목포시': '46110', '여수시': '46130', '순천시': '46150', '나주시': '46170', '광양시': '46230', '담양군': '46710', '곡성군': '46720', '구례군': '46730', '고흥군': '46770', '보성군': '46780', '화순군': '46790', '장흥군': '46800', '강진군': '46810', '해남군': '46820', '영암군': '46830', '무안군': '46840', '함평군': '46860', '영광군': '46870', '장성군': '46880', '완도군': '46890', '진도군': '46900', '신안군': '46910', '포항시 남구': '47111', '포항시 북구': '47113', '경주시': '47130', '김천시': '47150', '안동시': '47170', '구미시': '47190', '영주시': '47210', '영천시': '47230', '상주시': '47250', '문경시': '47280', '경산시': '47290', '군위군': '47720', '의성군': '47730', '청송군': '47750', '영양군': '47760', '영덕군': '47770', '청도군': '47820', '고령군': '47830', '성주군': '47840', '칠곡군': '47850', '예천군': '47900', '봉화군': '47920', '울진군': '47930', '울릉군': '47940', '창원시 의창구': '48121', '창원시 성산구': '48123', '창원시 마산합포구': '48125', '창원시 마산회원구': '48127', '창원시 진해구': '48129', '진주시': '48170', '통영시': '48220', '사천시': '48240', '김해시': '48250', '밀양시': '48270', '거제시': '48310', '양산시': '48330', '의령군': '48720', '함안군': '48730', '창녕군': '48740', '경남 고성군': '48820','남해군': '48840', '하동군': '48850', '산청군': '48860', '함양군': '48870', '거창군': '48880', '합천군': '48890', '제주시': '50110', '서귀포시': '50130'}
    
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
    empty = st.empty()
    login_code = empty.text_input('업데이트 코드', type='password')
    
    if login_code == st.secrets.login_code :
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
            
        empty.empty()
        st.success('접속 완료')
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
                
    elif login_code != '' and st.secrets.login_code :
        st.warning('코드 오류')
        
if choice == '삭제' :
    db = firestore.client()
    empty = st.empty()
    login_code2 = empty.text_input('삭제 코드 ', type='password')

    if login_code2 == st.secrets.login_code :
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
            
        empty.success('접속 완료')
        for i in list(db.collections())[:-5]:
            c = 0
            db = firestore.client()
            db = db.collection(i.id).get()
            with st.spinner(f"{i.id} 삭제중...") :
                for doc in db:
                    doc.reference.delete()
                    c += (100/len(address))
                    empty.progress(int(c)+1)
                empty.empty()
                st.warning('삭제 완료')
                
    elif login_code2 != '' and login_code2:
        st.warning('코드 오류')

# st.write(list(db.collections()))
