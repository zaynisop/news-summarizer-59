FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive

# Google Chrome (stable) + matching ChromeDriver from Chrome for Testing
RUN apt-get update && apt-get install -y --no-install-recommends wget curl unzip gnupg ca-certificates jq \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+') \
    && DRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json \
        | jq -r --arg v "$CHROME_VERSION" '.versions[] | select(.version==$v) | .downloads.chromedriver[] | select(.platform=="linux64") | .url') \
    && if [ -z "$DRIVER_URL" ]; then \
         DRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
           | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url'); fi \
    && wget -q -O /tmp/driver.zip "$DRIVER_URL" \
    && unzip -q /tmp/driver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/* /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 7000
# API starts automatically when the container runs
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "--workers", "2", "--timeout", "180", "app:app"]
