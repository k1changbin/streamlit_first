import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# 페이지 설정
st.set_page_config(
    page_title="종합 데이터 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 앱 제목 및 소개
st.title('종합 데이터 분석 대시보드')

st.markdown("""
이 대시보드는 판매 데이터를 종합적으로 분석하고 시각화합니다.
다양한 차트와 필터를 통해 데이터를 탐색하고 인사이트를 발견하세요.
""")

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 샘플 데이터 생성 (실제 앱에서는 CSV 파일을 로드하거나 데이터베이스에서 가져옴)
    np.random.seed(42)
    
    # 날짜 범위
    date_range = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # 제품 카테고리 및 지역
    categories = ['의류', '전자제품', '식품', '가구', '화장품']
    regions = ['서울', '부산', '인천', '대구', '광주', '대전', '울산', '세종']
    channels = ['온라인', '오프라인', '모바일']
    
    # 데이터 생성
    data = []
    
    for _ in range(10000):  # 10,000개 샘플 생성
        # date = np.random.choice(date_range)
        date = pd.Timestamp(np.random.choice(date_range))
        category = np.random.choice(categories)
        region = np.random.choice(regions)
        channel = np.random.choice(channels)
        
        # 카테고리별 가격 범위 설정
        if category == '전자제품':
            price = np.random.randint(50000, 1500000)
            quantity = np.random.randint(1, 5)
        elif category == '가구':
            price = np.random.randint(30000, 1000000)
            quantity = np.random.randint(1, 3)
        elif category == '의류':
            price = np.random.randint(10000, 200000)
            quantity = np.random.randint(1, 10)
        elif category == '화장품':
            price = np.random.randint(5000, 100000)
            quantity = np.random.randint(1, 8)
        else:  # 식품
            price = np.random.randint(1000, 50000)
            quantity = np.random.randint(1, 20)
            
        # 계절성 효과
        month = date.month
        if month in [12, 1, 2]:  # 겨울
            seasonal_factor = 1.2 if category in ['의류', '전자제품'] else 0.9
        elif month in [3, 4, 5]:  # 봄
            seasonal_factor = 1.1 if category in ['의류', '화장품'] else 1.0
        elif month in [6, 7, 8]:  # 여름
            seasonal_factor = 0.8 if category == '의류' else 1.1
        else:  # 가을
            seasonal_factor = 1.0
            
        # 주말 효과
        weekend_factor = 1.3 if date.dayofweek >= 5 else 1.0
        
        # 최종 판매량 조정
        quantity = max(1, int(quantity * seasonal_factor * weekend_factor))
        
        # 할인 여부
        
        discount = np.random.choice([True, False], p=[0.3, 0.7])
        discount_rate = np.random.randint(5, 30) / 100 if discount else 0
        
        # 최종 가격 계산
        final_price = price * (1 - discount_rate)
        revenue = final_price * quantity
        
        data.append({
            'date': date,
            'category': category,
            'region': region,
            'channel': channel,
            'price': price,
            'discount': discount,
            'discount_rate': discount_rate,
            'final_price': final_price,
            'quantity': quantity,
            'revenue': revenue,
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'dayofweek': date.dayofweek,
            'weekend': date.dayofweek >= 5,
            'quarter': (date.month - 1) // 3 + 1
        })
    
    return pd.DataFrame(data)

# 데이터 로드
with st.spinner('데이터를 로드하는 중...'):
    df = load_data()

# 사이드바 필터
st.sidebar.header('데이터 필터')

# 날짜 범위 선택
date_min = df['date'].min().date()
date_max = df['date'].max().date()
selected_dates = st.sidebar.date_input(
    "날짜 범위 선택",
    [date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    df_filtered = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
else:
    df_filtered = df.copy()

# 카테고리 선택
all_categories = df['category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "제품 카테고리",
    options=all_categories,
    default=all_categories
)

if selected_categories:
    df_filtered = df_filtered[df_filtered['category'].isin(selected_categories)]

# 지역 선택
all_regions = df['region'].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "지역",
    options=all_regions,
    default=all_regions
)

if selected_regions:
    df_filtered = df_filtered[df_filtered['region'].isin(selected_regions)]

# 채널 선택
all_channels = df['channel'].unique().tolist()
selected_channels = st.sidebar.multiselect(
    "판매 채널",
    options=all_channels,
    default=all_channels
)

if selected_channels:
    df_filtered = df_filtered[df_filtered['channel'].isin(selected_channels)]

# 할인 필터
discount_filter = st.sidebar.radio(
    "할인 여부",
    options=["모두", "할인 상품만", "정가 상품만"]
)

if discount_filter == "할인 상품만":
    df_filtered = df_filtered[df_filtered['discount'] == True]
elif discount_filter == "정가 상품만":
    df_filtered = df_filtered[df_filtered['discount'] == False]

# 필터링된 데이터가 없을 경우 처리
if df_filtered.empty:
    st.error("선택한 필터에 해당하는 데이터가 없습니다. 필터를 조정해주세요.")
    st.stop()

# 주요 지표
st.header('주요 판매 지표')

# 지표 계산
total_revenue = df_filtered['revenue'].sum()
total_orders = len(df_filtered)
total_units = df_filtered['quantity'].sum()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

# 지표 표시
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 매출", f"{total_revenue:,.0f}원")
col2.metric("총 주문 수", f"{total_orders:,}건")
col3.metric("총 판매 수량", f"{total_units:,}개")
col4.metric("평균 주문 금액", f"{avg_order_value:,.0f}원")

# 시간별 매출 추이
st.header('시간별 매출 추이')

# 시간 단위 선택
time_unit = st.radio(
    "시간 단위",
    options=["일별", "주별", "월별", "분기별"],
    horizontal=True
)

# 시간 단위에 따른 데이터 집계
if time_unit == "일별":
    time_data = df_filtered.groupby('date')['revenue'].sum().reset_index()
    x_col = 'date'
    x_title = '날짜'
elif time_unit == "주별":
    df_filtered['week'] = df_filtered['date'].dt.isocalendar().week
    df_filtered['year_week'] = df_filtered['date'].dt.strftime('%Y-%U')
    time_data = df_filtered.groupby('year_week')['revenue'].sum().reset_index()
    x_col = 'year_week'
    x_title = '주차'
elif time_unit == "월별":
    df_filtered['year_month'] = df_filtered['date'].dt.strftime('%Y-%m')
    time_data = df_filtered.groupby('year_month')['revenue'].sum().reset_index()
    x_col = 'year_month'
    x_title = '월'
else:  # 분기별
    df_filtered['year_quarter'] = df_filtered['date'].dt.strftime('%Y-Q') + df_filtered['quarter'].astype(str)
    time_data = df_filtered.groupby('year_quarter')['revenue'].sum().reset_index()
    x_col = 'year_quarter'
    x_title = '분기'

# 시간별 매출 차트
fig_time = px.line(
    time_data,
    x=x_col,
    y='revenue',
    title=f'{time_unit} 매출 추이',
    labels={x_col: x_title, 'revenue': '매출'},
    template='plotly_white'
)

fig_time.update_layout(
    xaxis_tickangle=-45,
    yaxis=dict(tickformat=",.0f")
)

st.plotly_chart(fig_time, use_container_width=True)

# 분석 대시보드
st.header('세부 분석')

# 탭 설정
tab1, tab2, tab3 = st.tabs(["카테고리 분석", "지역 분석", "채널 분석"])

with tab1:
    st.subheader('카테고리별 분석')
    
    # 카테고리별 매출 비중
    cat_revenue = df_filtered.groupby('category')['revenue'].sum().reset_index()
    cat_revenue = cat_revenue.sort_values('revenue', ascending=False)
    
    fig_cat_rev = px.pie(
        cat_revenue,
        values='revenue',
        names='category',
        title='카테고리별 매출 비중',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # 카테고리별 평균 주문 금액 및 수량
    cat_avg = df_filtered.groupby('category').agg({
        'revenue': 'mean',
        'quantity': 'mean',
        'discount_rate': 'mean'
    }).reset_index()
    
    cat_avg.columns = ['category', '평균 주문 금액', '평균 주문 수량', '평균 할인율']
    cat_avg['평균 할인율'] = cat_avg['평균 할인율'] * 100  # 퍼센트로 변환
    
    fig_cat_avg = px.bar(
        cat_avg,
        x='category',
        y=['평균 주문 금액', '평균 주문 수량', '평균 할인율'],
        title='카테고리별 평균 지표',
        barmode='group',
        labels={'category': '카테고리', 'value': '값', 'variable': '지표'},
        template='plotly_white'
    )
    
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.plotly_chart(fig_cat_rev, use_container_width=True)
    
    with col_cat2:
        st.plotly_chart(fig_cat_avg, use_container_width=True)
    
    # 카테고리별 시간 추이
    if time_unit == "일별":
        df_time_cat = df_filtered.groupby(['date', 'category'])['revenue'].sum().reset_index()
        x_col = 'date'
    elif time_unit == "주별":
        df_time_cat = df_filtered.groupby(['year_week', 'category'])['revenue'].sum().reset_index()
        x_col = 'year_week'
    elif time_unit == "월별":
        df_time_cat = df_filtered.groupby(['year_month', 'category'])['revenue'].sum().reset_index()
        x_col = 'year_month'
    else:  # 분기별
        df_time_cat = df_filtered.groupby(['year_quarter', 'category'])['revenue'].sum().reset_index()
        x_col = 'year_quarter'
    
    fig_time_cat = px.line(
        df_time_cat,
        x=x_col,
        y='revenue',
        color='category',
        title=f'카테고리별 {time_unit} 매출 추이',
        labels={x_col: x_title, 'revenue': '매출', 'category': '카테고리'},
        template='plotly_white'
    )
    
    fig_time_cat.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(tickformat=",.0f")
    )
    
    st.plotly_chart(fig_time_cat, use_container_width=True)

with tab2:
    st.subheader('지역별 분석')
    
    # 지역별 매출
    region_revenue = df_filtered.groupby('region')['revenue'].sum().reset_index()
    region_revenue = region_revenue.sort_values('revenue', ascending=False)
    
    fig_region = px.bar(
        region_revenue,
        x='region',
        y='revenue',
        title='지역별 총 매출',
        labels={'region': '지역', 'revenue': '매출'},
        color='revenue',
        color_continuous_scale='Viridis',
        template='plotly_white'
    )
    
    fig_region.update_layout(
        yaxis=dict(tickformat=",.0f")
    )
    
    st.plotly_chart(fig_region, use_container_width=True)
    
    # 지역 및 카테고리별 히트맵
    region_cat = df_filtered.groupby(['region', 'category'])['revenue'].sum().reset_index()
    region_cat_pivot = region_cat.pivot(index='region', columns='category', values='revenue')
    
    fig_heatmap = px.imshow(
        region_cat_pivot,
        labels=dict(x="카테고리", y="지역", color="매출"),
        x=region_cat_pivot.columns,
        y=region_cat_pivot.index,
        color_continuous_scale='Viridis',
        title='지역 및 카테고리별 매출 히트맵',
        text_auto=True,
        aspect="auto"
    )
    
    fig_heatmap.update_traces(
        texttemplate='%{z:,.0f}',
        textfont=dict(size=10)
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.subheader('채널별 분석')
    
    # 채널별 매출 및 주문 수
    channel_data = df_filtered.groupby('channel').agg({
        'revenue': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    # 서브플롯 생성
    fig_channel = make_subplots(
        rows=1, cols=2,
        subplot_titles=('채널별 매출', '채널별 판매 수량'),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )
    
    # 매출 파이 차트
    fig_channel.add_trace(
        go.Pie(
            labels=channel_data['channel'],
            values=channel_data['quantity'],
            name='수량',
            hole=0.4,
            marker_colors=px.colors.qualitative.Set3
        ),
        row=1, col=2
    )
    
    fig_channel.update_layout(
        title_text='채널별 매출 및 판매 수량 비교',
        height=450
    )
    
    st.plotly_chart(fig_channel, use_container_width=True)
    
    # 채널별 시간 추이
    if time_unit == "일별":
        df_time_channel = df_filtered.groupby(['date', 'channel'])['revenue'].sum().reset_index()
        x_col = 'date'
    elif time_unit == "주별":
        df_time_channel = df_filtered.groupby(['year_week', 'channel'])['revenue'].sum().reset_index()
        x_col = 'year_week'
    elif time_unit == "월별":
        df_time_channel = df_filtered.groupby(['year_month', 'channel'])['revenue'].sum().reset_index()
        x_col = 'year_month'
    else:  # 분기별
        df_time_channel = df_filtered.groupby(['year_quarter', 'channel'])['revenue'].sum().reset_index()
        x_col = 'year_quarter'
    
    fig_time_channel = px.line(
        df_time_channel,
        x=x_col,
        y='revenue',
        color='channel',
        title=f'채널별 {time_unit} 매출 추이',
        labels={x_col: x_title, 'revenue': '매출', 'channel': '채널'},
        template='plotly_white'
    )
    
    fig_time_channel.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(tickformat=",.0f")
    )
    
    st.plotly_chart(fig_time_channel, use_container_width=True)
    
    # 채널별 카테고리 분포
    channel_cat = df_filtered.groupby(['channel', 'category'])['revenue'].sum().reset_index()
    
    fig_channel_cat = px.bar(
        channel_cat,
        x='channel',
        y='revenue',
        color='category',
        title='채널별 카테고리 매출 분포',
        labels={'channel': '채널', 'revenue': '매출', 'category': '카테고리'},
        template='plotly_white',
        barmode='stack'
    )
    
    fig_channel_cat.update_layout(
        yaxis=dict(tickformat=",.0f")
    )
    
    st.plotly_chart(fig_channel_cat, use_container_width=True)

# 추가 분석: 할인 분석
st.header('할인 분석')

# 할인율에 따른 매출 분석
df_filtered['discount_bin'] = pd.cut(
    df_filtered['discount_rate'] * 100,
    bins=[0, 5, 10, 15, 20, 25, 30],
    labels=['0-5%', '5-10%', '10-15%', '15-20%', '20-25%', '25-30%'],
    include_lowest=True
)

discount_analysis = df_filtered.groupby('discount_bin').agg(
    revenue_sum = ('revenue', 'sum'),
    quantity = ('quantity', 'sum'),
    revenue_mean = ('revenue', 'mean')
).reset_index()

st.dataframe(discount_analysis, use_container_width=True)

discount_analysis.columns = ['할인율 구간', '총 매출', '총 판매량', '평균 주문 금액']

fig_discount = px.bar(
    discount_analysis,
    x='할인율 구간',
    y=['총 매출', '총 판매량', '평균 주문 금액'],
    title='할인율 구간별 매출 및 판매량',
    barmode='group',
    labels={'value': '값', 'variable': '지표'},
    template='plotly_white'
)

st.plotly_chart(fig_discount, use_container_width=True)

# 시간대별 할인율 추이
weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
df_filtered['weekday_name'] = df_filtered['dayofweek'].apply(lambda x: weekday_names[x])

weekday_discount = df_filtered.groupby('weekday_name').agg({
    'discount_rate': 'mean',
    'revenue': 'sum',
    'quantity': 'sum'
}).reset_index()

weekday_discount['discount_rate'] = weekday_discount['discount_rate'] * 100  # 퍼센트로 변환
# 요일 정렬을 위해 Categorical 지정
weekday_discount['weekday_name'] = pd.Categorical(
    weekday_discount['weekday_name'],
    categories=weekday_names,
    ordered=True
)

weekday_discount = weekday_discount.sort_values(by='weekday_name')


fig_weekday = px.line(
    weekday_discount,
    x='weekday_name',
    y=['discount_rate', 'revenue', 'quantity'],
    title='요일별 평균 할인율 및 매출/판매량',
    labels={'weekday_name': '요일', 'value': '값', 'variable': '지표'},
    template='plotly_white'
)

st.plotly_chart(fig_weekday, use_container_width=True)

# 상세 데이터 보기
st.header('상세 데이터')

show_data = st.checkbox('원본 데이터 보기')
if show_data:
    st.dataframe(
        df_filtered[['date', 'category', 'region', 'channel', 'price', 'discount_rate', 'quantity', 'revenue']],
        use_container_width=True
    )

# 상세 데이터 다운로드
st.download_button(
    label="데이터 CSV 다운로드",
    data=df_filtered[['date', 'category', 'region', 'channel', 'price', 'discount_rate', 'quantity', 'revenue']].to_csv(index=False).encode('utf-8'),
    file_name=f'sales_data_{start_date}_to_{end_date}.csv',
    mime='text/csv',
)

# 요약
st.header('데이터 요약')

# 요약 계산
top_category = cat_revenue.iloc[0]['category']
top_region = region_revenue.iloc[0]['region']
top_channel = channel_data.sort_values('revenue', ascending=False).iloc[0]['channel']

best_discount = discount_analysis.sort_values('총 매출', ascending=False).iloc[0]['할인율 구간']
best_weekday = weekday_discount.sort_values('revenue', ascending=False).iloc[0]['weekday_name']

summary_text = f"""
### 분석 요약:

- **총 매출**: {total_revenue:,.0f}원, **총 주문 수**: {total_orders:,}건
- **최고 매출 카테고리**: {top_category}
- **최고 매출 지역**: {top_region}
- **최고 매출 채널**: {top_channel}
- **최적 할인율 구간**: {best_discount}
- **최고 매출 요일**: {best_weekday}

선택한 기간 동안의 데이터를 기반으로 판매 전략을 수립하는 데 참고하세요.
"""

st.markdown(summary_text)

# 푸터
st.markdown("---")
st.caption("© 2025 Streamlit 데이터 분석 대시보드 | 샘플 데이터 기반")