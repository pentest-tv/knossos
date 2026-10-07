# Local scoreboard web app for the Pentest.TV lab. Flask + SQLite, single container.
# Base image pinned by digest via the PYTHON_IMAGE build arg.
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py course.json ./
COPY templates/ ./templates/
COPY static/ ./static/

EXPOSE 8888
CMD ["python", "app.py"]
