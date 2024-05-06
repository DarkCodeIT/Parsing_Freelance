import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup

from const import categoryes


All_data = {"Data" : []}

async def links_to_page(link_coll: str, category: str) -> list:
    tasks_get_data = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url=link_coll) as response_on_pagination:

                    page_card = await response_on_pagination.text()
                    soup = BeautifulSoup(page_card, "lxml")
                    li = soup.find_all("li")

                    for li_tag in li:

                        a_tag = li_tag.find("a").get("href")
                        url = f"https://stihi.ru{a_tag}"
                        
                        tasks_get_data.append(asyncio.create_task(get_data(link=url, category=category)))
    return tasks_get_data


async def get_data(link: str, category: str):
    async with aiohttp.ClientSession() as session:
         async with session.get(url=link) as response:
            response = await response.text()
            soup = BeautifulSoup(response, "lxml")
            try:
                date = link.split(sep="/")
                date = f"{date[-2]}.{date[-3]}.{date[-4]}"
                check = int(date[-4])
                
                text = soup.find('div', class_="text").text

                author = soup.find('div', class_="titleauthor").find('a').text

                link_author = f"https://stihi.ru{soup.find('div', class_="titleauthor").find('a').get("href")}"

                name = soup.find('div', class_="maintext").find('h1').text

                async with session.get(url=link_author) as response:
                    soup = BeautifulSoup(await response.text(), 'lxml')
                    link_message = f"https://stihi.ru{soup.find('div', class_="maintext").find('div', id="textlink").find('a').get('href')}"

                data = {
                         "Name" : name,
                         "Author" : author,
                         "Link to author" : link_author,
                        #  "Link to message" : link_message,
                         "Text" : text
                    }
                All_data["Data"].append(data)
                
            except Exception as ex:
                 print(link)
                 print(ex)
                 await  asyncio.sleep(60)
                 return
                    

async def link_to_page_collection() -> list:
    links_to_collections = []
    async with aiohttp.ClientSession() as session:

        for link in categoryes.keys():
            category = link
            link = categoryes[link]

            async with session.get(url=link) as response:

                page_category = await response.text()
                soup = BeautifulSoup(page_category, "lxml")

                try:
                    pagination = soup.find("div", class_="textlink nounline").find_all("a")
                    for link_to_pages_collection in pagination:
                        links_to_collections.append(asyncio.create_task(links_to_page(f"https://stihi.ru/{link_to_pages_collection.get("href")}", category)))

                except Exception as ex:
                    print(ex)
        
    return links_to_collections


async def main():
    tasks = await link_to_page_collection()
    tasks_p = await asyncio.gather(*tasks)
    for i in tasks_p:
         await asyncio.gather(*i)



if __name__ == "__main__":
    asyncio.run(main())
    with open("data.json", 'w', encoding='utf-8') as file:
         json.dump(All_data, file, ensure_ascii=False)