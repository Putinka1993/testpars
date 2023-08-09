
import requests
from bs4 import BeautifulSoup
import json
import csv
from time import sleep
from random import randint

# создаем ссылку url = адрес сайта
# url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"


# передаем заголовки для того что бы сайт не думал что мы бот
# добавляется как минимум файл Acept и User-agent во вкладке разработчика network
# или использовать библиотеку для генерации случайных агентов

headers = {
    "Acept": "*/*",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# возвращает нам метод get библиотеки requests
# req = requests.get(url, headers=headers)

# сохраняем полученный обьект (можно вызвать через print)
# для того что бы убедиться что мы выводим код страницы
# src = req.text

# сохраняем полученную страницу в отдельный файл html ("w" запись) 
# with open("index.html", "w") as file:
#     file.write(src)

# открыть файл и сохранить в переменной 
with open("index.html") as file:
    src = file.read()

# создадим обьект библиотеки (супа) BS4, передадим в качестве параметров
# переменную, и параметр lxml (для самого парсинга)
# soup = BeautifulSoup(src, "lxml")

# # создаем переменную с параметрами поиска искогомого значения 
# all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href") # поиск по тегу и классу

# all_categories_dict = {}

# # функция которая проходиться по всему найденному массиву 
# for item in all_products_hrefs:
#     item_text = item.text # отоброжает только текст
#     item_href = "https://health-diet.ru" + item.get("href") # в данном случае "href" отображает ссылки
    
#     # создание словаря для храненния данных парсинга
#     all_categories_dict[item_text] = item_href
# print(all_categories_dict)
# # сохранение в отдельный файл json для хранения данных
# with open("all_categories_dict.json", "w") as file: # "w" write - запись , записать файл
#     json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)  # indent - отступ в файле, ensure_ascii - убирает проблемы с кириллицей

with open("all_categories_dict.json") as file:   # open file
    all_categories = json.load(file) # метод load считывыает файл

# print(all_categories)

iteration_count = int(len(all_categories)) - 1
print(f"Всего итераций: {iteration_count}")
count = 0


for category_name, category_href in all_categories.items():

    rep = [",", " ", "-"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_") # изменяем имена
    print(category_name)
    
    req = requests.get(url=category_href, headers=headers)
    src = req.text
    
    with open(f"data/{count}_{category_name}.html", "w") as file: # добавляем в папку date странички html
        file.write(src)
    
    with open(f"data/{count}_{category_name}.html") as file: 
        src = file.read()
    
    soup = BeautifulSoup(src, "lxml") 
    
    # проверка страницы на наличе таблицы с продуктами
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue
    
    # забираем заголови таблицы
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    
    
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text
    
    
    # запись данных в таблицу в файле csv , для этого используем встроенную библиотеку import csv
    with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(    # метод writerow записывает в одну строку и принимает один аргумент
            (               # для того что бы записать несколько аргументов, используем кортеж () либо список [] 
                product,
                calories,
                proteins,
                fats,
                carbohydrates
            )
        )
        
        # собираем данные продуктов
        product_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")
        
        product_info = []
        
        # собираем теги из массива
        for item in product_data:
            product_tds = item.find_all("td")

            title = product_tds[0].find("a").text
            
            calories = product_tds[1].text
            proteins = product_tds[2].text
            fats = product_tds[3].text
            carbohydrates = product_tds[4].text
            
            product_info.append(
                {
                    "Title": title,
                    "Calories": calories,
                    "Proteins": proteins,
                    "Fats": fats,
                    "Carbohydrates": carbohydrates
                }
            )
            
            with open(f"data/{count}_{category_name}.csv", "a", encoding="utf-8") as file: # "a" означает append (дозаписывать в файл)
                writer = csv.writer(file)
                writer.writerow(    # метод writerow записывает в одну строку и принимает один аргумент
                (               # для того что бы записать несколько аргументов, используем кортеж () либо список [] 
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )
        with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:    
            json.dump(product_info, file, indent=4, ensure_ascii=False)
            
        count += 1
        print(f"# Итерация {count}. {iteration_count} записан...")
        iteration_count = iteration_count - 1
        
        if iteration_count == 0:
            print("Работа завершена")
            break
            
        print(f"Осталось итераций: {iteration_count}")
        sleep(randint(2, 4))