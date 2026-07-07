# API container. Note: printing to the RP850 needs the physical printer + the
# Windows driver, so containers run with PRINT_MODE=console by default. Use this
# to host the board/data layer; run the API natively on the PC to print for real.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY app ./app

ENV PRINT_MODE=console \
    DATABASE_URL=sqlite:////data/tasks.db
VOLUME ["/data"]
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
