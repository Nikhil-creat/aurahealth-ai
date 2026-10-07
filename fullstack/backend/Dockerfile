FROM python:3.12-slim AS builder
WORKDIR /w
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt -w /wheels
FROM python:3.12-slim AS runtime
RUN useradd -m aura
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY app ./app
USER aura
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
