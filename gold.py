
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# st.markdown('''
# <style>
# .stApp [data-testid="stHeader"] {visibility: hidden;}
# div[class^='block-container'] { padding-top: 1rem; }
# </style>
# ''', unsafe_allow_html=True)

# 세션 상태 초기화
if 'gold_price' not in st.session_state:
    st.session_state.gold_price = None
    
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
        '14k': 0.585,
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
    if st.session_state.gold_price == None:
        gold_data = scrape_naver_gold_prices(url)
        if gold_data:
            st.session_state.gold_price = gold_data
    
    # 금 시세 표시
    if st.session_state.gold_price != None:
        gold_data = st.session_state.gold_price
        gold_price_numeric = float(gold_data.replace(',', ''))

        if st.button(f'# 현재 금 시세 조회하기', use_container_width=True, type='primary'):
            st.toast("금 시세가 갱신되었습니다.", icon='🌟')
            gold_data = scrape_naver_gold_prices(url)
            
            if gold_data:
                st.session_state.gold_price = gold_data
                gold_price_numeric = float(gold_data.replace(',', ''))
                
        # e = st.empty()
        bt = st.button(f'{gold_price_numeric:,.0f}/g', use_container_width=True, type='tertiary')
        if bt :
            # e.empty()
            gold_price_numeric = st.number_input('직접입력',value=0)
            
            if gold_price_numeric:
                gold_price_numeric = float(gold_data.replace(',', ''))

        col1, col2 = st.columns(2)
        
        with col1:
            purity = st.radio('함량', ['14k', '18k', '24k'], label_visibility="collapsed", horizontal=True,)

        with col2:
            unit = st.radio('단위', ['돈', 'g'], label_visibility="collapsed", horizontal=True)
        
        # 무게 입력
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input('중량', value=0.00, step=0.01, min_value=0.0, format="%.2f")

            
        with col2:
            diamond_weight = st.number_input('다이아몬드 중량 (캐럿)', 
                                             value=0.00, 
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
        with st.expander("상세 정보",expanded=True):
            st.write(f"- 현재 금 시세: {gold_price_numeric:,.2f}원/g")
            st.write(f"- 함량: {purity} (순도: {'58.5%' if purity=='14k' else '75.00%' if purity=='18k' else '99.99%'})")
            if unit == '돈':
                st.write(f"- 입력 중량: {weight:.2f}돈 ({weight*3.75:.2f}g)")
            else:
                st.write(f"- 입력 중량: {weight:.2f}g ({weight/3.75:.2f}돈)")
            
            if diamond_weight > 0:
                st.write(f"- 다이아몬드 중량: {diamond_weight:.2f}캐럿 ({diamond_weight*0.2:.2f}g)")

if __name__ == "__main__":
    main()
