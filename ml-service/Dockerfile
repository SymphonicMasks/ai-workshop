FROM python:3.9-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install curl
RUN apt-get install -y --no-install-recommends  \
    ffmpeg \
    lilypond

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN chmod +x start.sh

CMD python -m uvicorn api:app --host 0.0.0.0 --port 8080