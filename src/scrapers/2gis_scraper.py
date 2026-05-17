import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def scrape_2gis_reviews():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Поставьте True, когда отладим
        context = await browser.new_context()
        page = await context.new_page()

        url = "https://2gis.kz/almaty/firm/70000001048737689/tab/reviews"
        await page.goto(url)
        
        # ВАЖНО: Ждем, пока загрузится хотя бы один блок с отзывами
        # (Обычно в 2ГИС отзывы лежат внутри div, поэтому ждем его)
        await page.wait_for_timeout(5000) # Дадим 5 секунд на полную загрузку страницы

        reviews_data = []

        for i in range(10): 
            # В 2ГИС отзывы часто находятся просто в блоках (div). 
            # Найдем все элементы, которые выглядят как карточка отзыва
            # ЗАМЕНИТЕ '_11gcv' и '_123abc' на те классы, которые вы нашли через F12!
            
            # Если тег <article> не работает, можно использовать более широкий поиск
            reviews = await page.locator('div').all() # Ищем внутри div-ов, если article нет
            
            for review in reviews:
                try:
                    # Вставьте СЮДА класс текста отзыва (начинается с точки)
                    text_element = review.locator('._co8kyiw') 
                    # Вставьте СЮДА класс имени автора
                    author_element = review.locator('._19h0cqe')
                    
                    # Проверяем, есть ли текст в этом блоке
                    if await text_element.count() > 0 and await author_element.count() > 0:
                        text = await text_element.first.inner_text() 
                        author = await author_element.first.inner_text()
                        
                        reviews_data.append({
                            'source': '2GIS',
                            'author': author,
                            'text': text
                        })
                except Exception as e:
                    continue

            # Скролл вниз по странице
            await page.mouse.wheel(0, 5000)
            await page.wait_for_timeout(2500)

        # Сохраняем (и сразу добавляем правильную кодировку для Excel!)
        df = pd.DataFrame(reviews_data).drop_duplicates()
        df.to_csv('data/raw/2gis_raw.csv', index=False, encoding='utf-8-sig')
        print(f"Собрано {len(df)} уникальных отзывов")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_2gis_reviews())