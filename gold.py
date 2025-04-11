# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import streamlit as st

# if 'gold' not in st.session_state:
#     st.session_state.gold = 0

# def scrape_naver_gold_prices(url='https://finance.naver.com/marketindex/goldDailyQuote.naver'):

#     # Send HTTP request to the URL
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
#     response = requests.get(url, headers=headers)
    
#     # Check if the request was successful
#     if response.status_code != 200:
#         print(f"Failed to retrieve the webpage: {response.status_code}")
#         return None
    
#     # Parse the HTML content
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     # Find the gold price table
#     table = soup.find('table', class_='tbl_exchange')
    
#     if not table:
#         print("Could not find the gold price table")
#         return None
    
#     # Initialize lists to store data
#     prices = []
#     # Extract data from each row
#     rows = table.find('tbody').find_all('tr')
    
#     for row in rows:
#         # <td class="num">146,855.32</td>
#         price_cells = row.find_all('td', class_='num')
#         if len(price_cells) >= 1:
#             # Extract the gold price (first numeric cell)
#             price_text = price_cells[0].text.strip()
#             prices.append(price_text)

#     return prices[0]

# # Example usage
# if __name__ == "__main__":
#     url = 'https://finance.naver.com/marketindex/goldDailyQuote.naver'

#     if st.session_state.gold == 0:
#         gold_data = scrape_naver_gold_prices(url)
#         st.session_state.gold = gold_data
#     else:
#         pass
        
#     gold_data = st.session_state.gold
#     gold_data2 = float(gold_data.replace(',', ''))
    
#     #bt = st.button('실시간 금 시세 갱신',use_container_width=False,type='primary')

#     bt = st.button('현재 금 시세 조회하기', use_container_width=False)
#     bt2 = st.button(f"{gold_data2:,.0f}/g", type='tertiary',)
    
#     #type="primary", "secondary", or "tertiary"
    
#     if bt:
#         gold_data = scrape_naver_gold_prices(url)
#         st.session_state.gold = gold_data

#     # c1,c2 = st.columns(2)
#     if gold_data is not None:
#         gold_data = float(gold_data.replace(',', ''))

#         a = st.radio('함량', ['14k', '18k', '24k'],label_visibility="collapsed", horizontal=True)
#         b = st.radio('단위', ['돈', 'g'],label_visibility="collapsed", horizontal=True)
        
#         weight = st.number_input('중량', value=1.0, step=0.01)
#         diamond_weight = st.number_input('다이아몬드 중량 (캐럿)', value=0.0, step=0.1, help='※ 1부 = 0.1캐럿')

#         # Convert diamond weight from carats to grams (1 carat = 0.2g)
#         diamond_weight_in_grams = diamond_weight * 0.2
        
#         if a == '14k':
#             purity_factor = 0.58
#         elif a == '18k':
#             purity_factor = 0.75
#         elif a == '24k':
#             purity_factor = 1.0
            
#         gold_price_per_gram = gold_data * purity_factor

#         if b == 'g':
#             # Subtract diamond weight from total weight for gold calculation
#             gold_weight = max(0, (weight - diamond_weight_in_grams) * purity_factor)
#             result = gold_weight * gold_price_per_gram
#             st.info(f"###### 순수 금 중량: {gold_weight:.2f}g\n###### :orange[KRW: {result:,.0f}원]")

#             #함량: {a}\n총 중량: {float(weight):.2f}g\n다이아몬드 중량: {diamond_weight_in_grams:.2f}g\n
        
#         if b == '돈':
#             # Convert to grams first (1 돈 = 3.75g), then subtract diamond weight
#             weight_in_grams = weight * 3.75
#             gold_weight = max(0, (weight_in_grams - diamond_weight_in_grams) * purity_factor)
#             result = gold_weight * gold_price_per_gram
#             st.info(f"###### 순수 금 중량: {gold_weight:.2f}g\n###### :orange[KRW: {result:,.0f}원]")
            
#             #함량: {a}\n총 중량: {weight_in_grams:.2f}g\n다이아몬드 중량: {diamond_weight_in_grams:.2f}g\n


import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

st.markdown('''
<style>
.stApp [data-testid="stHeader"] {visibility: hidden;}
div[class^='block-container'] { padding-top: 1rem; }
</style>
''', unsafe_allow_html=True)

# 세션 상태 초기화
if 'gold_price' not in st.session_state:
    st.session_state.gold_price = 0

