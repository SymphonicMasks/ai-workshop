FROM python:3.12-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install curl

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN chmod +x entrypoint.sh

CMD python -m uvicorn api:app --host 0.0.0.0 --port 8081