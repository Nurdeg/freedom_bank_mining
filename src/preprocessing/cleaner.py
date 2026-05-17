import pandas as pd
import re
import os
import pymorphy3
from glob import glob

morph = pymorphy3.MorphAnalyzer()

def custom_regex_cleaner(text):
    if not isinstance(text, str): return ""
    
    # 1. Ссылки
    text = re.sub(r'https?://\S+|www\.\S+', ' [URL] ', text)
    # 2. HTML сущности (&nbsp; и т.д.)
    text = re.sub(r'&[a-z0-9]+;', ' ', text)
    # 3. Хештеги и упоминания
    text = re.sub(r'[@#]\w+', ' ', text)
    # 4. Эмодзи и спецсимволы (оставляем только буквы, цифры и базовую пунктуацию)
    text = re.sub(r'[^а-яА-ЯёЁәіңғүұқөһa-zA-Z0-9\s.!?]', ' ', text)
    # 5. Дубли знаков препинания
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    # 6. Лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text.lower()

def lemmatize(text):
    # Разрезаем на слова, приводим к начальной форме (для RU)
    words = text.split()
    res = []
    for w in words:
        # Для казахских слов pymorphy не сработает, оставим их как есть
        # (в идеале тут нужен казахский стоп-словарь)
        p = morph.parse(w)[0]
        res.append(p.normal_form)
    return " ".join(res)

def process_all_data():
    # Собираем все файлы из raw
    raw_files = glob('data/raw/*.csv')
    all_dfs = []

    for file in raw_files:
        temp_df = pd.read_csv(file)
        all_dfs.append(temp_df)

    main_df = pd.concat(all_dfs, ignore_index=True)
    
    # Применяем очистку
    print("Начинаю очистку текста...")
    main_df['clean_text'] = main_df['text'].apply(custom_regex_cleaner)
    
    # Применяем лемматизацию
    print("Применяю лемматизацию...")
    main_df['lemmatized_text'] = main_df['clean_text'].apply(lemmatize)

    # Создаем сравнительную таблицу для отчета (10 примеров)
    report_sample = main_df[['text', 'lemmatized_text']].head(10)
    report_sample.to_csv('data/processed/comparison_table.csv', index=False, encoding='utf-8-sig')

    # Сохраняем финальный датасет
    main_df.to_csv('data/processed/final_cleaned_data.csv', index=False, encoding='utf-8-sig')
    print(f"Всего обработано записей: {len(main_df)}")

if __name__ == "__main__":
    process_all_data()