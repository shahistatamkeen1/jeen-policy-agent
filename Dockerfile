FROM python:3.12-slim
WORKDIR /app
COPY service /app/service
COPY documents /app/documents
ENV PYTHONUNBUFFERED=1 BIND_HOST=0.0.0.0 DB_PATH=/app/data/cases.db
CMD ["python", "-m", "service.agent"]
COPY workflows /app/workflows
COPY tests /app/tests
COPY docs /app/docs
RUN mkdir -p /app/evidence
