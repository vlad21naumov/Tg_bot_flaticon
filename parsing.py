from requests_html import HTMLSession
import random

s = HTMLSession()
page = random.randint(1, 10)

def get_icons(category) -> list:
    icons = []
    url = f'https://www.flaticon.com/search/{page}?word={category}'
    r = s.get(url)
    content = r.html.find('div.icon--holder')
    for icon in content:
        icon_url = icon.find('img', first=True).attrs['data-src']
        icons.append(icon_url)
    return icons