def scrape_naver_gold_prices(url='https://finance.naver.com/marketindex/goldDailyQuote.naver'):
    """네이버 금융에서 금 시세를 스크랩하는 함수"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 발생
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='tbl_exchange')
        
        if not table:
            st.error("금 시세 테이블을 찾을 수 없습니다.")
            return None
        
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            price_cells = row.find_all('td', class_='num')
            if len(price_cells) >= 1:
                price_text = price_cells[0].text.strip()
                return price_text
        
        st.error("시세 정보를 찾을 수 없습니다.")
        return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"웹페이지 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return None

def calculate_gold_value(purity, unit, weight, diamond_weight, gold_price_per_gram):
    """금 가치를 계산하는 함수"""
    # 순도 계수 설정
    purity_factors = {
        '14k': 0.58,
        '18k': 0.75,
        '24k': 1.0
    }
    purity_factor = purity_factors[purity]
    
    # 다이아몬드 무게를 그램으로 변환 (1캐럿 = 0.2g)
    diamond_weight_in_grams = diamond_weight * 0.2
    
    # 단위 변환 및 계산
    if unit == '돈':
        # 1돈 = 3.75g
        weight_in_grams = weight * 3.75
    else:
        weight_in_grams = weight
    
    # 순수 금 무게 계산 (총 무게에서 다이아몬드 무게 제외)
    pure_gold_weight = max(0, weight_in_grams - diamond_weight_in_grams)
    gold_weight = pure_gold_weight * purity_factor
    
    # 금 가격 계산 (순수 24K 금 시세 × 실제 함유된 금 무게)
    gold_value = gold_price_per_gram * gold_weight
    
    return gold_weight, gold_value

def main():
    # st.title("금 시세 계산기")
    
    # 초기 금 시세 가져오기
    url = 'https://finance.naver.com/marketindex/goldDailyQuote.naver'
    if st.session_state.gold_price == 0:
        gold_data = scrape_naver_gold_prices(url)
        if gold_data:
            st.session_state.gold_price = gold_data
    
    # 금 시세 표시
    if st.session_state.gold_price:
        gold_data = st.session_state.gold_price
        gold_price_numeric = float(gold_data.replace(',', ''))
        
        if st.button(f'# 현재 금 시세 조회하기\n {gold_price_numeric:,.0f}/g', use_container_width=True):
            gold_data = scrape_naver_gold_prices(url)
            if gold_data:
                st.session_state.gold_price = gold_data
                gold_price_numeric = float(gold_data.replace(',', ''))      
                st.toast("금 시세가 갱신되었습니다.", icon='🌟')
                # st.rerun()
        col1, col2 = st.columns(2)
        
        with col1:
            purity = st.radio('함량', ['14k', '18k', '24k'], label_visibility="collapsed", horizontal=True,)

        with col2:
            unit = st.radio('단위', ['돈', 'g'], label_visibility="collapsed", horizontal=True)
        
        # 무게 입력
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input('중량', value=0.0, step=0.01",min_value=0.0, format="%.2f")
        
        with col2:
            diamond_weight = st.number_input('다이아몬드 중량 (캐럿)', 
                                             value=0.0, 
                                             step=0.1,
                                             min_value=0.0,
                                             format="%.2f",
                                             help='※ 1부 = 0.1캐럿')
        
        # 계산 실행
        gold_weight, gold_value = calculate_gold_value(
            purity, unit, weight, diamond_weight, gold_price_numeric
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("순수 금 중량", f"{gold_weight:.2f}g")
        
        with col2:
            st.metric("예상 가격", f"{gold_value:,.0f}원")
        
        # 상세 정보
        with st.expander("상세 정보"):
            st.write(f"- 현재 금 시세: {gold_price_numeric:,.2f}원/g")
            st.write(f"- 함량: {purity} (순도 계수: {0.58 if purity=='14k' else 0.75 if purity=='18k' else 1.0})")
            if unit == '돈':
                st.write(f"- 입력 중량: {weight:.2f}돈 ({weight*3.75:.2f}g)")
            else:
                st.write(f"- 입력 중량: {weight:.2f}g ({weight/3.75:.2f}돈)")
            
            if diamond_weight > 0:
                st.write(f"- 다이아몬드 중량: {diamond_weight:.2f}캐럿 ({diamond_weight*0.2:.2f}g)")

if __name__ == "__main__":
    main()
