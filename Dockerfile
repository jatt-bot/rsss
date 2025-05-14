# Use Python slim base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run your bot
CMD ["python", "bot.py"]
