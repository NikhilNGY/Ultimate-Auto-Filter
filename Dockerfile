FROM python:3.11-slim

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Create session folder to persist .session file
RUN mkdir -p /bot/session

CMD ["python", "bot/main.py"]
