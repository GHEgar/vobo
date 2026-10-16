FROM python:3.14-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN mkdir -p /data /evidencias /contenido-media
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
RUN groupadd --system --gid 10001 validacion \
    && useradd --system --uid 10001 --gid validacion --home-dir /app --shell /usr/sbin/nologin validacion
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
RUN mkdir -p /data /evidencias /contenido-media \
    && chown validacion:validacion /data /evidencias /contenido-media
ARG APP_VERSION=""
ENV APP_VERSION=$APP_VERSION
USER validacion
CMD ["sh", "-c", "python -m app.inicializar && exec gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --access-logfile - --error-logfile -"]
