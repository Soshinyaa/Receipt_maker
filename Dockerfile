FROM python:3.12-slim

# Копируем код приложения в контейнер
COPY . /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
RUN pip install -r docs/requirements.txt

# Запускаем приложение
CMD ["python", "src/main.py"]
