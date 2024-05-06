import joblib
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, udf
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

# Функция для предсказания
def predict_message(batch_df, batch_id):
    # Извлекаем сообщения из DataFrame
    messages = batch_df.select("Message").rdd.map(lambda row: row["Message"]).collect()

    # Отфильтруем None значения
    messages = [msg for msg in messages if msg is not None]

    # Преобразуем сообщения в векторизованные данные
    messages_transformed = vectorizer.transform(messages)

    # Предсказание модели
    predictions = model.predict(messages_transformed)

    # Вывод результата
    for message, prediction in zip(messages, predictions):
        print(f"Сообщение: {message} | Подозрительное: {prediction}")

# Применение функции предсказания на каждом батче данных

logs_df.writeStream \
    .foreachBatch(predict_message) \
    .trigger(processingTime='10 seconds') \
    .start() \
    .awaitTermination()