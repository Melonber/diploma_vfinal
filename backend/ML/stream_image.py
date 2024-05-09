import websockets
import asyncio
import base64


async def stream_images(websocket, path):
    while True:
        # Считывание изображения из файла или получения его каким-то другим способом
        with open('graphics_anomaly/anomalies_plot.png', 'rb') as img_file:
            # Кодируем изображение в base64, чтобы передать его через WebSocket
            encoded_img = base64.b64encode(img_file.read()).decode('utf-8')

        # Отправляем изображение клиенту
        await websocket.send(encoded_img)

        # Подождем 1 секунду перед следующим отправлением
        await asyncio.sleep(1)


# Запускаем сервер WebSocket
start_server = websockets.serve(stream_images, 'localhost', 8765)

# Запуск сервера
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
