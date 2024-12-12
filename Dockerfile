FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user and group with specific UID/GID
RUN groupadd -r scraper && \
    useradd -r -g scraper -u 1000 scraper

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install Playwright browser
RUN playwright install chromium && \
    playwright install-deps

# Make entrypoint executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure environment file is present and readable
RUN chown scraper:scraper .env && \
    chmod 600 .env

# Ensure all files are owned by scraper user
RUN chown -R scraper:scraper /app

# Switch to scraper user
USER scraper

ENTRYPOINT ["/entrypoint.sh"] 