FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python -c "from database import DatabaseManager; DatabaseManager().initialize_database()"

EXPOSE 5000

CMD ["python", "app.py"]
