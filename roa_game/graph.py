import asyncio
import random
import textwrap
from dataclasses import dataclass
import aiohttp
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import config


@dataclass
class RoundData:
    users: [tuple[str, int]]
    total_score: int
    word: str


class ImageScraper:
    def __init__(self, api_key=config.unsplash_api_key):
        self.api_key = api_key
        self.base_url = "https://api.unsplash.com/photos/random"

    async def fetch_random_image(self, keyword):
        search_url = f"{self.base_url}?query={keyword}"
        headers = {"Authorization": f"Client-ID {self.api_key}"}

        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            json_response = response.json()
            if 'urls' in json_response:
                return json_response['urls']['regular']
        return None


class Plotter:
    def __init__(self, image_scraper=ImageScraper()):
        self.image_scraper = image_scraper

    async def insert_image_to_graph(self, image_url, position, ax):
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_content = await response.read()
                    img = Image.open(BytesIO(image_content))
                    img.thumbnail((50, 50))
                    imagebox = OffsetImage(img)
                    ab = AnnotationBbox(imagebox, position, frameon=False)
                    ax.add_artist(ab)

    async def create_plot(self, round_data_list: list[RoundData]) -> BytesIO:
        labels = [textwrap.fill(data.word, width=15) for data in round_data_list]
        x = [data.total_score for data in round_data_list]
        colors = [plt.cm.jet(random.random()) for _ in range(len(labels))]
        plt.figure(figsize=(10, 6))
        bars = plt.barh(labels, x, color=colors, edgecolor='black')

        plt.title('РЕЙТИНГ ВСЕГО', pad=20)

        plt.grid(True, axis='x')
        plt.axvline(0, color='black', linewidth=0.5)

        for bar, data in zip(bars, round_data_list):
            image_url = await self.image_scraper.fetch_random_image(data.word)
            if image_url:
                await self.insert_image_to_graph(
                    image_url, (data.total_score, bar.get_y() + bar.get_height() / 2), plt.gca()
                )

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.savefig('test.png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        plt.close()

        return buf

# data1 = RoundData(users=[('User1', 10), ('User2', 15)], total_score=25, word='путин')
# data2 = RoundData(users=[('User1', 5), ('User2', 8)], total_score=13, word='водка')
# data3 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=0, word='Анекдоты в бане')
# data4 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=--20, word='Пить воду с голыми мужчинами')
# data5 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=-40, word='Тут было бы')
# data6 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=100, word='А тут стало')
# data7 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=-100, word='Тыры пыры')
# data8 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=--2, word='В попе')
# data9 = RoundData(users=[('User1', 12), ('User2', 18)], total_score=-3, word='Дыры')
# #
# plotter = Plotter()
# asyncio.run(plotter.create_plot([data1, data2, data3, data4, data5, data6, data7, data8, data9]))
