# Use Python 3.12 slim variant
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file to working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Set environment variable to ensure stdout and stderr are unbuffered
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python", "src/bot.py"]
