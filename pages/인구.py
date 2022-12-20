import pandas as pd
import streamlit as st

main_year = 2
main_month = 11
year = 2020, 2021, 2022

file_path = 'https://raw.githubusercontent.com/Gyunald/streamlit-view/main/population/'
rename_columns = {'등록인구':'인구','등록인구.3' : '내국인', '등록인구.6': '외국인'}
rename_index = {'합계':'파주'}
drop_colums = ['시점','등록인구.1','등록인구.2','등록인구.4','등록인구.5','등록인구.7','등록인구.8']
drop_indexs = ['읍면동별(1)']

def csv_file(year):
    a = pd.read_csv(f'{file_path}{year}.csv',index_col=1)
    a = a.drop(drop_indexs,axis=0)
    a = a.drop(drop_colums,axis=1)
    a.rename(columns=rename_columns,index=rename_index, inplace=True)
    a = a.astype(int)
    return a

def draw_color(x,color): 
    color = f"background-color : {color}"
    return [color]

def color_negative_red(val):
    color = '#FFA07A' if val < 0 else '#4682B4'
    # return 'background-color: %s' % color
    return 'color: %s' % color

def m(month):
    c = (18 * month) - 18
    c2 = 18 * month
    globals()[f"date_{select_year}_{month}"] = csv_file(select_year)[c:c2].astype(int)
    return globals()

def m_output():
    if len(globals()[f"date_{select_year}_{month}"]) > 0 :
        st.table(globals()[f"date_{select_year}_{month}"][0:1].style.apply(draw_color, color='#FFA07A', subset=pd.IndexSlice[['파주시'],'인구'],axis=1).format('{:,}'))
        total = globals()[f"date_{select_year}_{month}"].iloc[0,1]
        globals()[f"date_{select_year}_{month}"] = globals()[f"date_{select_year}_{month}"][11:15]
        globals()[f"date_{select_year}_{month}"].loc['합계'] = globals()[f"date_{select_year}_{month}"][['세대수','인구','내국인','외국인']].sum()
        st.dataframe(globals()[f"date_{select_year}_{month}"].style.apply(draw_color, color='#17becf', subset=pd.IndexSlice[['합계'],'인구'],axis=1).format('{:,}'))        
        subtotal = globals()[f"date_{select_year}_{month}"].iloc[4,1]
        
        st.info(f"인구 비율 : { (subtotal / total) * 100:.2f} %")
        st.success('GTX 운정신도시 오픈챗 https://open.kakao.com/o/gICcjcDb')
        st.warning('참여코드 : 2023gtxa')
        
        
    else:
        st.write('No Data')
    return globals()

def sub(month):
    for month in range(month, month-2,-1):
        c = (18 * month) - 18
        c2 = 18 * month
        globals()[f"date_{select_year}_{month}"] = csv_file(select_year)[c:c2].astype(int)
    return globals()
try:
    c1,c2=st.columns([1,1])
    with c1:
        select_year = st.selectbox('Year', year, main_year)
        if select_year:
            csv_file(select_year)
            
    with c2:
        month = st.selectbox('Month',range(1,12+1),main_month-1)
    with st.expander(f"파주시 인구 - {month}월"):
        if select_year :
            m(month)
            st.dataframe(globals()[f"date_{select_year}_{month}"].style.format("{:,}"))
        
    c3,c4 = st.columns([1,1])
    with c3:
        with st.expander('파주시'):
            if select_year :
                m(month)
                m_output()

    with c4:
        with st.expander('운정'):
            sub(month)    
            g = globals()[f"date_{select_year}_{month}"] - globals()[f"date_{select_year}_{month-1}"]
            g.rename({'파주':'전월 대비'},inplace=True)
            st.dataframe(g.style.applymap(color_negative_red).format('{:+,}'))
except Exception as e:
    st.write(e)
