import pandas as pd
import glob
import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Cleaner')

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^а-яа-ёa-z0-9\s.,!?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def run_preprocessing():
    raw_folder = 'data/raw'
    processed_folder = 'data/processed'
    os.makedirs(processed_folder, exist_ok=True)
    
    csv_files = glob.glob(os.path.join(raw_folder, '*.csv'))
    
    if not csv_files:
        logger.error("не найдено ни одного CSV файла!")
        return
        
    logger.info(f"Найдено файлов для объединения: {len(csv_files)}")
    
    all_data = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            logger.info(f"Чтение файла {os.path.basename(file)}: {len(df)} строк.")
            
            required_cols = ['source', 'text']
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"⚠️ Файл {file} пропущен: нет колонок 'source' или 'text'")
                continue
                
            if 'date' not in df.columns:
                df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                
         
            df['lemmatized_text'] = df['text']
                
            df_standard = df[['source', 'date', 'text', 'lemmatized_text']].copy()
            all_data.append(df_standard)

        except Exception as e:
            logger.error(f"Ошибка при обработке файла {file}: {e}")
            
    if not all_data:
        logger.error("Нет данных для объединения.")
        return
        
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"Объединено всего строк: {len(combined_df)}")
    
    logger.info("Запуск очистки текстов...")
    combined_df['text'] = combined_df['text'].apply(clean_text)
    
    combined_df = combined_df[combined_df['text'].str.strip() != ""]
    
    combined_df.drop_duplicates(subset=['text'], inplace=True)
    logger.info(f"После удаления дубликатов осталось: {len(combined_df)} строк.")
    
    output_path = os.path.join(processed_folder, 'final_cleaned_data.csv')
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"Результат сохранен в {output_path}")

if __name__ == "__main__":
    run_preprocessing()