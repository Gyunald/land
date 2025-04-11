import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

if 'gold' not in st.session_state:
    st.session_state.gold = 0

def scrape_naver_gold_prices(url='https://finance.naver.com/marketindex/goldDailyQuote.naver'):

    # Send HTTP request to the URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
        return None
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the gold price table
    table = soup.find('table', class_='tbl_exchange')
    
    if not table:
        print("Could not find the gold price table")
        return None
    
    # Initialize lists to store data
    prices = []
    # Extract data from each row
    rows = table.find('tbody').find_all('tr')
    
    for row in rows:
        # <td class="num">146,855.32</td>
        price_cells = row.find_all('td', class_='num')
        if len(price_cells) >= 1:
            # Extract the gold price (first numeric cell)
            price_text = price_cells[0].text.strip()
            prices.append(price_text)

    return prices[0]

# Example usage
if __name__ == "__main__":
    url = 'https://finance.naver.com/marketindex/goldDailyQuote.naver'

    if st.session_state.gold == 0:
        gold_data = scrape_naver_gold_prices(url)
        st.session_state.gold = gold_data
    else:
        pass

    gold_data = st.session_state.gold

    #bt = st.button('실시간 금 시세 갱신',use_container_width=False,type='primary')

    #if bt:
        #gold_data = scrape_naver_gold_prices(url)
       # st.session_state.gold = gold_data

    
    gold_data2 = float(gold_data.replace(',', ''))

    st.button(f"###### 현재 금 시세: {gold_data2:,.0f}/g", type='tertiary', use_container_width=True)

    # c1,c2 = st.columns(2)
    if gold_data is not None:
        gold_data = float(gold_data.replace(',', ''))

        a = st.radio('함량', ['14k', '18k', '24k'],label_visibility="collapsed", horizontal=True)
        b = st.radio('단위', ['돈', 'g'],label_visibility="collapsed", horizontal=True)
        
        weight = st.number_input('중량', value=1.0, step=0.01)
        diamond_weight = st.number_input('다이아몬드 중량 (캐럿)', value=0.0, step=0.1, help='※ 1부 = 0.1캐럿')

        # Convert diamond weight from carats to grams (1 carat = 0.2g)
        diamond_weight_in_grams = diamond_weight * 0.2
        
        if a == '14k':
            purity_factor = 0.58
        elif a == '18k':
            purity_factor = 0.75
        elif a == '24k':
            purity_factor = 1.0
            
        gold_price_per_gram = gold_data * purity_factor

        if b == 'g':
            # Subtract diamond weight from total weight for gold calculation
            gold_weight = max(0, (weight - diamond_weight_in_grams) * purity_factor)
            result = gold_weight * gold_price_per_gram
            st.info(f"###### 순수 금 중량: {gold_weight:.2f}g\n###### KRW: {result:,.0f}원")

            #함량: {a}\n총 중량: {float(weight):.2f}g\n다이아몬드 중량: {diamond_weight_in_grams:.2f}g\n
        
        if b == '돈':
            # Convert to grams first (1 돈 = 3.75g), then subtract diamond weight
            weight_in_grams = weight * 3.75
            gold_weight = max(0, (weight_in_grams - diamond_weight_in_grams) * purity_factor)
            result = gold_weight * gold_price_per_gram
            st.info(f"\n순수 금 중량: {gold_weight:.2f}g\n###### KRW: {result:,.0f}원")
            
            #함량: {a}\n총 중량: {weight_in_grams:.2f}g\n다이아몬드 중량: {diamond_weight_in_grams:.2f}g 
