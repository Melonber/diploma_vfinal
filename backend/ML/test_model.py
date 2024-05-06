import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# Загрузка обученной модели и векторизатора
model = joblib.load('trained_model.joblib')
vectorizer = joblib.load('vectorizer.joblib')

# Ваше сообщение, которое вы хотите протестировать
your_message = "Как какать ?"

# Преобразование сообщения в формат, подходящий для модели
your_message_transformed = vectorizer.transform([your_message])

# Предсказание метки для вашего сообщения
prediction = model.predict(your_message_transformed)

# Вывод предсказания
print(f"Предсказанная метка: {prediction[0]}")

# Вы также можете использовать модель для предсказания вероятностей класса, если нужно
prediction_proba = model.predict_proba(your_message_transformed)
print(f"Вероятность классов: {prediction_proba[0]}")
