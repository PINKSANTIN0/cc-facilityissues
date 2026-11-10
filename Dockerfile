# ===============================================
# Dockerfile - Backend Python REST API
# Facility Issue Reporting System
# Telkom University - Cloud Computing UTS
# ===============================================

FROM python:3.11-slim

LABEL maintainer="Telkom University - Cloud Computing"
LABEL description="Backend API for Facility Issue Reporting System"

# Set working directory
WORKDIR /app

# Copy application file
COPY app.py .

# Create data directory
RUN mkdir -p /var/lib/backend_data

# Expose API port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "app.py"]
