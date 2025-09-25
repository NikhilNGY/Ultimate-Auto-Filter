# Use official slim Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /bot

# Copy all bot files
COPY . .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Koyeb health checks
EXPOSE 8080

# Start the bot
CMD ["python", "bot/main.py"]
