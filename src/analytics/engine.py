import logging
import json
import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AnalyticsEngine')

nltk.download('stopwords', quiet=True)

def get_stop_words():
    """Формирует итоговый список стоп-слов для фильтрации."""
    ru_stops = stopwords.words('russian')
    
    custom_stops = [
        'это', 'как', 'так', 'что', 'для', 'по', 'на', 'из', 'от',
        'банк', 'банка', 'freedom', 'фридом', 'finance', 'финанс', 
        'очень', 'просто', 'вообще', 'весь', 'свой', 'который', 'kz'
    ]
    return ru_stops + custom_stops

def build_co_occurrence_graph(documents, feature_names):
    """Строит граф связей слов на основе их совместной встречаемости."""
    G = nx.Graph()
    G.add_nodes_from(feature_names)
    
    for doc in documents:
        words_in_doc = list(set(doc.split()) & set(feature_names))
        
        for i in range(len(words_in_doc)):
            for j in range(i + 1, len(words_in_doc)):
                w1, w2 = words_in_doc[i], words_in_doc[j]
                if G.has_edge(w1, w2):
                    G[w1][w2]['weight'] += 1
                else:
                    G.add_edge(w1, w2, weight=1)

    edges_to_remove = [(u, v) for u, v, data in G.edges(data=True) if data['weight'] < 2]
    G.remove_edges_from(edges_to_remove)
    G.remove_nodes_from(list(nx.isolates(G)))
    
    return G

def run_analytics():
    """Основной пайплайн аналитики текста."""
    logger.info("Загрузка обработанных данных...")
    
    try:
        df = pd.read_csv('data/processed/final_cleaned_data.csv')
        df = df.dropna(subset=['lemmatized_text'])
        documents = df['lemmatized_text'].astype(str).tolist()
    except FileNotFoundError:
        logger.error("Файл данных не найден. Сначала запустите cleaner.py.")
        return

    if not documents:
        logger.warning("Датасет пуст после очистки.")
        return

    logger.info("Запуск TF-IDF векторизации...")
    vectorizer = TfidfVectorizer(
        max_df=0.85, 
        min_df=2, 
        max_features=40, 
        stop_words=get_stop_words()
    )
    
    try:
        vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
    except Exception as e:
        logger.error(f"Ошибка при вычислении TF-IDF: {e}")
        return
    
    pd.DataFrame({'keyword': feature_names}).to_csv(
        'data/processed/tfidf_keywords.csv', 
        index=False, 
        encoding='utf-8-sig'
    )

    logger.info("Генерация графа связей")
    graph = build_co_occurrence_graph(documents, feature_names)
    
    with open('data/processed/network_graph.json', 'w', encoding='utf-8') as f:
        json.dump(nx.node_link_data(graph), f, ensure_ascii=False, indent=2)
        
    logger.info(f"Извлечено {len(feature_names)} ключевых слов")

if __name__ == "__main__":
    run_analytics()