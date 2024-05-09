import requests
import time

# URL для отправки POST-запроса
url = "http://localhost:8000/log"

# Данные для отправки в запросе
data = {
    'phone': '1234567890',  # Укажите нужный номер телефона
    'message': 'Test request'  # Укажите нужное сообщение
}

# Отправляем POST-запрос и измеряем время, затраченное на запрос
start_time = time.time()  # Начало времени запроса
response = requests.post(url, json=data)  # Отправка запроса с данными в формате JSON
end_time = time.time()  # Конец времени запроса

# Вычисляем время ответа
response_time = end_time - start_time

# Выводим ответ и время ответа
print(f"Ответ сервера: {response.text}")
print(f"Время ответа: {response_time:.2f} секунд")
