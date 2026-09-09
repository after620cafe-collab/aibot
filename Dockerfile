FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.deno/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

# JS runtime required by modern yt-dlp YouTube extraction.
RUN curl -fsSL https://deno.land/install.sh | sh

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
