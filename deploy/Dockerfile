FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////data/fintrack.db

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/run.py ./run.py

RUN addgroup --system --gid 10001 fintrack \
    && adduser --system --uid 10001 --ingroup fintrack fintrack \
    && mkdir -p /data \
    && chown -R fintrack:fintrack /app /data

USER fintrack
EXPOSE 8000

CMD ["sh", "-c", "flask --app run db upgrade && waitress-serve --listen=0.0.0.0:8000 --threads=4 run:app"]