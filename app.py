import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import json
import time

# ==========================================
# ⚙️ НАСТРОЙКИ СТРАНИЦЫ
# ==========================================
st.set_page_config(page_title="Freedom Bank: Live Analytics", layout="wide")

st.title("🔴 Система мониторинга инфополя [LIVE]")
st.markdown("Потоковый анализ данных, детекция аномалий и интерактивный поиск.")
st.divider()

@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/final_cleaned_data.csv')
    keywords = pd.read_csv('data/processed/tfidf_keywords.csv')
    with open('data/processed/network_graph.json', 'r', encoding='utf-8') as f:
        graph_data = json.load(f)
    return df, keywords, graph_data

df, keywords, graph_data = load_data()

if 'sentiment' not in df.columns:
    st.error("Колонка 'sentiment' не найдена! Запустите sentiment_scorer.py.")
    st.stop()

# ==========================================
# 🕹️ РЕЖИМ РАБОТЫ И СИМУЛЯЦИЯ
# ==========================================
st.sidebar.header("🕹️ Управление режимом")

# Чекбокс переключения режимов
run_simulation = st.sidebar.checkbox("Включить симуляцию потока (Real-time)", value=False)

if 'stream_index' not in st.session_state:
    st.session_state.stream_index = min(5, len(df))
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False

# Если симуляция активна, работаем с увеличивающимся срезом данных
if run_simulation:
    if st.sidebar.button("▶️ Старт / ⏸ Пауза потока"):
        st.session_state.is_streaming = not st.session_state.is_streaming
    
    st.sidebar.write(f"**Статус потока:** {'🟢 LIVE' if st.session_state.is_streaming else '⏸ ПАУЗА'}")
    st.sidebar.progress(min(st.session_state.stream_index / len(df), 1.0))
    
    working_df = df.iloc[:st.session_state.stream_index].copy()
else:
    # Если симуляция выключена — сразу отдаем в работу ВСЕ данные без ограничений
    st.session_state.is_streaming = False
    working_df = df.copy()

# ==========================================
# 🎛 ИНТЕРАКТИВНЫЕ ФИЛЬТРЫ
# ==========================================
st.sidebar.divider()
st.sidebar.header("Интерактивные фильтры")

sources = ["Все"] + list(df['source'].unique())
selected_source = st.sidebar.selectbox("Источник данных:", sources)
search_query = st.sidebar.text_input("🔍 Поиск по тексту:")

# ==========================================
# 🧠 ЛОГИКА ДЕТЕКЦИИ АНОМАЛИЙ
# ==========================================
global_neg_ratio = len(df[df['sentiment'] == 'Негативный']) / len(df) if len(df) > 0 else 0
window_size = min(10, len(working_df))
recent_window = working_df.tail(window_size)
recent_neg_count = len(recent_window[recent_window['sentiment'] == 'Негативный'])
threshold = max(window_size * global_neg_ratio * 1.3, 2)

if run_simulation and window_size >= 5 and recent_neg_count >= threshold:
    st.error(f"🚨 **АНОМАЛИЯ ОБНАРУЖЕНА!** Резкий всплеск негатива: {recent_neg_count} негативных публикаций в текущем окне.")

# ==========================================
# ✂️ ПРИМЕНЕНИЕ ФИЛЬТРОВ К ДАННЫМ
# ==========================================
filtered_df = working_df.copy()

if selected_source != "Все":
    filtered_df = filtered_df[filtered_df['source'] == selected_source]

if search_query:
    filtered_df = filtered_df[filtered_df['text'].str.contains(search_query, case=False, na=False)]

st.sidebar.divider()
st.sidebar.write("📊 **Статистика дашборда:**")
st.sidebar.write(f"Доступно в выборке: **{len(working_df)} / {len(df)}**")
st.sidebar.write(f"Отображается после фильтров: **{len(filtered_df)}**")

# ==========================================
# 📊 ИНТЕРФЕЙС И ВКЛАДКИ
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 Обзор и Тональность", "🕸️ Граф связей", "🔑 Ключевые слова (TF-IDF)"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Тональность")
        if not filtered_df.empty:
            color_map = {'Позитивный': '#00CC96', 'Негативный': '#EF553B', 'Нейтральный': '#636EFA'}
            
            # Изменение: Передаем filtered_df напрямую и указываем только names='sentiment'.
            # Plotly Express сам посчитает точное количество строк для каждой категории.
            fig = px.pie(
                filtered_df, 
                names='sentiment', 
                hole=0.4,
                color='sentiment', 
                color_discrete_map=color_map
            )
            fig.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных для построения графика.")

    with col2:
        st.subheader("Поток сообщений")
        cols_to_show = ['date', 'source', 'sentiment', 'text'] if 'date' in filtered_df.columns else ['source', 'sentiment', 'text']
        st.dataframe(filtered_df[cols_to_show].iloc[::-1], use_container_width=True, height=400)

with tab2:
    st.subheader("Граф семантических связей (Глобальный)")
    G = nx.node_link_graph(graph_data)
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, k=0.7, seed=42) 
    nx.draw_networkx_nodes(G, pos, node_size=600, node_color='#4A90E2', alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=1.0, edge_color='lightgray', alpha=0.6, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    plt.axis('off')
    st.pyplot(fig)

with tab3:
    st.subheader("Топ ключевых слов (TF-IDF)")
    st.dataframe(keywords, use_container_width=False)

# ==========================================
# ⏱ ЦИКЛ СИМУЛЯЦИИ ПОТОКА
# ==========================================
if run_simulation and st.session_state.is_streaming and st.session_state.stream_index < len(df):
    time.sleep(3) 
    st.session_state.stream_index = min(st.session_state.stream_index + 2, len(df))
    st.rerun()
elif run_simulation and st.session_state.stream_index >= len(df) and st.session_state.is_streaming:
    st.session_state.is_streaming = False
    st.toast("✅ Симуляция завершена. Все данные обработаны.")