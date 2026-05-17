import pandas as pd
import logging
from transformers import pipeline

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SentimentScorer')

def run_sentiment_analysis():
    logger.info("Загрузка данных...")
    try:
        df = pd.read_csv('data/processed/final_cleaned_data.csv')
    except FileNotFoundError:
        logger.error("Файл данных не найден. Сначала запустите cleaner.py.")
        return

    # Загружаем легковесную модель для русского языка
    # При первом запуске она скачает веса (~700 МБ)
    logger.info("Инициализация NLP-модели (ruBERT)...")
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="blanchefort/rubert-base-cased-sentiment"
        )
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        return

    def get_sentiment(text):
        if not isinstance(text, str) or len(text.strip()) < 5:
            return "Нейтральный"
        try:
            # Нейросети имеют лимит на длину текста (обычно 512 токенов), поэтому обрезаем длинные статьи
            result = sentiment_pipeline(text[:1500])[0]
            label = result['label']
            
            # Переводим технические метки в бизнес-формат
            if label == 'POSITIVE': return 'Позитивный'
            elif label == 'NEGATIVE': return 'Негативный'
            else: return 'Нейтральный'
        except Exception:
            return "Нейтральный"

    logger.info("Запуск скоринга текстов. Это может занять несколько минут...")
    df['sentiment'] = df['text'].apply(get_sentiment)

    df.to_csv('data/processed/final_cleaned_data.csv', index=False, encoding='utf-8-sig')
    logger.info("Анализ тональности успешно завершен! Данные сохранены.")

if __name__ == "__main__":
    run_sentiment_analysis()