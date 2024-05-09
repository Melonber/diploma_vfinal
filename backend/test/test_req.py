import asyncio
import time

import httpx
import random
import string

async def send_request(client, url):
    # Случайное значение phone
    phone = ''.join(random.choices(string.digits, k=10))  # 10-значный номер телефона

    # Случайное значение message
    message = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    data = {
        'phone': phone,
        'message': message,
    }

    response = await client.post(url, json=data)
    return response.status_code

async def main():
    while True:
        time.sleep(1)
        url = 'http://localhost:8000/log'
        num_requests = random.randint(1, 1000)  # Случайное количество запросов от 1 до 20

        async with httpx.AsyncClient() as client:
            tasks = []
            for _ in range(num_requests):
                # Создаем задачи для отправки запросов
                tasks.append(send_request(client, url))

            # Ждем выполнения всех задач за 5 секунд
            try:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)
                print('SUCEESS')
            except asyncio.TimeoutError:
                print("Время ожидания истекло!")

# Запускаем главную функцию
asyncio.run(main())
