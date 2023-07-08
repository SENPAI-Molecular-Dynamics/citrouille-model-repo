FROM python:3.11

WORKDIR /app

COPY app.py .
COPY config.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
