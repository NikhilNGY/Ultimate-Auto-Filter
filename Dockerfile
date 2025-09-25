# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /bot

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for health checks
EXPOSE 8080

# Run the bot
CMD ["python", "bot/main.py"]
