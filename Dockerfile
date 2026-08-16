FROM python:3.12-slim

WORKDIR /app

# Запрещаем создание .pyc файлов и включаем мгновенный вывод логов в консоль
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Сначала копируем зависимости для эффективного кеширования слоев Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]