import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# Устанавливаем случайный сид для воспроизводимости
np.random.seed(42)

# Загрузка данных о загрузке CPU из файла
data_path = 'путь_к_файлу_с_данными.csv'  # Замените 'путь_к_файлу_с_данными.csv' на путь к вашему файлу с данными
data = pd.read_csv(data_path)

# Убедитесь, что данные содержат столбцы 'timestamp' и 'cpu_usage'
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.set_index('timestamp', inplace=True)

# Визуализируем данные
data.plot()
plt.show()

# Масштабируем данные с помощью MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
data_scaled = scaler.fit_transform(data['cpu_usage'].values.reshape(-1, 1))

# Создаем последовательности данных для обучения LSTM
sequence_length = 50  # Длина последовательности для обучения LSTM
X, y = [], []
for i in range(sequence_length, len(data_scaled)):
    X.append(data_scaled[i - sequence_length:i, 0])
    y.append(data_scaled[i, 0])

X = np.array(X)
y = np.array(y)

# Преобразуем данные в формат, подходящий для LSTM (samples, timesteps, features)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Создание модели LSTM
model = Sequential([
    LSTM(64, input_shape=(sequence_length, 1), return_sequences=True),
    LSTM(64),
    Dense(1)
])

# Компиляция модели
model.compile(optimizer='adam', loss='mean_squared_error')

# Обучение модели
history = model.fit(X, y, epochs=50, batch_size=32, validation_split=0.1, verbose=1)

# Визуализируем потери во время обучения
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='val')
plt.legend()
plt.show()

# Прогнозирование значений загрузки CPU
predicted = model.predict(X)

# Сравнение предсказанных значений с фактическими
predicted = scaler.inverse_transform(predicted)
actual = scaler.inverse_transform(y.reshape(-1, 1))

# Вычисляем ошибку прогноза
error = actual - predicted

# Визуализируем фактические и предсказанные значения, а также ошибку
plt.figure(figsize=(10, 6))
plt.plot(actual, label='Actual')
plt.plot(predicted, label='Predicted')
plt.plot(error, label='Error')
plt.legend()
plt.show()

# Определение аномалий на основе ошибки прогноза
threshold = 0.1  # Установите порог для определения аномалий
anomalies = np.where(np.abs(error) > threshold)[0]

# Визуализируем аномалии
plt.figure(figsize=(10, 6))
plt.plot(actual, label='Actual')
plt.scatter(anomalies, actual[anomalies], color='red', label='Anomalies')
plt.legend()
plt.show()
