import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import pandas as pd

def scrape_news():
    # Ищем Freedom Bank по региону Казахстан (KZ) на русском языке (ru)
    query = urllib.parse.quote("Freedom Bank Казахстан")
    url = f"https://news.google.com/rss/search?q={query}&hl=ru&gl=KZ&ceid=KZ:ru"
    
    print("Обращаемся к агрегатору новостей...")
    
    try:
        # Притворяемся обычным браузером
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        # Парсим XML-структуру
        root = ET.fromstring(xml_data)
        
        news_data = []
        
        # Проходим по всем новостям в ленте
        for item in root.findall('.//channel/item'):
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            # Вытаскиваем название портала (Tengrinews, Kursiv и т.д.)
            source_element = item.find('source')
            source = source_element.text if source_element is not None else 'Local News'
            
            news_data.append({
                'source': f'News: {source}',
                'author': 'Journalist',
                'text': title, # В новостях заголовок несет основную смысловую нагрузку
                'date': pub_date
            })
            
        df = pd.DataFrame(news_data).drop_duplicates(subset=['text'])
        df.to_csv('data/raw/news_raw.csv', index=False, encoding='utf-8-sig')
        print(f"Успешно собрано {len(df)} свежих новостей с разных порталов РК!")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    scrape_news()