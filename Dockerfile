FROM python:3.10-slim

# Set working directory di dalam kontainer
WORKDIR /app

# Install dependencies sistem yang mungkin dibutuhkan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements dulu agar Docker bisa cache layer ini
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi
COPY . .

# Jalankan aplikasi menggunakan uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]