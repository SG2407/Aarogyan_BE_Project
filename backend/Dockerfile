# Use official Python image with 3.11
FROM python:3.11-slim

# Set work directory
WORKDIR /app


# Install system dependencies for Tesseract OCR
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	tesseract-ocr \
	libtesseract-dev \
	libleptonica-dev \
	poppler-utils \
	unpaper \
	ghostscript \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code, but do NOT copy .env (let Render inject env vars)
COPY . .
RUN rm -f .env

# Expose port (match your uvicorn port)
EXPOSE 10000

# Start FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
