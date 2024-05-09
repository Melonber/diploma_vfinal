import time
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DateFormatter
import datetime  # Импортируем модуль datetime для обработки дат


def read_logs(file_path):
    data = []
    timestamps = []

    # Чтение данных из файла
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Пропустить первую строку, если это заголовок
    if lines[0].strip() == 'count, timestamp':
        lines = lines[1:]

    # Обработка строк
    for line in lines:
        line = line.strip()
        if ',' in line:
            count, timestamp = line.split(',')
            try:
                count = int(count)
                data.append(count)
                timestamps.append(timestamp.strip())
            except ValueError:
                print(f"Невозможно преобразовать count в целое число: '{count}'")
        else:
            print(f"Строка не содержит запятой: '{line}'")

    return np.array(data).reshape(-1, 1), timestamps


def save_plot(fig, file_path):
    """Сохраняет текущий график в файл."""
    time.sleep(1)
    fig.savefig(file_path)
    print(f"График сохранен в файл: {file_path}")


def update(frame, file_path, ax, model, fig):
    # Считывание данных из файла
    data, timestamps = read_logs(file_path)

    # Преобразуем временные метки в объекты datetime
    timestamps = [datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps]

    # Обучение модели на новых данных
    model.fit(data)

    # Предсказание аномалий
    predictions = model.predict(data)

    # Очистка графика перед обновлением
    ax.clear()

    # Установка черного фона и белой границы оси
    ax.set_facecolor('black')  # Задний фон оси черный
    ax.spines['top'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')

    # Установка цветов меток по оси y и оси x
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white')

    # Визуализация данных
    ax.plot(timestamps, data, label='Количество запросов', color='white')  # Установить цвет данных в белый

    # Флаг для проверки наличия аномалий
    anomalies_found = False

    # Вывод аномалий и аннотаций
    for i in range(len(predictions)):
        if predictions[i] == -1:
            anomalies_found = True
            ax.scatter(timestamps[i], data[i], color='red', label='Аномалии' if i == 0 else "")
            ax.annotate(
                timestamps[i].strftime('%d-%m-%Y %H:%M:%S'),
                (timestamps[i], data[i]),
                textcoords='offset points',
                xytext=(0, 5),
                ha='center',
                fontsize=8,
                color='red'
            )

    # Устанавливаем формат времени в оси x
    date_formatter = DateFormatter('%d-%m-%Y %H:%M')
    ax.xaxis.set_major_formatter(date_formatter)

    # Убираем метки по оси x
    ax.get_xaxis().set_ticks([])

    # Обновление легенды и заголовка
    ax.legend()
    ax.set_title('Количество запросов с аномалиями', color='white')
    ax.set_xlabel('Временная метка', color='white')
    ax.set_ylabel('Количество запросов', color='white')

    # Если найдена хотя бы одна аномалия, сохранить график в файл
    if anomalies_found:
        save_plot(fig, 'graphics_anomaly/anomalies_plot.png')


def main():
    file_path = '../FastAPI/logs_req_per_sec/logs.txt'  # Укажите путь к вашему файлу данных

    # Создание и настройка модели Isolation Forest
    model = IsolationForest(contamination=0.01, random_state=42)

    # Инициализация фигуры и оси
    fig, ax = plt.subplots(figsize=(10, 6))

    # Установка черного фона фигуры
    fig.patch.set_facecolor('black')

    # Используем FuncAnimation для обновления графика в реальном времени
    ani = animation.FuncAnimation(
        fig, update, fargs=(file_path, ax, model, fig), interval=1000
    )

    # Запуск анимации
    plt.show()


if __name__ == "__main__":
    main()
