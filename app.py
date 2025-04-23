import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm

st.set_page_config(layout="wide")
st.title("💼 売上ダッシュボード")

# --- データ生成 ---
@st.cache_data
def load_data():
    np.random.seed(42)
    today = pd.to_datetime("today").normalize()
    dates = pd.date_range(end=today, periods=90)  # 過去90日
    shops = ['東京店', '大阪店', '福岡店']
    categories = ['食品', '家電', '日用品']
    data = []
    for _ in range(500):
        data.append({
            '日付': np.random.choice(dates),
            '店舗': np.random.choice(shops),
            'カテゴリ': np.random.choice(categories),
            '商品名': f"商品{np.random.randint(1, 50)}",
            '売上金額': np.random.randint(1000, 30000)
        })
    return pd.DataFrame(data)

df = load_data()

# --- 💡 UIフィルター（横並び） ---
st.markdown("### 🔍 フィルター条件（直近30日間）")
col1, col2, col3 = st.columns(3)

max_date = df['日付'].max()
min_date = max_date - pd.Timedelta(days=30)
df = df[(df['日付'] >= min_date) & (df['日付'] <= max_date)]

with col1:
    shop_filter = st.multiselect("店舗", df['店舗'].unique(), default=df['店舗'].unique())
with col2:
    category_filter = st.multiselect("カテゴリ", df['カテゴリ'].unique(), default=df['カテゴリ'].unique())
with col3:
    sort_order = st.radio("店舗売上ランキング", ["降順", "昇順"], horizontal=True)

# --- フィルター適用 ---
filtered = df[
    (df['店舗'].isin(shop_filter)) &
    (df['カテゴリ'].isin(category_filter))
]

# --- 💡 KPIカード表示 ---
st.markdown("### 📌 指標サマリ")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="合計売上", value=f"{filtered['売上金額'].sum():,} 円")
with kpi2:
    st.metric(label="平均売上", value=f"{filtered['売上金額'].mean():,.0f} 円")
with kpi3:
    st.metric(label="取引数", value=len(filtered))

# --- 📊 月別売上推移（棒グラフ） ---
# 文字化け対策
plt.rcParams['font.family'] = 'MS Gothic'
# グラフタイトル
st.markdown("### 📈 月別×店舗別売上（集合縦棒）")

# 月単位の列を追加
filtered['月'] = filtered['日付'].dt.to_period('M').astype(str)

# ピボット形式にして月×店舗の売上合計を表にする
pivot = filtered.pivot_table(
    index='月',
    columns='店舗',
    values='売上金額',
    aggfunc='sum',
    fill_value=0
)

# グラフ描画
fig, ax = plt.subplots(figsize=(6, 2.5))

bar_width = 0.2
months = pivot.index
x = np.arange(len(months))  # X軸の位置基準

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # 任意の店舗カラー

for i, shop in enumerate(pivot.columns):
    ax.bar(x + i * bar_width, pivot[shop], width=bar_width, label=shop, color=colors[i % len(colors)])

# 軸調整
ax.set_xlabel("月", fontsize=12)
ax.set_ylabel("売上金額（円）", fontsize=12)
ax.set_title("月別×店舗別売上", fontsize=14)
ax.set_xticks(x + bar_width * (len(pivot.columns)-1) / 2)
ax.set_xticklabels(months, rotation=45)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"¥{int(x):,}"))

ax.legend(title="店舗", loc='upper left')
ax.grid(axis='y', linestyle='--', alpha=0.5)

st.pyplot(fig)

# --- 🏪 店舗別ランキング（テーブル） ---
st.markdown("### 🏪 店舗別売上ランキング")
rank = filtered.groupby('店舗')['売上金額'].sum()
rank = rank.sort_values(ascending=(sort_order == "昇順"))
st.table(rank)

# --- 📋 データ詳細（折りたたみ） ---
with st.expander("📋 データ一覧を見る"):
    st.dataframe(filtered, use_container_width=True)
