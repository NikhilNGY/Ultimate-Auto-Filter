FROM python:3.11-slim

WORKDIR /bot
COPY . .

# Create session dir with full permissions for sqlite
RUN mkdir -p /bot/session && chmod 777 /bot/session

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
