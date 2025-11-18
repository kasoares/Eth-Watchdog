# Lightweight base image optimized for production
FROM python:3.10-slim

# Project metadata
LABEL maintainer="Kaiky Soares"
LABEL description="Eth-Watchdog - Ethereum Node Health Monitor"

# Set working directory
WORKDIR /app

# Copy dependencies file first (leverage Docker cache)
COPY requirements.txt .

# Install dependencies without cache to reduce image size
# --no-cache-dir: prevents storage of pip temporary files
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security (production container best practice)
# Avoids running as root, reducing attack surface
RUN useradd -m -u 1000 watchdog && \
    chown -R watchdog:watchdog /app

# Switch to non-privileged user
USER watchdog

# Healthcheck for container monitoring
# Verifies if Python process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python app.py" || exit 1

# Application entry command
CMD ["python", "app.py"]
