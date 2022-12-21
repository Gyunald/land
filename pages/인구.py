import pandas as pd
import streamlit as st
import datetime

file_path = 'https://raw.githubusercontent.com/Gyunald/streamlit-view/main/population/'
rename_columns = {'합계':'파주시','등록인구':'인구','등록인구.3' : '내국인', '등록인구.6': '외국인'}
drop_colums = ['시점','등록인구.1','등록인구.2','등록인구.4','등록인구.5','등록인구.7','등록인구.8']
drop_indexs = ['읍면동별(1)']

def csv_file(year):
    a = pd.read_csv(f'{file_path}{year}.csv',index_col=1,encoding='cp949')
    a = a.drop(drop_indexs,axis=0)
    a = a.drop(drop_colums,axis=1)
    a.rename(columns=rename_columns, index=rename_columns, inplace=True)
    return a

def draw_color(x,color): 
    color = f"background-color : {color}"
    return [color]

def color_negative_red(val):
    color = '#4682B4' if val < 0 else '#ff7f0e'
    # return 'background-color: %s' % color
    return 'color: %s' % color

def m(month):
    c = (18 * month) - 18
    c2 = 18 * month
    globals()[f"date_{year}_{month}"] = csv_file(year)[c:c2].astype('int32')
    return globals()

def sub(month):
    for month in range(month, month-2,-1):
        c = (18 * month) - 18
        c2 = 18 * month
        globals()[f"date_{year}_{month}"] = csv_file(year)[c:c2].astype('int32')
    return globals()

try:
    c1,c2=st.columns([1,1])

    with c1:
        today = datetime.date.today()
        year = today.year
        value_date = today - datetime.timedelta(days=30)
        date = st.slider(f"{year} 🐱‍🏍",1,12, value=value_date.month)

    with st.expander(f"파주시 인구 - {year}.{date}"):
        if date :
            m(date)
            st.table(globals()[f"date_{year}_{date}"].style.format("{:,}"))
        
    c3,c4 = st.columns([1,1])

    with st.expander('운정신도시 인구',expanded=True):
        use_container = True

        if len(globals()[f"date_{year}_{date}"]) > 0 :
            파주합계 = globals()[f"date_{year}_{date}"][0:1]
            
            total = globals()[f"date_{year}_{date}"].iloc[0,1]

            운정합계 = globals()[f"date_{year}_{date}"] = globals()[f"date_{year}_{date}"][11:15]
            globals()[f"date_{year}_{date}"].loc['운정'] = globals()[f"date_{year}_{date}"][['세대수','인구','내국인','외국인']].sum().astype('int32')

            subtotal = globals()[f"date_{year}_{date}"].iloc[4,1]

            총합 = pd.concat([파주합계,운정합계],axis=0,sort=False)
            
            st.dataframe(총합.style.apply(draw_color, color='#17becf', subset=pd.IndexSlice[['운정'],'인구'],axis=1).apply(draw_color, color='#FFA07A', subset=pd.IndexSlice[['파주시'],'인구'],axis=1).format('{:,}'),use_container_width=use_container)

            st.info(f"👨‍👩‍👧‍👦 운정 비율 : { (subtotal / total) * 100:.2f} %")
        else:
            st.write('No Data')

        sub(date)    
        g = globals()[f"date_{year}_{date}"] - globals()[f"date_{year}_{date-1}"]

        if g['세대수'][0] > 0 :
            st.dataframe(g.style.applymap(color_negative_red).format('{:+,}'),use_container_width=use_container)
        else:
            st.dataframe(g.fillna('-'))

    st.success("📣 [GTX 운정신도시 정보공유방](%s)" % 'https://open.kakao.com/o/gICcjcDb')
    st.warning('참여코드 : gtxa24')
      
except Exception as e:
    st.write(e)
