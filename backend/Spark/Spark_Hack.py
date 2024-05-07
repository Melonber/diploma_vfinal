import joblib
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, udf
import requests

# Загрузка обученной модели и векторизатора
model = joblib.load('../ML/trained_model.joblib')
vectorizer = joblib.load('../ML/vectorizer.joblib')

# Создание SparkSession
spark = SparkSession.builder \
    .appName("LogAnalysis") \
    .getOrCreate()

# Чтение новых строк из файла logs с использованием Structured Streaming
logs_df = spark \
    .readStream \
    .format("text") \
    .option("path", "../FastAPI/logs/") \
    .option("maxFilesPerTrigger", 1) \
    .load()

# Преобразование данных
# Разделение log_entry на столбцы: IP, Date, Method, Path, Phone, Message, Status
logs_df = logs_df.withColumn("log_entry", split(col("value"), ", "))

# Извлечение Message из log_entry
logs_df = logs_df.withColumn("Message", logs_df.log_entry.getItem(5).cast("string"))
logs_df = logs_df.withColumn("Message", split(col("Message"), ": ").getItem(1))

# Функция для отправки подозрительного лога в FastAPI
def send_suspicious_log(log_entry):
    try:
        count = 0
        # Отправляем POST-запрос в FastAPI с подозрительным логом
        response = requests.post("http://localhost:9000/add_suspicious_log", json={"log_entry": log_entry})
        count+=1
        print("Отпрвлено",count)
        if not response.ok:
            print(f"Не удалось отправить подозрительный лог: {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке подозрительного лога: {e}")

# Функция для предсказания и отправки подозрительных логов
def predict_message(batch_df, batch_id):
    # Извлекаем сообщения из DataFrame
    messages = batch_df.select("Message").rdd.map(lambda row: row["Message"]).collect()

    # Отфильтруем None значения
    messages = [msg for msg in messages if msg is not None]

    # Преобразуем сообщения в векторизованные данные
    messages_transformed = vectorizer.transform(messages)

    # Предсказание модели
    predictions = model.predict(messages_transformed)

    # Проверяем каждое сообщение и предсказание
    for message, prediction in zip(messages, predictions):
        if prediction:  # Подозрительное сообщение
            log_entry = batch_df.filter(batch_df.Message == message).select("value").first()[0]
            # Отправляем подозрительный лог в FastAPI
            send_suspicious_log(log_entry)

# Применение функции предсказания на каждом батче данных
logs_df.writeStream \
    .foreachBatch(predict_message) \
    .trigger(processingTime='10 seconds') \
    .start() \
    .awaitTermination()
