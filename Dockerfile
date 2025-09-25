# Use slim Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /bot

# Copy all bot files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure session folder exists
RUN mkdir -p session

# Set default command to run bot
CMD ["python", "bot/main.py"]
