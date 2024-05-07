from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Добавление middleware для поддержки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники для простоты
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для подозрительного лога
class SuspiciousLog(BaseModel):
    log_entry: str

# Список для хранения подозрительных логов
suspicious_logs = []

# POST-роут для добавления подозрительных логов
@app.post("/add_suspicious_log")
def add_suspicious_log(log: SuspiciousLog):
    # Добавление подозрительного лога в список
    suspicious_logs.append(log.log_entry)
    return {"message": "Log entry added successfully"}

# GET-роут для получения всех подозрительных логов
@app.get("/get_suspicious_logs")
def get_suspicious_logs():
    # Возвращаем список всех подозрительных логов
    return suspicious_logs

# Запуск приложения FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
