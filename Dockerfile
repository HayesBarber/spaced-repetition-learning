FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN pip install .

EXPOSE 8080

CMD ["srl", "server", "--host", "0.0.0.0", "--port", "8080"]
