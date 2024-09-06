import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re
from selenium.webdriver.chrome.options import Options

# Путь к драйверу
driver_path = "C:/chromedriver-win64/chromedriver.exe"
# Словарь с ссылками на товары
products = {
    "https://www.g2a.com/adobe-acrobat-pro-dc-2019-pc-1-device-lifetime-adobe-key-global-i10000502609001": {
        "price": 2.45,
        "name": "Adobe Acrobat Pro DC 2019"
    },
    "https://www.g2a.com/aida64-extreme-key-global-i10000049796001": {"price": 2.43, "name": "AIDA64 Extreme"},
}
my_nick = "Giftcardsellery"
telegram_token = "7396669176:AAHq4f-ncs0CoR0f2-t4lq8kP9OshL7ibzM"  #
chat_ids = ["333161917", "315745444"]

# Словарь для отслеживания
sent_notifications = {}

def is_price(text):
    return re.match(r'^[\d,\.]+$', text.replace('€', '').replace('$', '').strip())

def clean_seller_name(seller_text):
    lines = seller_text.split("\n")
    return lines[0].strip()

def send_telegram_message(message):
    for chat_id in chat_ids:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка при отправке сообщения в Telegram для chat_id {chat_id}: {e}")

def check_prices(product_url, product_name, my_price_regular):
    chrome_options = Options()
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(product_url)
    time.sleep(5)

    try:
        seller_blocks = driver.find_elements(By.CLASS_NAME, "gCRGIc")
        seller_names = driver.find_elements(By.CLASS_NAME, "bWpUG")

        if len(seller_blocks) != len(seller_names):
            print("Ошибка: количество блоков с предложениями не совпадает с количеством ников продавцов.")
            return

        print(f"Проверка цен для товара: {product_name}")

        my_price_found = None

        for block, seller in zip(seller_blocks, seller_names):
            prices_text = block.text.split("\n")
            seller_nick = clean_seller_name(seller.text)

            if seller_nick == my_nick:
                filtered_prices = [text for text in prices_text if is_price(text)]
                if len(filtered_prices) >= 2:
                    try:
                        my_price_found = float(filtered_prices[1].replace('€', '').replace('$', '').replace(',', '.').strip())
                        if my_price_found != my_price_regular:
                            print(f"Ваша новая цена для {product_name}: ${my_price_found}")
                            products[product_url]['price'] = my_price_found
                        continue
                    except (IndexError, ValueError) as e:
                        print(f"Ошибка при обработке цен: {e}")

            if seller_nick == my_nick:
                continue

            filtered_prices = [text for text in prices_text if is_price(text)]

            if len(filtered_prices) >= 2:
                try:
                    price_regular = float(filtered_prices[1].replace('€', '').replace('$', '').replace(',', '.').strip())

                    if price_regular < my_price_regular:
                        if product_url not in sent_notifications or sent_notifications[product_url] != price_regular:
                            message = (f"{seller_nick} изменил цену на ${price_regular} для {product_name}\n"
                                       f"Ваша цена: {my_price_regular}")
                            send_telegram_message(message)
                            sent_notifications[product_url] = price_regular
                    else:
                        if product_url in sent_notifications:
                            del sent_notifications[product_url]
                except (IndexError, ValueError) as e:
                    print(f"Ошибка при обработке цен: {e}")
            else:
                print(f"{seller_nick}: не удалось найти обе цены для продавца.")

    finally:
        driver.quit()

while True:
    for url, product_info in products.items():
        check_prices(url, product_info["name"], product_info["price"])
    print("Ожидание 5 минут перед следующей проверкой...\n")
    time.sleep(300)