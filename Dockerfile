FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer le répertoire pour la base de données
RUN mkdir -p /app/data

CMD ["python", "bot.py"] 


