FROM python:3.10-slim

WORKDIR /app
COPY Application-code/ .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
