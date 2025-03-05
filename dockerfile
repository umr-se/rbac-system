FROM python:3.13.1-slim

RUN apt-get update && \
    apt-get install -y gcc python3-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir bcrypt==4.0.1

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]