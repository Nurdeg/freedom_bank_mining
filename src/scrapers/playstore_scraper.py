import pandas as pd
import logging
import os
from google_play_scraper import Sort, reviews

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PlayStoreScraper')

def run_playstore_scraper():
    app_id = 'ffinbank.MyFreedom' 
    target_count = 2500
    
    logger.info(f"сбор отзывов из Google Play для '{app_id}'...")
    
    try:
        result, _ = reviews(
            app_id,
            lang='ru',       
            country='kz',    
            sort=Sort.NEWEST,
            count=target_count
        )
        
        if not result:
            logger.warning("Проверьте подключение к сети.")
            return
            
        logger.info(f"получено {len(result)} сырых отзывов.")
        
        df = pd.DataFrame(result)
        
        if 'at' in df.columns:
            date_col = df['at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_col = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

        clean_df = pd.DataFrame({
            'source': 'Google Play',
            'date': date_col,
            'text': df['content'] if 'content' in df.columns else df['text'],
            'rating': df['score'] if 'score' in df.columns else 0
        })
        
        os.makedirs('data/raw', exist_ok=True)
        output_path = 'data/raw/playstore_reviews.csv'
        clean_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        logger.info(f"Данные сохранены в {output_path} (Строк: {len(clean_df)})")
        
    except Exception as e:
        logger.error(f"Ошибка при сборе данных: {e}")

if __name__ == "__main__":
    run_playstore_scraper()