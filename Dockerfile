FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bourse_tracker/ bourse_tracker/

# Le rapport est écrit dans /app/output : monter un volume pour le récupérer
ENTRYPOINT ["python", "-m", "bourse_tracker"]
