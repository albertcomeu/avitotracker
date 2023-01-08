from bs4 import BeautifulSoup
import asyncio
import re
from arsenic import get_session, browsers, services
import sys
import os

if sys.platform.startswith('win'):
    CHROMEDRIVER = 'avito_tracker/chrome_driver/chromedriver.exe'
else:
    CHROMEDRIVER = 'avito_tracker/chrome_driver/chromedriver'


async def parse_info(page: str) -> dict:
    avito_url = 'https://www.avito.ru'
    max_words = 40
    info = {
        'link': '',
        'name': '',
        'img': '',
        'price': '',
        'description': '',
    }
    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.find_all(
            "div", {'class': re.compile(r'^iva-item-content')}):
        try:
            result = link.find(
                'div', {'class': re.compile(r'^iva-item-text')}).text
            if len(result.split(' ')) > max_words:
                new = ' '.join(result.split(' ')[:max_words])
                info['description'] = f"{new}..."
            else:
                info['description'] = result
        except Exception:
            info['description'] = 'Не удалось поучить описание'
        try:
            info['price'] = link.find(
                'meta', {'itemprop': 'price'})['content']
        except Exception:
            info['price'] = 'Не удалось получить цену'
        try:
            result = link.find(
                'a', {'itemprop': 'url'})['href']
            info['link'] = f"{avito_url}{result}"
        except Exception:
            info['link'] = 'Не удалось получить ссылку'
        try:
            info['name'] = link.find(
                'h3', {'itemprop': 'name'}).text
        except Exception:
            info['name'] = 'Не удалось получить имя'
        try:
            info['img'] = link.findNext('img')['src']
        except Exception:
            info['img'] = 'Не удалось получить картинку'
        break
    return info


async def async_avito(url: str) -> dict:
    service = services.Chromedriver(binary=CHROMEDRIVER, log_file=os.devnull)
    browser = browsers.Chrome()
    browser.capabilities = {
        "goog:chromeOptions": {
            "args":
                [
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-in-process-stack-traces",
                    "--remote-debugging-port=9222"
                ]
        }
    }
    async with get_session(service, browser) as driver:
        await driver.get(url)
        await asyncio.sleep(3)
        html = await driver.get_page_source()
        new_data = await parse_info(html)
        return new_data
