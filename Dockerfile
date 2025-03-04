FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "bot.py"] 

ENV DISCORD_TOKEN=MTM0NjIwMTYwNzMxNDA4MzkyMA.Gl-KrA.k_6pYNTyGuhPYYTyHR-By48xzz4ipsH0fjwW80