# Freedom Bank Web Mining & Analytics

Проект по сбору и анализу упоминаний бренда Freedom Bank в сети (2GIS, YouTube, Instagram, Threads).

## Архитектура
- **Data Acquisition**: Playwright (UI scraping) + Google API Client (JSON).
- **Preprocessing**: Custom Regex Pipeline + Lemmatization (pymorphy2).
- **Core Logic**: TF-IDF, NetworkX (PageRank).
- **Dashboard**: Streamlit (Real-time simulation & Anomaly detection).

## Запуск
1. Клонировать репозиторий.
2. `pip install -r requirements.txt` и `playwright install`.
3. Добавить `.env` файл с `YOUTUBE_API_KEY`.
4. Запуск дашборда: `streamlit run app.py`.