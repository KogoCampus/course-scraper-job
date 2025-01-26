FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app

RUN pip install --no-cache-dir setuptools

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown pwuser:pwuser .env && \
    chmod 600 .env

# Ensure all files are owned by pwuser
RUN chown -R pwuser:pwuser /app

# Switch to pwuser (pre-configured in the Playwright image)
USER pwuser

ENTRYPOINT ["/entrypoint.sh"]