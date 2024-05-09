from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime, timedelta
import os
import psutil
from fastapi.responses import JSONResponse

# Создание экземпляра FastAPI-приложения
app = FastAPI()

# Добавление CORS Middleware для разрешения кросс-доменных запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Активные WebSocket-соединения
active_connections = []
request_counts = []
time_window = 5  # Время окна в секундах для подсчета запросов
request_general = 0
anomalies = []

# Функция для генерации уникальных имен файлов на основе текущей даты и времени
def generate_log_filename():
    current_time = datetime.now()
    date_time_str = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"logs/log_{date_time_str}.txt"
    return filename


# Запись логов
@app.post("/log")
async def log_request(request: Request):

    data = await request.json()
    phone = data.get('phone')
    message = data.get('message')
    ip_address = request.client.host
    method = request.method
    path = request.url.path

    # Текущее время
    current_time = datetime.now()

    # Формирование лог-записи
    log_entry = f"INFO - IP: {ip_address}, Date: {current_time.strftime('%Y-%m-%d %H:%M:%S')}, Method: {method}, Path: {path}, Phone: {phone}, Message: {message}, Status: 200"

    # Сгенерировать уникальное имя файла
    log_filename = generate_log_filename()

    # Запись лог-записи в новый файл
    with open(log_filename, 'a') as file:
        file.write(log_entry + '\n')
        global request_general
        request_general+=1
        print(request_general)
    # Отправка лог-записи всем активным WebSocket-клиентам
    await broadcast_log_entry(log_entry)

    # Добавляем текущее время в список request_counts для подсчета количества запросов
    request_counts.append(current_time)

    # Возвращение ответа клиенту
    return {"message": "Спасибо за обращение ! Специалисты скоро свяжутся с вами"}


# Отправка логов всем активным WebSocket-клиентам
async def broadcast_log_entry(log_entry: str):
    for connection in active_connections:
        await connection.send_text(log_entry)


# Работа с WebSocket
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# Маршрут для получения логов
@app.get("/get_logs")
async def get_logs():
    try:
        # Найдите последний лог-файл (по имени)
        latest_log_file = \
        sorted([os.path.join("logs", file) for file in os.listdir("logs")], key=os.path.getmtime, reverse=True)[0]
        with open(latest_log_file, 'r') as file:
            logs = file.readlines()
        return {"logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл логов не найден.")


# Маршрут для получения количества запросов
@app.get("/get_request_count")
async def get_request_count():
    current_time = datetime.now()
    # Удаление старых запросов из списка request_counts
    request_counts[:] = [time for time in request_counts if current_time - time <= timedelta(seconds=time_window)]

    # Подсчет количества запросов и получение текущего времени
    count = len(request_counts)
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_for_file = current_time.strftime('%H%M%S')
    filename = f'./logs_req_per_sec/logs.txt'

    with open(filename, 'a') as file:
        # Форматирование временной метки для данных
        timestamp_for_data = current_time.strftime('%Y-%m-%d %H:%M:%S')
        # Запись данных в файл
        file.write(f'{count}, {timestamp_for_data}\n')

    return {"count": count, "timestamp": timestamp}

#получить количество запросов в сумме
@app.get("/get_request_count_general")
async def get_request_count():
    global request_general
    return {"count": request_general}


@app.get("/cpu_usage")
async def get_cpu_usage():
    """
    Эндпоинт, который возвращает текущую загрузку процессора вместе с текущим временем.
    Одновременно записывает данные в новый файл в папку logs_cpu/.
    """
    # Получаем загрузку процессора в процентах
    cpu_usage = psutil.cpu_percent(interval=1)

    current_time = str(datetime.now().strftime('%H:%M:%S'))

    current_time.replace('T',' ')
    # Создаем запись для файла в виде строки
    log_entry = f"{cpu_usage}, {current_time}\n"

    # Указываем путь к папке logs_cpu
    logs_folder = "/Users/aydyn/Desktop/DIPLOM_JOKES_END/backend/FastAPI/logs_cpu/cpu_data.txt"

    # Открываем новый файл для записи и записываем log_entry
    with open(logs_folder, "a") as file:
        file.write(log_entry)

    # Возвращаем данные в формате JSON
    return {
        "cpu_usage": cpu_usage,
        "timestamp": current_time
    }
@app.post("/cpu_anomalies")
async def receive_anomalies(request: Request):
    data = await request.json()

    anomalies.extend(data)

    return JSONResponse({"message": "Anomalies received successfully."})
@app.get("/cpu_anomalies")
async def get_anomalies():
    # Возвращаем текущие аномалии в JSON-формате
    return JSONResponse(content=anomalies)

# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)