FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -e .

EXPOSE 7890

CMD ["python", "-m", "clawnet.server", "--host", "0.0.0.0", "--port", "7890", "--persist", "/data"]
