import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

def get_youtube_comments(video_ids):
    # Инициализация клиента YouTube API
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    all_comments = []

    for video_id in video_ids:
        try:
            # Обращение к API для получения комментариев
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100, # API позволяет до 100 за один запрос
                textFormat="plainText"
            )
            response = request.execute() # Ответ приходит в формате JSON

            # Парсинг JSON-ответа
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                all_comments.append({
                    'source': 'YouTube',
                    'author': comment['authorDisplayName'],
                    'text': comment['textOriginal'],
                    'date': comment['publishedAt']
                })
        except Exception as e:
            print(f"Ошибка при сборе с видео {video_id}: {e}")

    # Сохранение в сырые данные
    df = pd.DataFrame(all_comments)
    # drop_duplicates() на случай, если одно и то же видео передали дважды
    df = df.drop_duplicates(subset=['text', 'author']) 
    
    # Дозапись в файл или создание нового
    output_path = 'data/raw/youtube_raw.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Успешно собрано {len(df)} комментариев с YouTube.")

if __name__ == "__main__":
    # Вам нужно будет найти на YouTube 3-5 видео про Freedom Bank 
    # и скопировать их ID (то, что идет после v= в ссылке)
    # Пример: https://www.youtube.com/watch?v=dQw4w9WgXcQ -> ID = dQw4w9WgXcQ
    
    freedom_videos = [
        '4FtamLt6opY', # Замените на реальные ID
        '4GvUjphkZl4',
        'x7Qaa1IBKZ8'
    ]
    
    get_youtube_comments(freedom_videos)